import numpy as np
import polars as pl
import pytest

from kingsrace.models.event_study import (
    ajusta,
    base_transicoes,
    contraste,
    holm,
    persistencia,
    por_transicao,
    salto,
)

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


def _horizontes(retido: float, n=600, seed=2):
    """x afeta 2014→2018 em −0,3; em 2022 resta a fração `retido` do efeito."""
    rng = np.random.default_rng(seed)
    amc = np.arange(n)
    x = rng.normal(size=n)
    logit = {2014: rng.normal(size=n)}
    logit[2018] = logit[2014] - 0.3 * x + rng.normal(0, 0.1, n)
    logit[2022] = logit[2014] - 0.3 * retido * x + rng.normal(0, 0.1, n)
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
        for ano in (2014, 2018, 2022)
    )
    _, geo, cov, _ = _dados(n=n)
    return painel, geo, cov, pl.DataFrame({"amc_id": amc, "x": x})


@pytest.mark.parametrize(
    ("retido", "classe"), [(1.0, "persistente"), (0.0, "passageiro"), (0.5, "inconclusivo")]
)
def test_persistencia_classifica_pela_fracao_retida(retido, classe):
    base = base_transicoes(*_horizontes(retido), transicoes=[(2014, 2018), (2014, 2022)])

    r = persistencia(base)

    assert r["retencao"] == pytest.approx(retido, abs=0.1)
    assert r["classe"] == classe


def test_duas_medidas_em_pp_sem_padronizar():
    painel, geo, cov, exp = _dados(efeito_alvo=0.0, seed=3)
    rng = np.random.default_rng(3)
    a, b = rng.uniform(0, 5, 600), rng.uniform(0, 5, 600)
    # a pesa −0,05 por unidade em 2014→2018; b não pesa
    painel = painel.with_columns(
        pl.when(pl.col("ano") == 2018)
        .then(pl.col("pt_2p_logit") - 0.05 * pl.Series(np.tile(a, 3)))
        .otherwise(pl.col("pt_2p_logit"))
    )
    exp = exp.select("amc_id").with_columns(x_a=pl.Series(a), x_b=pl.Series(b))

    base = base_transicoes(painel, geo, cov, exp, transicoes=TRANS, padroniza=False)
    fit = ajusta(base, "2014→2018", termos=("x_a", "x_b"))
    dif = contraste(fit, {"x_a": 1.0, "x_b": -1.0})

    assert base["x_a"].to_list()[:600] == pytest.approx(a.tolist())  # sem padronizar
    assert fit.coef()["x_a"] == pytest.approx(-0.05, abs=0.01)
    assert dif["ic_sup"] < 0


def test_holm_completo_e_igual_ao_classico():
    p = {"a": 0.001, "b": 0.02, "c": 0.04}

    assert holm(p, m=3) == {"a": "rejeita", "b": "rejeita", "c": "rejeita"}
    assert holm({"a": 0.001, "b": 0.03, "c": 0.04}, m=3) == {
        "a": "rejeita",
        "b": "nao_rejeita",  # 0,03 > 0,05/2
        "c": "nao_rejeita",
    }


def test_holm_com_pendentes():
    p = {"forte": 0.004, "medio": 0.02, "fraco": 0.2}

    res = holm(p, m=5)

    assert res["forte"] == "rejeita"  # ≤ 0,05/5 em qualquer caso
    assert res["medio"] == "pendente"  # > 0,05/4; ≤ 0,05/2 se os pendentes vierem antes
    assert res["fraco"] == "nao_rejeita"  # > 0,05 em qualquer ordem


def test_medida_nao_finita_fica_de_fora_sem_contaminar_a_padronizacao():
    painel, geo, cov, exp = _dados()
    exp = exp.with_columns(
        x=pl.when(pl.col("amc_id") == 0).then(float("nan")).otherwise(pl.col("x"))
    )

    base = base_transicoes(painel, geo, cov, exp, transicoes=TRANS)

    assert base.filter(pl.col("amc_id") == 0).height == 0
    assert base["x"].is_finite().all()
