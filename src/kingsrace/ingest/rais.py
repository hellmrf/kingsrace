"""Emprego formal por município (RAIS, arquivo de estabelecimentos; medidas E4a e E4b).

Arquivos brutos em data/raw/rais/estab_<ano>.{7z,zip}, baixados do FTP do PDET
(ftp://ftp.mtps.gov.br/pdet/microdados/RAIS/<ano>/; URLs em data/reference/fontes_ftp.csv).
Um texto por arquivo, `;`, latin-1, com cabeçalho. Vínculos ativos em 31/12, somados por
município (código IBGE de 6 dígitos), no total e nos setores ligados à Lava Jato.
"""

import tempfile
import zipfile
from pathlib import Path

import duckdb
import polars as pl
import py7zr

from kingsrace import paths

ANOS = [2006, 2009, 2010, 2013, 2014, 2017, 2018, 2021, 2022, 2025]
# CNAE 2.0 (prefixo da subclasse): extração de petróleo e gás (06), apoio à extração de
# petróleo e gás (09.1), derivados de petróleo (19), construção de embarcações (30.1) e obras
# de infraestrutura (42) — registro da E4b em docs/hipoteses.md
LAVA_JATO = ("06", "091", "19", "301", "42")


def extrai(arquivo: Path, destino: Path) -> Path:
    if arquivo.suffix == ".7z":
        with py7zr.SevenZipFile(arquivo) as z:
            (nome,) = z.getnames()
            z.extractall(destino)
    else:
        with zipfile.ZipFile(arquivo) as z:
            (nome,) = z.namelist()
            z.extract(nome, destino)
    return destino / nome


def colunas(texto: Path) -> tuple[str, dict[str, str]]:
    """Separador e nomes das colunas usadas, achadas pelo prefixo.

    O layout muda: até 2017, `;` e "Município"; a partir de 2018, `,`, aspas e "Município -
    Código", "CNAE 2.0 Subclasse - Codigo".
    """
    with open(texto, encoding="latin-1") as f:
        cabecalho = f.readline()
    sep = ";" if cabecalho.count(";") > cabecalho.count(",") else ","
    nomes = [n.strip().strip('"') for n in cabecalho.split(sep)]
    achadas = {}
    for chave, prefixo in [
        ("municipio", "Município"),
        ("vinculos", "Qtd Vínculos Ativos"),
        ("subclasse", "CNAE 2.0 Subclasse"),
    ]:
        (achadas[chave],) = (n for n in nomes if n.startswith(prefixo))
    return sep, achadas


def emprego_municipio(texto: Path, ano: int) -> duckdb.DuckDBPyRelation:
    """Vínculos ativos por município, no total e nos setores da Lava Jato."""
    sep, c = colunas(texto)
    vinculos = f'try_cast(trim("{c["vinculos"]}") AS BIGINT)'
    subclasse = f'trim("{c["subclasse"]}")'
    lava_jato = " OR ".join(f"starts_with({subclasse}, '{p}')" for p in LAVA_JATO)
    return duckdb.sql(f"""
        SELECT try_cast(trim("{c["municipio"]}") AS INTEGER) AS cd_ibge6,
               {ano} AS ano,
               sum({vinculos})::BIGINT AS vinculos,
               sum(CASE WHEN {lava_jato} THEN {vinculos} ELSE 0 END)::BIGINT
                   AS vinculos_lava_jato
        FROM read_csv('{texto}', delim='{sep}', quote='"', header=true, encoding='latin-1',
                      all_varchar=true, strict_mode=false)
        GROUP BY ALL
    """)


def converte() -> None:
    saida = paths.INTERIM / "rais"
    saida.mkdir(parents=True, exist_ok=True)
    partes = []
    with tempfile.TemporaryDirectory(dir=saida) as tmp:
        for ano in ANOS:
            (arquivo,) = (
                a for a in (paths.RAW / "rais").glob(f"estab_{ano}.*") if a.suffix != ".dvc"
            )
            texto = extrai(arquivo, Path(tmp))
            partes.append(emprego_municipio(texto, ano).pl())
            texto.unlink()
    pl.concat(partes).sort("cd_ibge6", "ano").write_parquet(saida / "emprego.parquet")


if __name__ == "__main__":
    converte()
