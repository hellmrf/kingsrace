"""Voto em candidatos religiosos para deputado federal, por AMC e eleição (medida E2c).

Regra registrada em docs/hipoteses.md (E2c): religioso = ocupação declarada "sacerdote ou
membro de ordem ou seita religiosa" **ou** nome de urna começando por um título evangélico;
nomes começando por "Padre" ou "Frei" ficam de fora. A ocupação vem do cadastro de
candidatos (`consulta_cand`); o nome de urna, do próprio arquivo de votação, porque alguns
candidatos com voto não estão no cadastro (sem ocupação conhecida, contam só pelo título).
"""

import polars as pl

from kingsrace import paths

OCUPACAO_RELIGIOSA = "SACERDOTE OU MEMBRO DE ORDEM OU SEITA RELIGIOSA"
# título no início do nome de urna; "PR" só como abreviação (com ponto ou seguido de espaço)
TITULO_EVANGELICO = (
    r"^(PASTORA?|BISP[OA]|AP[OÓ]STOL[OA]|MISSION[AÁ]RI[OA]|PRESB[IÍ]TERO)\b|^PR\.|^PR\s"
)
TITULO_CATOLICO = r"^(PADRE|FREI)\b"


def eh_religioso(nome_urna: str = "nm_urna_candidato", ocupacao: str = "ds_ocupacao") -> pl.Expr:
    """Expressão booleana da regra da E2c (ocupação nula conta como não religiosa)."""
    nome = pl.col(nome_urna).str.to_uppercase().str.strip_chars()
    por_ocupacao = (pl.col(ocupacao) == OCUPACAO_RELIGIOSA).fill_null(False)
    return (por_ocupacao | nome.str.contains(TITULO_EVANGELICO)) & ~nome.str.contains(
        TITULO_CATOLICO
    )


def religiosos_amc(
    votos: pl.DataFrame,
    candidatos: pl.DataFrame,
    detalhe: pl.DataFrame,
    municipios: pl.DataFrame,
) -> pl.DataFrame:
    """Votos válidos em candidatos religiosos e válidos totais para deputado federal por AMC.

    `votos` precisa de `votos_validos` (votos nominais válidos por candidato e zona);
    `detalhe`, de `qt_total_votos_validos` (nominais + legenda). Falha se algum município
    do TSE não tiver AMC.
    """
    ocupacao = candidatos.select("ano_eleicao", "sg_uf", "sq_candidato", "ds_ocupacao")
    por_mun = (
        votos.join(ocupacao, on=["ano_eleicao", "sg_uf", "sq_candidato"], how="left")
        .with_columns(religioso=eh_religioso())
        .group_by("ano_eleicao", "cd_municipio")
        .agg(
            votos_religiosos=pl.col("votos_validos").filter(pl.col("religioso")).sum(),
            nominais_validos=pl.col("votos_validos").sum(),
        )
        .join(
            detalhe.group_by("ano_eleicao", "cd_municipio").agg(
                validos_deputado=pl.col("qt_total_votos_validos").sum()
            ),
            on=["ano_eleicao", "cd_municipio"],
            how="full",
            coalesce=True,
        )
        .with_columns(pl.col("votos_religiosos", "nominais_validos").fill_null(0))
    )
    mapa = municipios.select(pl.col("cd_tse").cast(pl.Int32), "amc_id")
    sem_par = por_mun.join(mapa, left_on="cd_municipio", right_on="cd_tse", how="anti")
    if sem_par.height:
        raise ValueError(f"municípios do TSE sem AMC: {sem_par['cd_municipio'].to_list()}")
    return (
        por_mun.join(mapa, left_on="cd_municipio", right_on="cd_tse")
        .group_by("amc_id", pl.col("ano_eleicao").alias("ano"))
        .agg(pl.col("votos_religiosos", "nominais_validos", "validos_deputado").sum())
        .with_columns(pct_religiosos=100 * pl.col("votos_religiosos") / pl.col("validos_deputado"))
        .sort("amc_id", "ano")
    )


def le_votos_deputado(interim) -> pl.DataFrame:
    """Lê os votos por candidato de todos os anos, com `votos_validos` padronizado."""
    partes = []
    for arq in sorted((interim / "votacao_deputado").glob("ano=*/data.parquet")):
        v = pl.read_parquet(arq)
        # até 2014 os anulados já vêm zerados em qt_votos_nominais (ver ingest/tse.py)
        validos = "qt_votos_nominais_validos" if "qt_votos_nominais_validos" in v.columns else None
        partes.append(
            v.filter(pl.col("nr_turno") == 1).with_columns(
                votos_validos=pl.col(validos or "qt_votos_nominais")
            )
        )
    return pl.concat(partes, how="diagonal")


def executa() -> None:
    interim = paths.INTERIM / "tse"
    resultado = religiosos_amc(
        le_votos_deputado(interim),
        pl.read_parquet(interim / "candidatos" / "**" / "*.parquet", hive_partitioning=False),
        pl.read_parquet(
            interim / "detalhe_deputado" / "**" / "*.parquet", hive_partitioning=False
        ).filter(pl.col("nr_turno") == 1),
        pl.read_parquet(paths.PROCESSED / "municipios.parquet"),
    )
    resultado.write_parquet(paths.PROCESSED / "religiosos_amc.parquet")


if __name__ == "__main__":
    executa()
