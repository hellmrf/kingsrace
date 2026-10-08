"""Correspondência entre códigos de município do TSE e do IBGE.

Casa por UF + nome normalizado e aplica overrides manuais para renomeações e grafias
divergentes (data/reference/municipios_overrides.csv). Falha se a correspondência não
for completa e 1:1 — um erro aqui contamina silenciosamente todas as covariáveis.
"""

import re
import unicodedata

import polars as pl

from kingsrace import paths


class ErroCorrespondencia(ValueError):
    pass


def normaliza_nome(nome: str) -> str:
    """Remove acentos, apóstrofos e hífens; maiúsculas; espaços simples."""
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    return re.sub(r"[\s'\-]+", " ", sem_acento).strip().upper()


def casa_municipios(tse: pl.DataFrame, ibge: pl.DataFrame, overrides: pl.DataFrame) -> pl.DataFrame:
    """Devolve `cd_tse, cd_ibge` para cada código de município do TSE.

    tse: cd_tse, uf, nome — pode ter vários nomes por código (renomeações entre pleitos);
    basta um casar. ibge: cd_ibge, uf, nome. overrides: cd_tse, cd_ibge (+ colunas de
    documentação, ignoradas) — têm precedência.
    """
    overrides = overrides.select(
        pl.col("cd_tse").cast(tse.schema["cd_tse"]), pl.col("cd_ibge").cast(ibge.schema["cd_ibge"])
    )
    chave = pl.col("nome").map_elements(normaliza_nome, return_dtype=pl.String).alias("_nome")
    por_nome = (
        tse.with_columns(chave)
        .join(ibge.with_columns(chave).select("uf", "_nome", "cd_ibge"), on=["uf", "_nome"])
        .join(overrides, on="cd_tse", how="anti")
        .select("cd_tse", "cd_ibge")
    )
    res = pl.concat(
        [por_nome, overrides.join(tse.select("cd_tse"), on="cd_tse", how="semi")]
    ).unique()

    sem_par = tse.join(res, on="cd_tse", how="anti")
    if sem_par.height:
        lista = ", ".join(
            f"{r['cd_tse']} {r['nome']}/{r['uf']}" for r in sem_par.iter_rows(named=True)
        )
        raise ErroCorrespondencia(f"códigos TSE sem par no IBGE: {lista}")

    for origem, destino in (("cd_tse", "cd_ibge"), ("cd_ibge", "cd_tse")):
        multiplos = (
            res.group_by(origem).agg(pl.col(destino).sort()).filter(pl.col(destino).list.len() > 1)
        )
        if multiplos.height:
            lista = "; ".join(
                f"{o} → {', '.join(map(str, d))}" for o, d in multiplos.sort(origem).iter_rows()
            )
            tipo = {"cd_tse": "TSE", "cd_ibge": "IBGE"}
            raise ErroCorrespondencia(
                f"código {tipo[origem]} com mais de um código {tipo[destino]}: {lista}"
            )

    return res.sort("cd_tse")


def atribui_amc(municipios: pl.DataFrame, amc: pl.DataFrame) -> pl.DataFrame:
    """Acrescenta `amc_id`: o de data/reference/amc.csv, ou o próprio `cd_ibge`."""
    return municipios.join(amc.select("cd_ibge", "amc_id"), on="cd_ibge", how="left").with_columns(
        pl.coalesce("amc_id", "cd_ibge").alias("amc_id")
    )


def le_ibge(caminho) -> pl.DataFrame:
    """Lê o JSON da API de localidades do IBGE (view=nivelado)."""
    return pl.read_json(caminho).select(
        pl.col("municipio-id").alias("cd_ibge"),
        pl.col("municipio-nome").alias("nome"),
        pl.col("UF-sigla").alias("uf"),
        pl.col("regiao-sigla").alias("regiao"),
        pl.col("regiao-intermediaria-id").alias("cd_regiao_intermediaria"),
        pl.col("regiao-intermediaria-nome").alias("regiao_intermediaria"),
        pl.col("regiao-imediata-id").alias("cd_regiao_imediata"),
        pl.col("regiao-imediata-nome").alias("regiao_imediata"),
    )


def executa() -> None:
    """Gera data/processed/municipios.parquet a partir de todos os anos convertidos."""
    tse = (
        pl.scan_parquet(paths.INTERIM / "tse" / "detalhe_munzona" / "*" / "*.parquet")
        .filter(pl.col("sg_uf") != "ZZ")
        .select(
            pl.col("cd_municipio").alias("cd_tse"),
            pl.col("sg_uf").alias("uf"),
            pl.col("nm_municipio").alias("nome"),
        )
        .unique()
        .collect()
    )
    ibge = le_ibge(paths.RAW / "ibge" / "municipios.json")
    overrides = pl.read_csv(paths.REFERENCE / "municipios_overrides.csv")
    amc = pl.read_csv(paths.REFERENCE / "amc.csv")

    pares = casa_municipios(tse, ibge.select("cd_ibge", "uf", "nome"), overrides)
    municipios = atribui_amc(pares.join(ibge, on="cd_ibge"), amc).sort("cd_ibge")
    paths.PROCESSED.mkdir(parents=True, exist_ok=True)
    municipios.write_parquet(paths.PROCESSED / "municipios.parquet")


if __name__ == "__main__":
    executa()
