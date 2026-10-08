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
    """Devolve `cd_tse, cd_ibge` para cada código de município do TSE.

    tse: cd_tse, uf, nome — pode ter vários nomes por código (renomeações entre pleitos);
    basta um casar. ibge: cd_ibge, uf, nome. overrides: cd_tse, cd_ibge — têm precedência.
    """
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
