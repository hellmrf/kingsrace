"""Testes sobre os dados processados (rodar `just repro` antes)."""

import polars as pl
import pytest

from kingsrace import paths
from kingsrace.esquemas import Municipios, PainelMunicipio, VotosMunicipio
from kingsrace.harmonize.municipios import le_ibge

pytestmark = [
    pytest.mark.dados,
    pytest.mark.skipif(
        not (paths.PROCESSED / "painel_municipio.parquet").exists(),
        reason="dados processados ausentes; rode `just repro`",
    ),
]


@pytest.fixture(scope="module")
def municipios():
    return pl.read_parquet(paths.PROCESSED / "municipios.parquet")


@pytest.fixture(scope="module")
def painel():
    return pl.read_parquet(paths.PROCESSED / "painel_municipio.parquet")


@pytest.fixture(scope="module")
def votos():
    return pl.read_parquet(paths.PROCESSED / "votos_municipio.parquet")


def test_esquemas(municipios, painel, votos):
    Municipios.validate(municipios)
    PainelMunicipio.validate(painel)
    VotosMunicipio.validate(votos)


def test_totais_nacionais_batem_com_os_oficiais(votos):
    oficiais = pl.read_csv(paths.REFERENCE / "totais_oficiais.csv")
    calculados = votos.group_by("ano", "turno", "nr_votavel").agg(pl.col("votos").sum())

    comparacao = oficiais.join(
        calculados.cast({"ano": pl.Int64, "turno": pl.Int64, "nr_votavel": pl.Int64}),
        on=["ano", "turno", "nr_votavel"],
        how="left",
        suffix="_calc",
    )

    divergentes = comparacao.filter(pl.col("votos") != pl.col("votos_calc").fill_null(-1))
    assert divergentes.is_empty(), divergentes


def test_correspondencia_cobre_todos_os_municipios_do_ibge(municipios):
    ibge = le_ibge(paths.RAW / "ibge" / "municipios.json")

    assert set(municipios["cd_ibge"]) == set(ibge["cd_ibge"])


def test_overrides_apontam_para_municipio_da_mesma_uf():
    overrides = pl.read_csv(paths.REFERENCE / "municipios_overrides.csv")
    ibge = le_ibge(paths.RAW / "ibge" / "municipios.json").select("cd_ibge", "uf")

    res = overrides.join(ibge, on="cd_ibge", how="left", suffix="_ibge")

    assert res.filter(pl.col("uf") != pl.col("uf_ibge").fill_null("")).is_empty()


def test_identidades_contabeis(painel):
    violacoes = painel.filter(
        (
            pl.col("aptos")
            != pl.col("comparecimento") + pl.col("abstencoes") + pl.col("eleitores_nao_instalados")
        )
        | (pl.col("comparecimento") != pl.col("validos") + pl.col("brancos") + pl.col("nulos"))
        | (pl.col("validos") != pl.col("votos_pt") + pl.col("votos_adv") + pl.col("votos_outros"))
    )

    assert violacoes.is_empty(), violacoes


def test_numero_de_amcs_igual_em_todos_os_pleitos():
    amc = pl.read_parquet(paths.PROCESSED / "painel_amc.parquet")

    assert amc.group_by("ano", "turno").len()["len"].n_unique() == 1


@pytest.fixture(scope="module")
def covariaveis():
    return pl.read_parquet(paths.PROCESSED / "covariaveis_municipio.parquet")


def test_covariaveis_sem_colunas_vazias(covariaveis):
    taxa_nulos = covariaveis.null_count() / covariaveis.height
    vazias = [c for c in covariaveis.columns if taxa_nulos[c][0] > 0.01]

    assert vazias == []


def test_so_municipio_instalado_depois_do_censo_fica_sem_populacao(covariaveis):
    sem_pop = covariaveis.filter(pl.col("populacao").is_null())["cd_ibge"].to_list()

    assert sem_pop == [5101837]  # Boa Esperança do Norte (MT), instalado em 2025


def test_percentuais_entre_0_e_100(covariaveis):
    pct = covariaveis.select(pl.col("^pct_.*$"), "taxa_alfabetizacao")
    fora = [c for c in pct.columns if not pct[c].drop_nulls().is_between(0, 100).all()]

    assert fora == []
