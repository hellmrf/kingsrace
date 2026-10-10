"""Centro eleitoral de cada município e de cada AMC: a média das coordenadas dos locais de
votação de 2026, ponderada pelos eleitores aptos de cada local. Serve aos mapas de pontos
(um ponto por município, onde os eleitores estão, e não o centro geométrico do território).

Uso: python -m kingsrace.features.coordenadas
"""

import polars as pl

from kingsrace import paths


def centros(locais: pl.DataFrame, chave: str) -> pl.DataFrame:
    """Média ponderada de lat/lon por `chave`, só com locais que têm coordenadas."""
    com = locais.filter(
        pl.col("lat").is_not_null() & pl.col("lon").is_not_null() & (pl.col("aptos") > 0)
    )
    return (
        com.group_by(chave)
        .agg(
            lat=(pl.col("lat") * pl.col("aptos")).sum() / pl.col("aptos").sum(),
            lon=(pl.col("lon") * pl.col("aptos")).sum() / pl.col("aptos").sum(),
            locais_com_coordenada=pl.len(),
        )
        .sort(chave)
    )


def executa() -> None:
    locais = pl.read_parquet(paths.PROCESSED / "painel_local.parquet").filter(
        (pl.col("ano") == 2026) & (pl.col("turno") == 1)
    )
    centros(locais, "cd_ibge").write_parquet(paths.PROCESSED / "coordenadas_municipio.parquet")
    centros(locais, "amc_id").write_parquet(paths.PROCESSED / "coordenadas_amc.parquet")


if __name__ == "__main__":
    executa()
