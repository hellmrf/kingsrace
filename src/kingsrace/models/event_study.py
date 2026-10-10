"""Event study da série E (docs/hipoteses.md, "Série E: mecanismos da virada de 2018").

Para uma medida X de um mecanismo, o efeito de X (padronizada) sobre a variação do PT em
cada transição entre 1ºs turnos, com a base da C5 (log do eleitorado, nível inicial, efeitos
fixos e erros agrupados por região imediata) e os controles estruturais do Censo 2022.
O teste de "salto" compara o efeito na transição-alvo com o da transição anterior num
painel empilhado em que tudo é interagido com a transição. O mesmo painel empilhado, com
horizontes que partem todos de 2014, mede a persistência (E0b).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import polars as pl
import pyfixest as pf
from scipy import stats

TRANSICOES = [(2006, 2010), (2010, 2014), (2014, 2018), (2018, 2022), (2022, 2026)]
HORIZONTES = [(2014, 2018), (2014, 2022), (2014, 2026)]
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
    padroniza: bool = True,
) -> pl.DataFrame:
    """Uma linha por AMC × transição, com `dl`, `nivel`, `log_aptos`, controles e as medidas.

    `exposicao`: `amc_id`, uma ou mais medidas (em geral só `x`) e, se a medida muda no tempo,
    `de` (ano do pleito inicial da transição a que se aplica). Sem `de`, o mesmo valor vale
    para todas as transições. Com `padroniza`, cada medida é padronizada dentro de cada
    transição; AMCs sem alguma medida (nula, NaN ou infinita) ficam de fora da transição.
    """
    medidas = [c for c in exposicao.columns if c not in ("amc_id", "de")]
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
        d = (
            ini.join(fim, on="amc_id")
            .join(x.select("amc_id", *medidas), on="amc_id")
            .drop_nulls(medidas)
            .filter(pl.all_horizontal(pl.col(medidas).is_finite()))
        )
        if padroniza:
            d = d.with_columns((pl.col(m) - pl.col(m).mean()) / pl.col(m).std() for m in medidas)
        partes.append(
            d.with_columns(
                dl=pl.col("fim") - pl.col("nivel"), transicao=pl.lit(rotulo(de, para))
            ).drop("fim")
        )
    return (
        pl.concat(partes)
        .join(geo.select("amc_id", "cd_regiao_imediata"), on="amc_id")
        .join(controles, on="amc_id", how="left")
    )


def _formula(controles: bool, interage: bool, termos=("x",)) -> str:
    todos = [*termos, "log_aptos", "nivel", *(CONTROLES if controles else [])]
    if interage:
        return " + ".join(f"{t}:C(transicao)" for t in todos)
    return " + ".join(todos)


def ajusta(
    base: pl.DataFrame,
    transicao: str,
    termos=("x",),
    controles: bool = True,
    pesos: bool = False,
) -> pf.Feols:
    """O modelo de uma transição: Δ logit nas medidas e na base, EF de região imediata."""
    d = base.filter(pl.col("transicao") == transicao).with_columns(peso=pl.col("log_aptos").exp())
    return pf.feols(
        f"dl ~ {_formula(controles, False, termos)} | cd_regiao_imediata",
        d.to_pandas(),
        vcov=CLUSTER,
        weights="peso" if pesos else None,
    )


def por_transicao(
    base: pl.DataFrame, controles: bool = True, pesos: bool = False, termo: str = "x"
) -> pl.DataFrame:
    """Coeficiente de `termo` em cada transição (um modelo por transição)."""
    linhas = []
    for transicao in base["transicao"].unique(maintain_order=True):
        fit = ajusta(base, transicao, controles=controles, pesos=pesos)
        t = fit.tidy()
        linhas.append(
            {
                "transicao": transicao,
                "coef": t.loc[termo, "Estimate"],
                "ic_inf": t.loc[termo, "2.5%"],
                "ic_sup": t.loc[termo, "97.5%"],
                "p": t.loc[termo, "Pr(>|t|)"],
                "amcs": base.filter(pl.col("transicao") == transicao).height,
            }
        )
    return pl.DataFrame(linhas)


def empilha(
    base: pl.DataFrame, transicoes: list[str], termos=("x",), controles: bool = True
) -> pf.Feols:
    """Painel empilhado de várias transições, com tudo interagido com a transição.

    Efeitos fixos de região imediata × transição, erros agrupados por região imediata: a
    mesma região aparece em todas as transições, então a covariância entre os coeficientes
    entra no erro de qualquer combinação deles.
    """
    d = (
        base.filter(pl.col("transicao").is_in(transicoes))
        .with_columns(ri_t=pl.format("{}_{}", "cd_regiao_imediata", "transicao"))
        .to_pandas()
    )
    return pf.feols(f"dl ~ {_formula(controles, True, termos)} | ri_t", d, vcov=CLUSTER)


def contraste(fit: pf.Feols, pesos: dict[str, float]) -> dict:
    """Combinação linear Σ wᵢ·βᵢ, com IC 95% e p (t com G − 1 graus de liberdade)."""
    coef = fit.coef()
    c = pd.Series(0.0, index=coef.index)
    for nome, w in pesos.items():
        c[nome] = w
    valor = float(c @ coef)
    ep = float(np.sqrt(c.to_numpy() @ fit._vcov @ c.to_numpy()))
    gl = min(fit._G) - 1
    q = stats.t.ppf(0.975, gl)
    return {
        "valor": valor,
        "ic_inf": valor - q * ep,
        "ic_sup": valor + q * ep,
        "p": float(2 * stats.t.sf(abs(valor / ep), gl)),
    }


def _termo(transicao: str, termo: str = "x") -> str:
    return f"{termo}:C(transicao)[{transicao}]"


def salto(
    base: pl.DataFrame,
    alvo: tuple[int, int] = (2014, 2018),
    anterior: tuple[int, int] = (2010, 2014),
    controles: bool = True,
) -> dict:
    """β(alvo) − β(anterior) num painel empilhado das duas transições."""
    nomes = [rotulo(*alvo), rotulo(*anterior)]
    fit = empilha(base, nomes, controles=controles)
    a, b = (_termo(n) for n in nomes)
    dif = contraste(fit, {a: 1.0, b: -1.0})
    return {
        "alvo": nomes[0],
        "anterior": nomes[1],
        "beta_alvo": float(fit.coef()[a]),
        "beta_anterior": float(fit.coef()[b]),
        "diferenca": dif["valor"],
        **{k: dif[k] for k in ("ic_inf", "ic_sup", "p")},
    }


def persistencia(
    base: pl.DataFrame,
    alvo: tuple[int, int] = (2014, 2018),
    depois: tuple[int, int] = (2014, 2022),
    fracao: float = 0.5,
) -> dict:
    """E0b: D = β(depois) − fração · β(alvo), com os dois horizontes partindo do mesmo ano.

    `base` precisa ter os dois horizontes (ex.: `base_transicoes(..., HORIZONTES)`).
    Persistente: D com o sinal de β(alvo) e IC sem o zero (retém mais que a fração);
    passageiro: D com o sinal oposto e IC sem o zero; senão, inconclusivo.
    """
    nomes = [rotulo(*alvo), rotulo(*depois)]
    fit = empilha(base, nomes)
    a, b = (_termo(n) for n in nomes)
    beta_alvo, beta_depois = float(fit.coef()[a]), float(fit.coef()[b])
    d = contraste(fit, {b: 1.0, a: -fracao})
    sinal = np.sign(beta_alvo)
    if sinal * d["ic_inf"] > 0 and sinal * d["ic_sup"] > 0:
        classe = "persistente"
    elif sinal * d["ic_inf"] < 0 and sinal * d["ic_sup"] < 0:
        classe = "passageiro"
    else:
        classe = "inconclusivo"
    return {
        "beta_alvo": beta_alvo,
        "beta_depois": beta_depois,
        "retencao": beta_depois / beta_alvo,
        "d": d["valor"],
        "ic_inf": d["ic_inf"],
        "ic_sup": d["ic_sup"],
        "p": d["p"],
        "classe": classe,
    }


def holm(pvals: dict[str, float], m: int, alfa: float = 0.05) -> dict[str, str]:
    """Holm com testes ainda não calculados (registro de 2026-10-10).

    `pvals` traz os testes já calculados; faltam `m − len(pvals)`. Cada teste sai como
    "rejeita" (rejeitado mesmo com todos os pendentes no fim da ordem, p = 1), "nao_rejeita"
    (não rejeitado nem com todos os pendentes no começo, p = 0) ou "pendente".
    """
    ordem = sorted(pvals, key=pvals.get)
    k = len(ordem)
    if k > m:
        raise ValueError(f"{k} testes calculados, mais que os {m} da família")

    def rejeitados(limiares):
        fora = set()
        for nome, limiar in zip(ordem, limiares, strict=True):
            if pvals[nome] > limiar:
                break
            fora.add(nome)
        return fora

    garantidos = rejeitados([alfa / (m - j) for j in range(k)])
    possiveis = rejeitados([alfa / (k - j) for j in range(k)])
    return {
        n: "rejeita" if n in garantidos else "pendente" if n in possiveis else "nao_rejeita"
        for n in pvals
    }
