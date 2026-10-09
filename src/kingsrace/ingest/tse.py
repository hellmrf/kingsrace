"""Conversão dos arquivos do TSE (CSV latin-1 com `;`, dentro de zip) para parquet."""

import tempfile
import zipfile
from pathlib import Path

import duckdb

from kingsrace import paths


def csv_zip_para_parquet(
    zip_path: Path,
    membro: str,
    destino: Path,
    colunas: dict[str, str],
    filtro: str | None = None,
) -> None:
    """Extrai `membro` do zip e grava as `colunas` (nome TSE → tipo DuckDB) em parquet.

    Tudo é lido como texto e só as colunas pedidas são convertidas, porque o TSE às
    vezes põe aspas nos números e às vezes não. Por isso `filtro` (SQL) compara texto,
    ex.: `CD_CARGO = '1'`. As colunas de saída ficam em minúsculas.
    """
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    select = ", ".join(f'CAST("{c}" AS {t}) AS {c.lower()}' for c, t in colunas.items())
    where = f"WHERE {filtro}" if filtro else ""

    with tempfile.TemporaryDirectory(dir=destino.parent) as tmp:
        with zipfile.ZipFile(zip_path) as z:
            csv = z.extract(membro, tmp)
        duckdb.sql(
            f"""
            COPY (
                SELECT {select}
                FROM read_csv('{csv}', delim=';', quote='"', header=true,
                              encoding='latin-1', all_varchar=true)
                {where}
            ) TO '{destino}' (FORMAT parquet, COMPRESSION zstd)
            """
        )


SECAO = {
    "ANO_ELEICAO": "SMALLINT",
    "NR_TURNO": "TINYINT",
    "SG_UF": "VARCHAR",
    "CD_MUNICIPIO": "INTEGER",
    "NM_MUNICIPIO": "VARCHAR",
    "NR_ZONA": "INTEGER",
    "NR_SECAO": "INTEGER",
    "NR_LOCAL_VOTACAO": "INTEGER",
    "NR_VOTAVEL": "INTEGER",
    "NM_VOTAVEL": "VARCHAR",
    "QT_VOTOS": "BIGINT",
}

DETALHE = {
    "ANO_ELEICAO": "SMALLINT",
    "NR_TURNO": "TINYINT",
    "SG_UF": "VARCHAR",
    "CD_MUNICIPIO": "INTEGER",
    "NM_MUNICIPIO": "VARCHAR",
    "NR_ZONA": "INTEGER",
    "QT_APTOS": "BIGINT",
    "QT_COMPARECIMENTO": "BIGINT",
    "QT_ABSTENCOES": "BIGINT",
    "QT_ELEITORES_SECOES_NAO_INSTALADAS": "BIGINT",
    "QT_TOTAL_VOTOS_VALIDOS": "BIGINT",
    "QT_VOTOS_NOMINAIS_VALIDOS": "BIGINT",
    "QT_VOTOS_BRANCOS": "BIGINT",
    "QT_TOTAL_VOTOS_NULOS": "BIGINT",
}


DEPUTADO_FEDERAL = 6

CANDIDATO = {
    "ANO_ELEICAO": "SMALLINT",
    "SG_UF": "VARCHAR",
    "CD_CARGO": "TINYINT",
    "SQ_CANDIDATO": "BIGINT",
    "NR_CANDIDATO": "INTEGER",
    "NM_URNA_CANDIDATO": "VARCHAR",
    "SG_PARTIDO": "VARCHAR",
    "DS_SITUACAO_CANDIDATURA": "VARCHAR",
    "CD_OCUPACAO": "INTEGER",
    "DS_OCUPACAO": "VARCHAR",
    "DS_SIT_TOT_TURNO": "VARCHAR",
}

VOTACAO_CANDIDATO = {
    "ANO_ELEICAO": "SMALLINT",
    "NR_TURNO": "TINYINT",
    "SG_UF": "VARCHAR",
    "CD_MUNICIPIO": "INTEGER",
    "NR_ZONA": "INTEGER",
    "CD_CARGO": "TINYINT",
    "SQ_CANDIDATO": "BIGINT",
    "NM_URNA_CANDIDATO": "VARCHAR",
    "SG_PARTIDO": "VARCHAR",
    "DS_SITUACAO_CANDIDATURA": "VARCHAR",
    "DS_DETALHE_SITUACAO_CAND": "VARCHAR",
    "QT_VOTOS_NOMINAIS": "BIGINT",
}

DETALHE_CARGO = {
    "ANO_ELEICAO": "SMALLINT",
    "NR_TURNO": "TINYINT",
    "SG_UF": "VARCHAR",
    "CD_MUNICIPIO": "INTEGER",
    "NR_ZONA": "INTEGER",
    "CD_CARGO": "TINYINT",
    "QT_TOTAL_VOTOS_VALIDOS": "BIGINT",
    "QT_VOTOS_NOMINAIS_VALIDOS": "BIGINT",
    "QT_TOTAL_VOTOS_LEG_VALIDOS": "BIGINT",
}


def converte_deputados(ano: int) -> None:
    """Converte candidatos, votos por candidato e detalhe por município×zona (deputado federal)."""
    raw, interim = paths.RAW / "tse", paths.INTERIM / "tse"
    filtro = f"CD_CARGO = '{DEPUTADO_FEDERAL}'"
    csv_zip_para_parquet(
        raw / "consulta_cand" / f"consulta_cand_{ano}.zip",
        membro=f"consulta_cand_{ano}_BRASIL.csv",
        destino=interim / "candidatos" / f"ano={ano}" / "data.parquet",
        colunas=CANDIDATO,
        filtro=filtro,
    )
    # Até 2014 os votos nominais anulados já vêm zerados; a partir de 2018 o TSE separa
    # QT_VOTOS_NOMINAIS (todos) de QT_VOTOS_NOMINAIS_VALIDOS (em 2022 diferem em ~1 milhão).
    validos = {"QT_VOTOS_NOMINAIS_VALIDOS": "BIGINT"} if ano >= 2018 else {}
    csv_zip_para_parquet(
        raw / "votacao_candidato_munzona" / f"votacao_candidato_munzona_{ano}.zip",
        membro=f"votacao_candidato_munzona_{ano}_BRASIL.csv",
        destino=interim / "votacao_deputado" / f"ano={ano}" / "data.parquet",
        colunas=VOTACAO_CANDIDATO | validos,
        filtro=filtro,
    )
    csv_zip_para_parquet(
        raw / "detalhe_votacao_munzona" / f"detalhe_votacao_munzona_{ano}.zip",
        membro=f"detalhe_votacao_munzona_{ano}_BRASIL.csv",  # o _BR só tem presidente
        destino=interim / "detalhe_deputado" / f"ano={ano}" / "data.parquet",
        colunas=DETALHE_CARGO,
        filtro=filtro,
    )


def converte_ano(ano: int) -> None:
    """Converte votação por seção e detalhe por município×zona (presidente) de um ano."""
    raw, interim = paths.RAW / "tse", paths.INTERIM / "tse"
    csv_zip_para_parquet(
        raw / "votacao_secao" / f"votacao_secao_{ano}_BR.zip",
        membro=f"votacao_secao_{ano}_BR.csv",
        destino=interim / "votacao_secao" / f"ano={ano}" / "data.parquet",
        colunas=SECAO,
        filtro="CD_CARGO = '1'",
    )
    csv_zip_para_parquet(
        raw / "detalhe_votacao_munzona" / f"detalhe_votacao_munzona_{ano}.zip",
        membro=f"detalhe_votacao_munzona_{ano}_BR.csv",
        destino=interim / "detalhe_munzona" / f"ano={ano}" / "data.parquet",
        colunas=DETALHE,
        filtro="CD_CARGO = '1'",
    )


if __name__ == "__main__":
    import sys

    # python -m kingsrace.ingest.tse 2022  |  python -m kingsrace.ingest.tse deputados 2022
    if sys.argv[1] == "deputados":
        converte_deputados(int(sys.argv[2]))
    else:
        converte_ano(int(sys.argv[1]))
