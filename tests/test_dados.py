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


def test_soja_nunca_ocupa_mais_que_o_territorio(covariaveis):
    for ano in ("2021", "2025"):
        excesso = covariaveis.filter(pl.col(f"area_soja_{ano}_ha") > 100 * pl.col("area_km2"))

        assert excesso.is_empty(), excesso.select("cd_ibge", f"area_soja_{ano}_ha", "area_km2")


def test_residuos_de_turnout_nao_sao_negativos(painel):
    assert painel.filter(
        (pl.col("nulos") < 0) | (pl.col("eleitores_nao_instalados") < 0)
    ).is_empty()


def test_religiosos_uma_linha_por_amc_e_eleicao():
    rel = pl.read_parquet(paths.PROCESSED / "religiosos_amc.parquet")
    amcs = pl.read_parquet(paths.PROCESSED / "painel_amc.parquet")["amc_id"].n_unique()

    assert rel.group_by("ano").len()["len"].to_list() == [amcs] * 5
    assert rel.null_count().sum_horizontal().item() == 0
    assert rel["pct_religiosos"].is_between(0, 100).all()
    assert (rel["votos_religiosos"] <= rel["nominais_validos"]).all()
    assert (rel["nominais_validos"] <= rel["validos_deputado"]).all()


def test_votos_nominais_de_deputado_batem_com_o_detalhe_por_uf():
    from kingsrace.features.religiao import le_votos_deputado

    interim = paths.INTERIM / "tse"
    cand = (
        le_votos_deputado(interim)
        .group_by("ano_eleicao", "sg_uf")
        .agg(pl.col("votos_validos").sum())
    )
    det = (
        pl.read_parquet(interim / "detalhe_deputado" / "**" / "*.parquet", hive_partitioning=False)
        .filter(pl.col("nr_turno") == 1)
        .group_by("ano_eleicao", "sg_uf")
        .agg(pl.col("qt_votos_nominais_validos").sum())
    )
    res = cand.join(det, on=["ano_eleicao", "sg_uf"], how="full")

    assert res.height == 27 * 5
    assert res.filter(pl.col("votos_validos") != pl.col("qt_votos_nominais_validos")).is_empty()


def test_homicidios_quase_todos_atribuidos_a_uma_amc():
    """O SIM deixa 1–3% em "município ignorado"; perder mais denuncia código mal lido."""
    sim = paths.INTERIM / "sim" / "homicidios.parquet"
    if not sim.exists():
        pytest.skip("intermediário do SIM ausente")
    total = pl.read_parquet(sim).group_by("ano").agg(sim=pl.col("homicidios").sum())
    amc = (
        pl.read_parquet(paths.PROCESSED / "homicidios_amc.parquet")
        .group_by("ano")
        .agg(amc=pl.col("homicidios").sum())
    )
    fracao = total.join(amc, on="ano", how="left").with_columns(
        f=pl.col("amc").fill_null(0) / pl.col("sim")
    )
    assert fracao.filter(pl.col("f") < 0.96).height == 0, fracao.sort("ano")


@pytest.mark.skipif(
    not (paths.PROCESSED / "painel_secao.parquet").exists(), reason="painel por seção ausente"
)
def test_painel_secao_e_local_somam_o_painel_amc():
    contagens = ["aptos", "comparecimento", "validos", "votos_pt", "votos_adv", "votos_outros"]
    amc = pl.read_parquet(paths.PROCESSED / "painel_amc.parquet").filter(
        pl.col("ano").is_in([2022, 2026])
    )
    esperado = (
        amc.group_by("ano", "turno", "uf").agg(pl.col(contagens).sum()).sort("ano", "turno", "uf")
    )
    for arquivo in ("painel_secao", "painel_local"):
        painel = pl.read_parquet(paths.PROCESSED / f"{arquivo}.parquet")
        obtido = (
            painel.group_by("ano", "turno", "uf")
            .agg(pl.col(contagens).sum())
            .sort("ano", "turno", "uf")
        )
        assert obtido.equals(esperado.select(obtido.columns)), arquivo
