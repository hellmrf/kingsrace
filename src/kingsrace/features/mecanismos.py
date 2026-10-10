"""Medidas X da série E, como registradas em docs/hipoteses.md ("Série E").

Cada função devolve `amc_id`, `x` e, quando a medida muda com a transição, `de` (ano do
pleito inicial da transição a que se aplica), no formato de `models/event_study.py`.
"""

import polars as pl

from kingsrace import paths

# transição (ano do pleito inicial) → janela da medida
JANELA_EMPREGO = {
    2006: (2006, 2009),
    2010: (2010, 2013),
    2014: (2014, 2017),
    2018: (2018, 2021),
    2022: (2022, 2025),
}
JANELA_MEI = {2010: (2010, 2013), 2014: (2014, 2017), 2018: (2018, 2021), 2022: (2022, 2025)}
# triênios de homicídios (antes → depois) e o ano do meio de cada um (população estimada)
TRIENIOS = {
    2006: ((2003, 2005), (2007, 2009)),
    2010: ((2007, 2009), (2011, 2013)),
    2014: ((2011, 2013), (2015, 2017)),
    2018: ((2015, 2017), (2019, 2021)),
    2022: ((2019, 2021), (2023, 2025)),
}


def por_amc_ibge6(df: pl.DataFrame, municipios: pl.DataFrame, valores: list[str]) -> pl.DataFrame:
    """Soma `valores` por AMC × ano a partir do código IBGE de 6 dígitos.

    Códigos sem município (ex.: "município ignorado", terminados em 0000) ficam de fora.
    """
    mapa = municipios.select((pl.col("cd_ibge") // 10).cast(pl.Int32).alias("cd_ibge6"), "amc_id")
    return (
        df.join(mapa, on="cd_ibge6")
        .group_by("amc_id", "ano")
        .agg(pl.col(valores).sum())
        .sort("amc_id", "ano")
    )


def e4a_emprego(emprego: pl.DataFrame) -> pl.DataFrame:
    """Δ log do emprego formal na janela de cada transição."""
    v = emprego.pivot(on="ano", index="amc_id", values="vinculos")
    return pl.concat(
        v.select("amc_id", de=pl.lit(de), x=pl.col(str(a1)).log() - pl.col(str(a0)).log())
        for de, (a0, a1) in JANELA_EMPREGO.items()
    ).filter(pl.col("x").is_finite())


def e4b_lava_jato(emprego: pl.DataFrame) -> pl.DataFrame:
    """% do emprego formal de 2013 nos setores ligados à Lava Jato."""
    return emprego.filter(pl.col("ano") == 2013).select(
        "amc_id", x=100 * pl.col("vinculos_lava_jato") / pl.col("vinculos")
    )


def e5_homicidios(homicidios: pl.DataFrame, cov: pl.DataFrame) -> pl.DataFrame:
    """Δ da taxa de homicídios por 100 mil habitantes entre os triênios de cada transição.

    Taxa do triênio = homicídios dos três anos / (3 × população estimada no ano do meio).
    """

    def taxa(anos):
        a0, a1 = anos
        meio = (a0 + a1) // 2
        return (
            homicidios.filter(pl.col("ano").is_between(a0, a1))
            .group_by("amc_id")
            .agg(pl.col("homicidios").sum())
            .join(cov.select("amc_id", pop=pl.col(f"pop_{meio}")), on="amc_id", how="right")
            .with_columns(taxa=1e5 * pl.col("homicidios").fill_null(0) / (3 * pl.col("pop")))
            .select("amc_id", "taxa")
        )

    partes = []
    for de, (antes, depois) in TRIENIOS.items():
        partes.append(
            taxa(antes)
            .join(taxa(depois), on="amc_id", suffix="_depois")
            .select("amc_id", de=pl.lit(de), x=pl.col("taxa_depois") - pl.col("taxa"))
        )
    return pl.concat(partes).drop_nulls("x")


def e2b_estoque(cnpj: pl.DataFrame) -> pl.DataFrame:
    """Igrejas evangélicas ativas por 10 mil habitantes no ano do pleito inicial."""
    return cnpj.filter(pl.col("ano").is_in(list(JANELA_EMPREGO))).select(
        "amc_id", de=pl.col("ano"), x="evangelicas_10mil"
    )


def e2b_aberturas(cnpj: pl.DataFrame) -> pl.DataFrame:
    """Aberturas líquidas de igrejas evangélicas por 10 mil hab. na janela de cada transição."""
    return _variacao(cnpj, "evangelicas_10mil", JANELA_EMPREGO)


def e7a_mei(cnpj: pl.DataFrame) -> pl.DataFrame:
    """Aberturas líquidas de MEI por 100 habitantes na janela de cada transição."""
    return _variacao(cnpj, "meis_100hab", JANELA_MEI)


def _variacao(df: pl.DataFrame, coluna: str, janelas: dict) -> pl.DataFrame:
    largo = df.pivot(on="ano", index="amc_id", values=coluna)
    return pl.concat(
        largo.select("amc_id", de=pl.lit(de), x=pl.col(str(a1)) - pl.col(str(a0)))
        for de, (a0, a1) in janelas.items()
    )


def executa() -> None:
    municipios = pl.read_parquet(paths.PROCESSED / "municipios.parquet")
    por_amc_ibge6(
        pl.read_parquet(paths.INTERIM / "rais" / "emprego.parquet"),
        municipios,
        ["vinculos", "vinculos_lava_jato"],
    ).write_parquet(paths.PROCESSED / "emprego_amc.parquet")
    por_amc_ibge6(
        pl.read_parquet(paths.INTERIM / "sim" / "homicidios.parquet"), municipios, ["homicidios"]
    ).write_parquet(paths.PROCESSED / "homicidios_amc.parquet")


if __name__ == "__main__":
    executa()
