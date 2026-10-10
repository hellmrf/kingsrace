"""Homicídios por município de residência e ano (SIM/DATASUS; medida E5).

Arquivos brutos em data/raw/datasus/sim/DOBR<ano>.dbc, baixados do FTP do DATASUS
(ftp://ftp.datasus.gov.br/dissemin/publicos/SIM/CID10/DORES/; 2025 de PRELIM/DORES, ainda
preliminar; URLs em data/reference/fontes_ftp.csv). Homicídio = agressões (CID-10 X85–Y09)
+ intervenções legais (Y35–Y36), pela causa básica, como no Atlas da Violência.
"""

import re
import struct
import tempfile
from pathlib import Path

import numpy as np
import polars as pl
from pyreaddbc import dbc2dbf

from kingsrace import paths

HOMICIDIO = r"^(X8[5-9]|X9\d|Y0\d|Y3[56])"


def le_dbf(caminho: Path, campos: list[str]) -> pl.DataFrame:
    """Lê `campos` de um DBF (registros de largura fixa) como texto, sem os excluídos."""
    dados = Path(caminho).read_bytes()
    n, cabecalho, largura = struct.unpack("<IHH", dados[4:12])
    posicoes, pos = {}, 1  # o 1º byte de cada registro marca exclusão ("*")
    for i in range(32, cabecalho - 1, 32):
        if dados[i] == 0x0D:
            break
        nome = dados[i : i + 11].split(b"\0")[0].decode()
        tamanho = dados[i + 16]
        posicoes[nome] = (pos, tamanho)
        pos += tamanho
    registros = np.frombuffer(dados, np.uint8, n * largura, cabecalho).reshape(n, largura)
    validos = registros[:, 0] != ord("*")
    colunas = {}
    for c in campos:
        ini, tam = posicoes[c]
        bruto = np.ascontiguousarray(registros[validos, ini : ini + tam]).view(f"S{tam}")[:, 0]
        colunas[c] = pl.Series(c, bruto).cast(pl.Binary).cast(pl.String).str.strip_chars()
    return pl.DataFrame(colunas)


def conta_homicidios(obitos: pl.DataFrame, ano: int) -> pl.DataFrame:
    """Homicídios por município de residência (código IBGE de 6 dígitos).

    Até 2005 o SIM grava o código com 7 dígitos (com o verificador); depois, com 6.
    """
    codigo = pl.col("CODMUNRES").str.strip_chars()
    seis = pl.when(codigo.str.len_chars() == 7).then(codigo.str.slice(0, 6)).otherwise(codigo)
    return (
        obitos.filter(pl.col("CAUSABAS").str.strip_chars().str.contains(HOMICIDIO))
        .group_by(cd_ibge6=seis.cast(pl.Int32, strict=False))
        .agg(homicidios=pl.len())
        .with_columns(ano=pl.lit(ano, pl.Int32))
    )


def converte() -> None:
    saida = paths.INTERIM / "sim"
    saida.mkdir(parents=True, exist_ok=True)
    partes = []
    for arq in sorted((paths.RAW / "datasus" / "sim").glob("DOBR*.dbc")):
        ano = int(re.search(r"(\d{4})", arq.name).group(1))
        with tempfile.TemporaryDirectory(dir=saida) as tmp:
            dbf = Path(tmp) / f"{arq.stem}.dbf"
            dbc2dbf(str(arq), str(dbf))
            obitos = le_dbf(dbf, ["CAUSABAS", "CODMUNRES"])
        partes.append(conta_homicidios(obitos, ano))
    pl.concat(partes).sort("cd_ibge6", "ano").write_parquet(saida / "homicidios.parquet")


if __name__ == "__main__":
    converte()
