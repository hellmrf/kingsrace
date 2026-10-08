"""Correspondência entre códigos de município do TSE e do IBGE.

Casa por UF + nome normalizado e aplica overrides manuais para renomeações e grafias
divergentes (data/reference/municipios_overrides.csv). Falha se a correspondência não
for completa e 1:1 — um erro aqui contamina silenciosamente todas as covariáveis.
"""

import re
import unicodedata

import polars as pl


class ErroCorrespondencia(ValueError):
    pass


def normaliza_nome(nome: str) -> str:
    """Remove acentos, apóstrofos e hífens; maiúsculas; espaços simples."""
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    return re.sub(r"[\s'\-]+", " ", sem_acento).strip().upper()


def casa_municipios(tse: pl.DataFrame, ibge: pl.DataFrame, overrides: pl.DataFrame) -> pl.DataFrame:
    """Devolve `cd_tse, cd_ibge` para cada município do TSE.

    tse: cd_tse, uf, nome · ibge: cd_ibge, uf, nome · overrides: cd_tse, cd_ibge
    """
    chave = pl.col("nome").map_elements(normaliza_nome, return_dtype=pl.String).alias("_nome")
    por_nome = tse.with_columns(chave).join(
        ibge.with_columns(chave).select("uf", "_nome", "cd_ibge"),
        on=["uf", "_nome"],
        how="left",
    )
    res = (
        por_nome.join(overrides.rename({"cd_ibge": "_override"}), on="cd_tse", how="left")
        .with_columns(pl.coalesce("_override", "cd_ibge").alias("cd_ibge"))
        .select("cd_tse", "uf", "nome", "cd_ibge")
    )

    sem_par = res.filter(pl.col("cd_ibge").is_null())
    if sem_par.height:
        lista = ", ".join(f"{r['cd_tse']} {r['nome']}/{r['uf']}" for r in sem_par.iter_rows(named=True))
        raise ErroCorrespondencia(f"códigos TSE sem par no IBGE: {lista}")

    repetidos = res.filter(pl.col("cd_ibge").is_duplicated())
    if repetidos.height:
        lista = ", ".join(
            f"{r['cd_ibge']} ← {r['cd_tse']} {r['nome']}" for r in repetidos.iter_rows(named=True)
        )
        raise ErroCorrespondencia(f"código IBGE com mais de um código TSE: {lista}")

    return res.select("cd_tse", "cd_ibge")
