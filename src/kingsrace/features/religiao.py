"""Voto em candidatos religiosos para deputado federal, por AMC e eleição (medida E2c).

Regra registrada em docs/hipoteses.md (E2c): religioso = ocupação declarada "sacerdote ou
membro de ordem ou seita religiosa" **ou** nome de urna começando por um título evangélico;
nomes começando por "Padre" ou "Frei" ficam de fora. A ocupação vem do cadastro de
candidatos (`consulta_cand`); o nome de urna, do próprio arquivo de votação, porque alguns
candidatos com voto não estão no cadastro (sem ocupação conhecida, contam só pelo título).

Para a E2d, o voto religioso também é separado pelo partido do candidato: da coligação
presidencial do PT naquele ano ou não, e PRB/Republicanos (Igreja Universal).
"""

import io
import re
import zipfile
from pathlib import Path

import polars as pl

from kingsrace import paths

PRB = ("PRB", "REPUBLICANOS")
ANOS_DEPUTADOS = (2006, 2010, 2014, 2018, 2022)

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


def partidos_coligacao(composicao: str) -> list[str]:
    """Siglas de `DS_COMPOSICAO_COLIGACAO`; federações (2022) entram pelos seus partidos.

    Ex.: "Federação Brasil da Esperança - FE BRASIL (PT / PC do B / PV) / PSB" →
    ["PT", "PC do B", "PV", "PSB"].
    """
    sem_federacao = re.sub(r"Federação[^(]*\(([^)]*)\)", r"\1", composicao)
    return [p.strip() for p in sem_federacao.split("/") if p.strip()]


def coligacao_pt(zips: dict[int, Path]) -> pl.DataFrame:
    """`ano_eleicao`, `sg_partido` da coligação presidencial do PT (1º turno), do cadastro."""
    linhas = []
    for ano, arq in zips.items():
        with zipfile.ZipFile(arq) as z:
            cand = pl.read_csv(
                io.BytesIO(z.read(f"consulta_cand_{ano}_BRASIL.csv")),
                separator=";",
                encoding="latin1",
                infer_schema=False,
                columns=["DS_CARGO", "SG_PARTIDO", "NR_TURNO", "DS_COMPOSICAO_COLIGACAO"],
            )
        comp = (
            cand.filter(
                (pl.col("DS_CARGO").str.to_uppercase() == "PRESIDENTE")
                & (pl.col("SG_PARTIDO") == "PT")
                & (pl.col("NR_TURNO") == "1")
            )["DS_COMPOSICAO_COLIGACAO"]
            .unique()
            .to_list()
        )
        if len(comp) != 1:
            raise ValueError(f"{ano}: esperava uma coligação presidencial do PT, achei {comp}")
        linhas += [{"ano_eleicao": ano, "sg_partido": p} for p in partidos_coligacao(comp[0])]
    return pl.DataFrame(linhas, schema={"ano_eleicao": pl.Int16, "sg_partido": pl.String})


def religiosos_amc(
    votos: pl.DataFrame,
    candidatos: pl.DataFrame,
    detalhe: pl.DataFrame,
    municipios: pl.DataFrame,
    coligacao: pl.DataFrame | None = None,
) -> pl.DataFrame:
    """Votos válidos em candidatos religiosos e válidos totais para deputado federal por AMC.

    `votos` precisa de `votos_validos` (votos nominais válidos por candidato e zona);
    `detalhe`, de `qt_total_votos_validos` (nominais + legenda). Falha se algum município
    do TSE não tiver AMC. Com `coligacao` (`ano_eleicao`, `sg_partido`), `votos` precisa de
    `sg_partido` e o resultado ganha a separação da E2d: votos religiosos da coligação, do
    PRB/Republicanos e o total nominal da coligação (religiosos ou não).
    """
    ocupacao = candidatos.select("ano_eleicao", "sg_uf", "sq_candidato", "ds_ocupacao")
    votos = votos.join(ocupacao, on=["ano_eleicao", "sg_uf", "sq_candidato"], how="left")
    somas = {
        "votos_religiosos": pl.col("religioso"),
        "nominais_validos": pl.lit(True),
    }
    if coligacao is not None:
        votos = votos.join(
            coligacao.select(
                pl.col("ano_eleicao").cast(votos.schema["ano_eleicao"]),
                "sg_partido",
                da_coligacao=pl.lit(True),
            ),
            on=["ano_eleicao", "sg_partido"],
            how="left",
        ).with_columns(pl.col("da_coligacao").fill_null(False))
        somas |= {
            "votos_religiosos_coligacao": pl.col("religioso") & pl.col("da_coligacao"),
            "votos_religiosos_prb": pl.col("religioso") & pl.col("sg_partido").is_in(PRB),
            "votos_coligacao": pl.col("da_coligacao"),
        }
    por_mun = (
        votos.with_columns(religioso=eh_religioso())
        .group_by("ano_eleicao", "cd_municipio")
        .agg(pl.col("votos_validos").filter(f).sum().alias(nome) for nome, f in somas.items())
        .join(
            detalhe.group_by("ano_eleicao", "cd_municipio").agg(
                validos_deputado=pl.col("qt_total_votos_validos").sum()
            ),
            on=["ano_eleicao", "cd_municipio"],
            how="full",
            coalesce=True,
        )
        .with_columns(pl.col(*somas).fill_null(0))
    )
    mapa = municipios.select(pl.col("cd_tse").cast(pl.Int32), "amc_id")
    sem_par = por_mun.join(mapa, left_on="cd_municipio", right_on="cd_tse", how="anti")
    if sem_par.height:
        raise ValueError(f"municípios do TSE sem AMC: {sem_par['cd_municipio'].to_list()}")
    return (
        por_mun.join(mapa, left_on="cd_municipio", right_on="cd_tse")
        .group_by("amc_id", pl.col("ano_eleicao").alias("ano"))
        .agg(pl.col(*somas, "validos_deputado").sum())
        .with_columns(
            (100 * pl.col(c) / pl.col("validos_deputado")).alias(c.replace("votos_", "pct_"))
            for c in somas
            if c != "nominais_validos"
        )
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
        coligacao_pt(
            {
                a: paths.RAW / "tse" / "consulta_cand" / f"consulta_cand_{a}.zip"
                for a in ANOS_DEPUTADOS
            }
        ),
    )
    resultado.write_parquet(paths.PROCESSED / "religiosos_amc.parquet")


if __name__ == "__main__":
    executa()
