import math

import polars as pl
import pytest

from kingsrace.features.base import base_variacao


def _painel():
    linhas = [
        # amc, ano, turno, uf, aptos, pt_2p
        (1, 2022, 1, "SP", 1000, 0.60),
        (1, 2026, 1, "SP", 1100, 0.50),
        (2, 2022, 1, "BA", 50000, 0.80),
        (2, 2026, 1, "BA", 52000, 0.75),
        (2, 2022, 2, "BA", 50000, 0.82),  # outro turno: não entra
    ]
    df = pl.DataFrame(
        linhas, schema=["amc_id", "ano", "turno", "uf", "aptos", "pt_2p"], orient="row"
    )
    return df.with_columns(pt_2p_logit=(pl.col("pt_2p") / (1 - pl.col("pt_2p"))).log())


def _municipios():
    return pl.DataFrame(
        {
            "cd_ibge": [11, 12, 21],
            "amc_id": [1, 1, 2],
            "nome": ["B", "A", "C"],
            "uf": ["SP", "SP", "BA"],
            "regiao": ["SE", "SE", "NE"],
            "cd_regiao_imediata": [350001, 350001, 290001],
            "regiao_imediata": ["R1", "R1", "R2"],
        }
    )


def _cov():
    return pl.DataFrame({"amc_id": [1, 2], "pct_evangelica": [30.0, 20.0]})


def test_base_variacao_calcula_deltas_tamanho_e_traz_geografia_e_covariaveis():
    res = base_variacao(_painel(), _cov(), _municipios(), de=(2022, 1), para=(2026, 1))
    r = res.sort("amc_id").row(0, named=True)

    assert res.height == 2
    assert r["delta_pp"] == pytest.approx(-10.0)
    assert r["delta_logit"] == pytest.approx(math.log(0.5 / 0.5) - math.log(0.6 / 0.4))
    assert r["pt_2p_logit_de"] == pytest.approx(math.log(0.6 / 0.4))
    assert r["log_aptos_de"] == pytest.approx(math.log(1000))
    assert (r["nome"], r["regiao"], r["cd_regiao_imediata"]) == ("A + B", "SE", 350001)
    assert r["pct_evangelica"] == 30.0


def test_amc_que_atravessa_regioes_imediatas_fica_com_a_mais_frequente():
    # ex.: Paraíso das Águas + Chapadão do Sul (mesma região) + Água Clara + Costa Rica
    municipios = pl.DataFrame(
        {
            "cd_ibge": [11, 12, 13, 14],
            "amc_id": [1, 1, 1, 1],
            "nome": ["A", "B", "C", "D"],
            "uf": ["MS"] * 4,
            "regiao": ["CO"] * 4,
            "cd_regiao_imediata": [500002, 500003, 500004, 500003],
            "regiao_imediata": ["Três Lagoas", "Chapadão", "Coxim", "Chapadão"],
        }
    )
    painel = _painel().filter(pl.col("amc_id") == 1)

    res = base_variacao(painel, _cov(), municipios, de=(2022, 1), para=(2026, 1))

    assert res.select("cd_regiao_imediata", "regiao_imediata").row(0) == (500003, "Chapadão")
