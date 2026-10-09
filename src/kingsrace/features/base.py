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
    Se uma AMC atravessar regiões imediatas, fica com a mais frequente entre os membros.
    """

    def pleito(ano_turno, sufixo):
        ano, turno = ano_turno
        return painel_amc.filter((pl.col("ano") == ano) & (pl.col("turno") == turno)).select(
            "amc_id", *(pl.col(c).alias(f"{c}_{sufixo}") for c in ("aptos", "pt_2p", "pt_2p_logit"))
        )

    # região imediata da AMC: a mais frequente entre os membros (empate: menor código).
    # Só importa para AMCs que atravessam regiões (ex.: Paraíso das Águas/MS).
    regiao_amc = (
        municipios.group_by("amc_id", "cd_regiao_imediata", "regiao_imediata")
        .len()
        .sort(["amc_id", "len", "cd_regiao_imediata"], descending=[False, True, False])
        .group_by("amc_id", maintain_order=True)
        .first()
        .drop("len")
    )
    geo = (
        municipios.group_by("amc_id")
        .agg(pl.col("nome").sort().str.join(" + "), pl.col("uf", "regiao").first())
        .join(regiao_amc, on="amc_id")
    )

    return (
        pleito(de, "de")
        .join(pleito(para, "para"), on="amc_id")
        .join(geo, on="amc_id")
        .join(cov_amc, on="amc_id", how="left")
        .with_columns(
            delta_logit=pl.col("pt_2p_logit_para") - pl.col("pt_2p_logit_de"),
            delta_pp=100 * (pl.col("pt_2p_para") - pl.col("pt_2p_de")),
            log_aptos_de=pl.col("aptos_de").log(),
        )
        .sort("amc_id")
    )
