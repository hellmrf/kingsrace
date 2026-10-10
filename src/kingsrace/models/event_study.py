"""Event study da série E (docs/hipoteses.md, "Série E: mecanismos da virada de 2018").

Para uma medida X de um mecanismo, o efeito de X (padronizada) sobre a variação do PT em
cada transição entre 1ºs turnos, com a base da C5 (log do eleitorado, nível inicial, efeitos
fixos e erros agrupados por região imediata) e os controles estruturais do Censo 2022.
O teste de "salto" compara o efeito na transição-alvo com o da transição anterior num
painel empilhado em que tudo é interagido com a transição.
"""

import numpy as np
import pandas as pd
import polars as pl
import pyfixest as pf
from scipy import stats

TRANSICOES = [(2006, 2010), (2010, 2014), (2014, 2018), (2018, 2022), (2022, 2026)]
CONTROLES = ["log_renda", "taxa_alfabetizacao", "pct_urbana", "idade_mediana", "pct_preta_parda"]
CLUSTER = {"CRV1": "cd_regiao_imediata"}


def rotulo(de: int, para: int) -> str:
    return f"{de}→{para}"


def base_transicoes(
    painel_amc: pl.DataFrame,
    geo: pl.DataFrame,
    cov: pl.DataFrame,
    exposicao: pl.DataFrame,
    transicoes=TRANSICOES,
) -> pl.DataFrame:
    """Uma linha por AMC × transição, com `dl`, `nivel`, `log_aptos`, controles e `x`.

    `exposicao`: `amc_id`, `x` e, se a medida muda no tempo, `de` (ano do pleito inicial da
    transição a que se aplica). Sem `de`, o mesmo valor vale para todas as transições.
    `x` é padronizada dentro de cada transição; AMCs sem `x` ficam de fora dela.
    """
    primeiro = painel_amc.filter(pl.col("turno") == 1)
    controles = cov.select(
        "amc_id", pl.col("renda_pc_mediana").log().alias("log_renda"), *CONTROLES[1:]
    )
    partes = []
    for de, para in transicoes:
        ini = primeiro.filter(pl.col("ano") == de).select(
            "amc_id", nivel=pl.col("pt_2p_logit"), log_aptos=pl.col("aptos").log()
        )
        fim = primeiro.filter(pl.col("ano") == para).select("amc_id", fim=pl.col("pt_2p_logit"))
        x = exposicao.filter(pl.col("de") == de) if "de" in exposicao.columns else exposicao
        partes.append(
            ini.join(fim, on="amc_id")
            .join(x.select("amc_id", "x"), on="amc_id")
            .drop_nulls("x")
            .with_columns(
                dl=pl.col("fim") - pl.col("nivel"),
                x=(pl.col("x") - pl.col("x").mean()) / pl.col("x").std(),
                transicao=pl.lit(rotulo(de, para)),
            )
            .drop("fim")
        )
    return (
        pl.concat(partes)
        .join(geo.select("amc_id", "cd_regiao_imediata"), on="amc_id")
        .join(controles, on="amc_id", how="left")
    )


def _formula(controles: bool, interage: bool) -> str:
    termos = ["x", "log_aptos", "nivel", *(CONTROLES if controles else [])]
    if interage:
        return " + ".join(f"{t}:C(transicao)" for t in termos)
    return " + ".join(termos)


def por_transicao(base: pl.DataFrame, controles: bool = True, pesos: bool = False) -> pl.DataFrame:
    """Coeficiente de `x` em cada transição (um modelo por transição)."""
    linhas = []
    for transicao in base["transicao"].unique(maintain_order=True):
        d = base.filter(pl.col("transicao") == transicao).with_columns(
            peso=pl.col("log_aptos").exp()
        )
        fit = pf.feols(
            f"dl ~ {_formula(controles, False)} | cd_regiao_imediata",
            d.to_pandas(),
            vcov=CLUSTER,
            weights="peso" if pesos else None,
        )
        t = fit.tidy()
        linhas.append(
            {
                "transicao": transicao,
                "coef": t.loc["x", "Estimate"],
                "ic_inf": t.loc["x", "2.5%"],
                "ic_sup": t.loc["x", "97.5%"],
                "p": t.loc["x", "Pr(>|t|)"],
                "amcs": d.height,
            }
        )
    return pl.DataFrame(linhas)


def salto(
    base: pl.DataFrame,
    alvo: tuple[int, int] = (2014, 2018),
    anterior: tuple[int, int] = (2010, 2014),
    controles: bool = True,
) -> dict:
    """β(alvo) − β(anterior) num painel empilhado das duas transições.

    Tudo interagido com a transição, efeitos fixos de região imediata × transição, erros
    agrupados por região imediata (a mesma região aparece nas duas transições, então a
    covariância entre os dois coeficientes entra no erro da diferença).
    """
    nomes = [rotulo(*alvo), rotulo(*anterior)]
    d = (
        base.filter(pl.col("transicao").is_in(nomes))
        .with_columns(ri_t=pl.format("{}_{}", "cd_regiao_imediata", "transicao"))
        .to_pandas()
    )
    fit = pf.feols(f"dl ~ {_formula(controles, True)} | ri_t", d, vcov=CLUSTER)
    coef = fit.coef()
    a, b = (f"x:C(transicao)[{n}]" for n in nomes)
    c = pd.Series(0.0, index=coef.index)
    c[a], c[b] = 1.0, -1.0
    dif = float(c @ coef)
    ep = float(np.sqrt(c.to_numpy() @ fit._vcov @ c.to_numpy()))
    gl = min(fit._G) - 1
    q = stats.t.ppf(0.975, gl)
    return {
        "alvo": nomes[0],
        "anterior": nomes[1],
        "beta_alvo": float(coef[a]),
        "beta_anterior": float(coef[b]),
        "diferenca": dif,
        "ic_inf": dif - q * ep,
        "ic_sup": dif + q * ep,
        "p": float(2 * stats.t.sf(abs(dif / ep), gl)),
    }
