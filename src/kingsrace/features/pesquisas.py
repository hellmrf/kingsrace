"""Pesquisas eleitorais de 2026: uma tabela para a G6 e para a B4 (docs/hipoteses.md).

- `pesquisas_serie_2025_2026.csv`: o 2º turno simulado Lula × Flávio, desde jun/2025. As
  pesquisas com fim de campo a partir de 05/10/2026 são as do 2º turno de verdade. Cada
  pesquisa nova entra aqui, numa linha.
- `pesquisas_2026.csv`: as últimas pesquisas de 1º turno de cada instituto, que dão o viés
  usado na correção.
- `institutos.csv`: nome de cada instituto → nome canônico. A correção casa os dois arquivos
  por ele.
"""

from datetime import date

import polars as pl

from kingsrace import paths

INICIO_2T = date(2026, 10, 5)  # fim de campo depois do 1º turno (04/10)


def canoniza(df: pl.DataFrame, institutos: pl.DataFrame) -> pl.DataFrame:
    """Troca `instituto` pelo nome canônico; falha se algum nome não estiver na tabela."""
    faltam = df.join(institutos, left_on="instituto", right_on="nome", how="anti")["instituto"]
    if faltam.len():
        raise ValueError(f"institutos sem nome canônico em institutos.csv: {sorted(set(faltam))}")
    return (
        df.join(institutos, left_on="instituto", right_on="nome", how="left", suffix="_canonico")
        .with_columns(pl.col("instituto_canonico").alias("instituto"))
        .drop("instituto_canonico")
    )


def segundo_turno(serie: pl.DataFrame, desde: date = INICIO_2T) -> pl.DataFrame:
    """Pesquisas do 2º turno (fim de campo ≥ `desde`), com s = Lula / (Lula + Flávio)."""
    return (
        serie.filter(pl.col("campo_fim") >= desde)
        .with_columns(
            turno=pl.lit(2, pl.Int64), s=pl.col("lula") / (pl.col("lula") + pl.col("flavio"))
        )
        .sort("campo_fim", "instituto")
    )


def para_previsao(
    primeiro: pl.DataFrame, serie: pl.DataFrame, institutos: pl.DataFrame
) -> pl.DataFrame:
    """Tabela no formato da B4: 1º turno de `pesquisas_2026.csv` + 2º turno da série."""
    colunas = ["instituto", "turno", "campo_inicio", "campo_fim", "lula", "flavio", "base", "fonte"]
    tipos = {"turno": pl.Int64, "lula": pl.Float64, "flavio": pl.Float64,
             "campo_inicio": pl.Date, "campo_fim": pl.Date}  # fmt: skip
    t1 = canoniza(primeiro.filter(pl.col("turno") == 1), institutos).select(colunas)
    t2 = canoniza(segundo_turno(serie), institutos).select(colunas)
    return pl.concat([t.cast(tipos) for t in (t1, t2)]).sort("turno", "campo_fim", "instituto")


def le() -> tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame]:
    """(pesquisas de 1º turno, série do 2º turno, institutos), com as datas lidas."""
    ref = paths.REFERENCE
    primeiro = pl.read_csv(ref / "pesquisas_2026.csv", try_parse_dates=True)
    serie = pl.read_csv(ref / "pesquisas_serie_2025_2026.csv", try_parse_dates=True)
    institutos = pl.read_csv(ref / "institutos.csv")
    return primeiro, serie, institutos
