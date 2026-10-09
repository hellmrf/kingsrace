"""Bases de análise: uma linha por AMC comparando dois pleitos."""

import polars as pl


def base_variacao(
    painel_amc: pl.DataFrame,
    cov_amc: pl.DataFrame,
    municipios: pl.DataFrame,
    de: tuple[int, int],
    para: tuple[int, int],
) -> pl.DataFrame:
    """Variação do PT entre dois pleitos (ano, turno) por AMC, com tamanho e covariáveis.

    Colunas: `delta_logit` e `delta_pp` (de `pt_2p`), níveis `*_de`/`*_para`,
    `log_aptos_de`, geografia (nome, uf, regiao, região imediata) e as covariáveis.
    Falha se uma AMC atravessar regiões imediatas (os efeitos fixos dependem disso).
    """

    def pleito(ano_turno, sufixo):
        ano, turno = ano_turno
        return painel_amc.filter((pl.col("ano") == ano) & (pl.col("turno") == turno)).select(
            "amc_id", *(pl.col(c).alias(f"{c}_{sufixo}") for c in ("aptos", "pt_2p", "pt_2p_logit"))
        )

    geo = municipios.group_by("amc_id").agg(
        pl.col("nome").sort().str.join(" + "),
        pl.col("uf", "regiao", "regiao_imediata").first(),
        pl.col("cd_regiao_imediata").first(),
        pl.col("cd_regiao_imediata").n_unique().alias("_n_ri"),
    )
    multiplas = geo.filter(pl.col("_n_ri") > 1)
    if multiplas.height:
        raise ValueError(f"AMC em mais de uma região imediata: {multiplas['amc_id'].to_list()}")

    return (
        pleito(de, "de")
        .join(pleito(para, "para"), on="amc_id")
        .join(geo.drop("_n_ri"), on="amc_id")
        .join(cov_amc, on="amc_id", how="left")
        .with_columns(
            delta_logit=pl.col("pt_2p_logit_para") - pl.col("pt_2p_logit_de"),
            delta_pp=100 * (pl.col("pt_2p_para") - pl.col("pt_2p_de")),
            log_aptos_de=pl.col("aptos_de").log(),
        )
        .sort("amc_id")
    )
