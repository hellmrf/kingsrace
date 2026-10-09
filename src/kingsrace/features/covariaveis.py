"""Covariáveis municipais (Censo 2022, PIB dos Municípios) por município e por AMC."""

import json

import polars as pl

from kingsrace import paths
from kingsrace.ingest.ibge import CONSULTAS, sidra_para_tabela

SOMAS = ["populacao", "area_km2"]  # agregadas por soma na AMC; o resto, média ponderada


def deriva_covariaveis(df: pl.DataFrame) -> pl.DataFrame:
    """PIB per capita (R$), participações no valor adicionado (%), % preta + parda.

    Participação setorial fica nula quando o VA total não é positivo (ex.: Cachoeira
    Dourada/GO em 2021, VA negativo por causa da usina hidrelétrica na crise hídrica).
    """
    novas = []
    for ano in ("2021", "2023"):
        if f"pib_{ano}" in df.columns:
            novas.append((1000 * pl.col(f"pib_{ano}") / pl.col("populacao")).alias(f"pib_pc_{ano}"))
        for setor in ("agro", "adm"):
            if f"va_{setor}_{ano}" in df.columns:
                va = pl.col(f"va_{ano}")
                novas.append(
                    pl.when(va > 0)
                    .then(100 * pl.col(f"va_{setor}_{ano}") / va)
                    .alias(f"pct_va_{setor}_{ano}")
                )
    if {"pct_preta", "pct_parda"} <= set(df.columns):
        novas.append((pl.col("pct_preta") + pl.col("pct_parda")).alias("pct_preta_parda"))
    return df.with_columns(novas)


def agrega_covariaveis_amc(cov: pl.DataFrame, municipios: pl.DataFrame) -> pl.DataFrame:
    """Soma população e área; demais colunas pela média ponderada pela população.

    É uma aproximação para taxas com denominadores diferentes (religião é sobre 10+ anos,
    alfabetização sobre 15+), aceitável porque só agrupa municípios vizinhos.
    Municípios sem dados (instalados depois do Censo) não entram nos pesos.
    """
    taxas = [c for c in cov.columns if c not in {"cd_ibge", "densidade", *SOMAS}]
    peso = pl.col("populacao")
    return (
        cov.join(municipios.select("cd_ibge", "amc_id"), on="cd_ibge")
        .filter(peso.is_not_null())
        .group_by("amc_id")
        .agg(
            *(pl.col(c).sum() for c in SOMAS if c in cov.columns),
            *(
                ((pl.col(c) * peso).sum() / peso.filter(pl.col(c).is_not_null()).sum()).alias(c)
                for c in taxas
            ),
        )
        .with_columns((pl.col("populacao") / pl.col("area_km2")).alias("densidade"))
    )


def executa() -> None:
    raw = paths.RAW / "ibge" / "sidra"
    tabelas = [
        sidra_para_tabela(json.loads((raw / f"{nome}.json").read_text("utf8")), colunas)
        for nome, (_, colunas) in CONSULTAS.items()
    ]
    cov = tabelas[0]
    for t in tabelas[1:]:
        cov = cov.join(t, on="cd_ibge", how="full", coalesce=True)
    cov = deriva_covariaveis(cov).sort("cd_ibge")

    municipios = pl.read_parquet(paths.PROCESSED / "municipios.parquet")
    cov = municipios.select("cd_ibge").join(cov, on="cd_ibge", how="left")
    cov.write_parquet(paths.PROCESSED / "covariaveis_municipio.parquet")
    agrega_covariaveis_amc(cov, municipios).sort("amc_id").write_parquet(
        paths.PROCESSED / "covariaveis_amc.parquet"
    )


if __name__ == "__main__":
    executa()
