import numpy as np
import polars as pl
import pytest

from kingsrace.models.event_study import base_transicoes, por_transicao, salto

TRANS = [(2010, 2014), (2014, 2018)]


def _dados(efeito_alvo=-0.3, n=600, seed=0):
    """AMCs sintéticas em 60 regiões; x só afeta a variação de 2014→2018."""
    rng = np.random.default_rng(seed)
    amc = np.arange(n)
    x = rng.normal(size=n)
    logit = {2010: rng.normal(size=n)}
    logit[2014] = logit[2010] + rng.normal(0, 0.1, n)
    logit[2018] = logit[2014] + efeito_alvo * x + rng.normal(0, 0.1, n)
    painel = pl.concat(
        pl.DataFrame(
            {
                "amc_id": amc,
                "ano": ano,
                "turno": 1,
                "pt_2p_logit": logit[ano],
                "aptos": rng.integers(1_000, 100_000, n),
            }
        )
        for ano in (2010, 2014, 2018)
    )
    geo = pl.DataFrame({"amc_id": amc, "cd_regiao_imediata": amc % 60})
    cov = pl.DataFrame(
        {
            "amc_id": amc,
            "renda_pc_mediana": rng.uniform(300, 3000, n),
            **{
                c: rng.normal(size=n)
                for c in ("taxa_alfabetizacao", "pct_urbana", "idade_mediana", "pct_preta_parda")
            },
        }
    )
    return painel, geo, cov, pl.DataFrame({"amc_id": amc, "x": 10 + 5 * x})


def test_recupera_efeito_so_na_transicao_certa():
    base = base_transicoes(*_dados(), transicoes=TRANS)
    res = por_transicao(base).sort("transicao")

    antes, alvo = res.rows(named=True)
    assert antes["ic_inf"] < 0 < antes["ic_sup"]
    assert alvo["coef"] == pytest.approx(-0.3, abs=0.03)  # x é padronizada (dp 1)
    assert alvo["ic_sup"] < 0


def test_salto_reproduz_os_coeficientes_separados():
    base = base_transicoes(*_dados(), transicoes=TRANS)
    separados = dict(por_transicao(base).select("transicao", "coef").iter_rows())

    s = salto(base)

    assert s["beta_alvo"] == pytest.approx(separados["2014→2018"], rel=1e-8)
    assert s["beta_anterior"] == pytest.approx(separados["2010→2014"], rel=1e-8)
    assert s["diferenca"] == pytest.approx(s["beta_alvo"] - s["beta_anterior"])
    assert s["ic_sup"] < 0


def test_sem_efeito_o_salto_contem_zero():
    base = base_transicoes(*_dados(efeito_alvo=0.0, seed=1), transicoes=TRANS)

    s = salto(base)

    assert s["ic_inf"] < 0 < s["ic_sup"]


def test_exposicao_variavel_no_tempo_e_padronizada_por_transicao():
    painel, geo, cov, exp = _dados()
    por_ano = pl.concat(
        [exp.with_columns(de=pl.lit(2010)), exp.with_columns(de=pl.lit(2014), x=pl.col("x") * 3)]
    )

    base = base_transicoes(painel, geo, cov, por_ano, transicoes=TRANS)

    resumo = base.group_by("transicao").agg(
        media=pl.col("x").mean(), dp=pl.col("x").std(), n=pl.len()
    )
    assert resumo["media"].to_list() == pytest.approx([0, 0], abs=1e-9)
    assert resumo["dp"].to_list() == pytest.approx([1, 1])
    assert resumo["n"].to_list() == [600, 600]
