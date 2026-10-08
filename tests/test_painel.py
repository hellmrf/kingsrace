import math

import polars as pl
import pytest

from kingsrace.features.painel import (
    adiciona_metricas,
    agrega_amc,
    classifica_votos,
    monta_painel,
)

CANDIDATOS = pl.DataFrame(
    {
        "ano": [2026, 2026, 2026],
        "nr_votavel": [13, 22, 28],
        "papel": ["pt", "adversario", "anulado"],
    }
)


def test_classifica_votos_por_papel_com_branco_nulo_e_outro_por_padrao():
    votos = pl.DataFrame({"ano": [2026] * 6, "nr_votavel": [13, 22, 28, 95, 96, 70]})

    res = classifica_votos(votos, CANDIDATOS)

    assert dict(res.select("nr_votavel", "papel").iter_rows()) == {
        13: "pt",
        22: "adversario",
        28: "anulado",
        95: "branco",
        96: "nulo",
        70: "outro",
    }


def test_classificacao_depende_do_ano():
    votos = pl.DataFrame({"ano": [2022], "nr_votavel": [28]})

    assert classifica_votos(votos, CANDIDATOS)["papel"].to_list() == ["outro"]


def test_metricas_de_participacao():
    df = pl.DataFrame(
        {
            "votos_pt": [60],
            "votos_adv": [40],
            "validos": [120],
            "aptos": [200],
            "abstencoes": [50],
        }
    )

    r = adiciona_metricas(df).row(0, named=True)

    assert r["pt_validos"] == pytest.approx(0.5)
    assert r["adv_validos"] == pytest.approx(1 / 3)
    assert r["pt_2p"] == pytest.approx(0.6)
    assert r["pt_2p_logit"] == pytest.approx(math.log(0.6 / 0.4))
    assert r["pt_aptos"] == pytest.approx(0.3)
    assert r["abstencao"] == pytest.approx(0.25)


def _municipios():
    return pl.DataFrame(
        {"cd_tse": [100, 200], "cd_ibge": [1000001, 2000002], "amc_id": [9000001, 9000001]}
    )


def _secao():
    # município 100: duas zonas; 200: uma zona; exterior (ZZ) separado
    linhas = [
        ("SP", 100, 1, 13, 30),
        ("SP", 100, 1, 22, 10),
        ("SP", 100, 2, 13, 20),
        ("SP", 100, 2, 70, 5),
        ("SP", 100, 2, 28, 3),
        ("SP", 100, 2, 95, 2),
        ("SP", 200, 9, 22, 7),
        ("ZZ", 999, 1, 13, 4),
    ]
    return pl.DataFrame(
        linhas, schema=["uf", "cd_tse", "nr_zona", "nr_votavel", "votos"], orient="row"
    ).with_columns(ano=pl.lit(2026), turno=pl.lit(1))


def _detalhe():
    linhas = [
        ("SP", 100, 1, 50, 40, 10, 40, 0, 0),
        ("SP", 100, 2, 50, 30, 20, 25, 2, 3),
        ("SP", 200, 9, 10, 7, 3, 7, 0, 0),
        ("ZZ", 999, 1, 8, 4, 4, 4, 0, 0),
    ]
    cols = ["uf", "cd_tse", "nr_zona", "aptos", "comparecimento", "abstencoes", "validos"]
    cols += ["brancos", "nulos"]
    return pl.DataFrame(linhas, schema=cols, orient="row").with_columns(
        ano=pl.lit(2026), turno=pl.lit(1)
    )


def test_monta_painel_soma_zonas_separa_papeis_e_exclui_exterior():
    votos = classifica_votos(_secao(), CANDIDATOS)

    painel = monta_painel(votos, _detalhe(), _municipios())

    cols = ["cd_ibge", "aptos", "validos", "votos_pt", "votos_adv", "votos_outros", "nulos"]
    assert painel.sort("cd_ibge").select(cols).rows() == [
        (1000001, 100, 65, 50, 10, 5, 3),
        (2000002, 10, 7, 0, 7, 0, 0),
    ]


def test_monta_painel_falha_se_votos_por_candidato_nao_fecham_com_validos():
    votos = classifica_votos(_secao(), CANDIDATOS.filter(pl.col("nr_votavel") != 28))

    with pytest.raises(ValueError, match="1000001"):
        monta_painel(votos, _detalhe(), _municipios())


def test_agrega_amc_soma_votos_antes_de_calcular_proporcoes():
    painel = pl.DataFrame(
        {
            "cd_ibge": [1000001, 2000002],
            "ano": [2026, 2026],
            "turno": [1, 1],
            "uf": ["SP", "SP"],
            "aptos": [1200, 150],
            "comparecimento": [1000, 100],
            "abstencoes": [200, 50],
            "validos": [1000, 100],
            "brancos": [0, 0],
            "nulos": [0, 0],
            "votos_pt": [900, 10],
            "votos_adv": [100, 90],
            "votos_outros": [0, 0],
        }
    )

    res = agrega_amc(painel, _municipios())

    r = res.row(0, named=True)
    assert res.height == 1
    assert (r["amc_id"], r["votos_pt"], r["validos"]) == (9000001, 910, 1100)
    assert r["pt_2p"] == pytest.approx(910 / 1100)
