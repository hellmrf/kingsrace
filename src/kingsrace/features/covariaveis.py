"""Covariáveis municipais (Censo, PIB, PAM, Bolsa Família) por município e por AMC."""

import json

import polars as pl

from kingsrace import paths
from kingsrace.ingest.ibge import CONSULTAS, sidra_para_tabela
from kingsrace.ingest.mds import CONSULTAS as MDS
from kingsrace.ingest.mds import le_misocial

# colunas extensivas (contagens, áreas, valores): somadas na AMC; as demais são taxas,
# ponderadas pela população. As derivadas são recalculadas a partir das somas.
SOMAS = [
    "populacao",
    "area_km2",
    "pib_2021",
    "pib_2023",
    "va_2021",
    "va_agro_2021",
    "va_adm_2021",
    "area_soja_2021_ha",
    "area_soja_2025_ha",
    "familias_ab_2022",
    "valor_ab_2022",
    "familias_bf_2026",
    "pessoas_bf_2026",
    "valor_bf_2026",
    *(f"pop_{a}" for a in (2004, 2008, 2012, 2016, 2020, 2024)),
]


def deriva_covariaveis(df: pl.DataFrame) -> pl.DataFrame:
    """Covariáveis derivadas, calculadas só quando as colunas de origem existem.

    - PIB per capita (R$) e participações no valor adicionado (%); participação nula quando o
      VA total não é positivo (Cachoeira Dourada/GO em 2021: usina hidrelétrica na crise hídrica);
    - % preta + parda; crescimento evangélico 2010→2022 (pp);
    - soja em % do território (1 km² = 100 ha, logo ha/km² = %) e sua expansão 2021→2025;
    - famílias no Auxílio Brasil (2022) e no Bolsa Família (2026) por 100 habitantes.
    """
    cols = set(df.columns)
    novas = []
    for ano in ("2021", "2023"):
        if {f"pib_{ano}", "populacao"} <= cols:
            novas.append((1000 * pl.col(f"pib_{ano}") / pl.col("populacao")).alias(f"pib_pc_{ano}"))
        for setor in ("agro", "adm"):
            if {f"va_{setor}_{ano}", f"va_{ano}"} <= cols:
                va = pl.col(f"va_{ano}")
                novas.append(
                    pl.when(va > 0)
                    .then(100 * pl.col(f"va_{setor}_{ano}") / va)
                    .alias(f"pct_va_{setor}_{ano}")
                )
    if {"pct_preta", "pct_parda"} <= cols:
        novas.append((pl.col("pct_preta") + pl.col("pct_parda")).alias("pct_preta_parda"))
    if {"pct_evangelica", "pct_evangelica_2010"} <= cols:
        novas.append(
            (pl.col("pct_evangelica") - pl.col("pct_evangelica_2010")).alias("delta_evangelica")
        )
    if {"area_soja_2021_ha", "area_km2"} <= cols:
        novas.append(
            (pl.col("area_soja_2021_ha") / pl.col("area_km2")).alias("soja_2021_pct_territorio")
        )
    if {"area_soja_2021_ha", "area_soja_2025_ha", "area_km2"} <= cols:
        novas.append(
            (
                (pl.col("area_soja_2025_ha") - pl.col("area_soja_2021_ha")) / pl.col("area_km2")
            ).alias("exp_soja_pct_territorio")
        )
    for fam, ano in (("familias_ab", "2022"), ("familias_bf", "2026")):
        if {f"{fam}_{ano}", "populacao"} <= cols:
            novas.append(
                (100 * pl.col(f"{fam}_{ano}") / pl.col("populacao")).alias(f"{fam}_100hab_{ano}")
            )
    return df.with_columns(novas)


def agrega_covariaveis_amc(cov: pl.DataFrame, municipios: pl.DataFrame) -> pl.DataFrame:
    """Soma as colunas extensivas, pondera as taxas pela população e recalcula as derivadas.

    A ponderação é uma aproximação para taxas com denominadores diferentes (religião é sobre
    10+ anos, alfabetização sobre 15+), aceitável porque só agrupa municípios vizinhos.
    Município sem população (instalado depois do Censo) entra nas somas, não nos pesos.
    """
    extensivas = [c for c in SOMAS if c in cov.columns]
    taxas = [c for c in cov.columns if c not in {"cd_ibge", "densidade", *extensivas}]
    peso = pl.col("populacao")

    def ponderada(c):
        valido = pl.col(c).is_not_null() & peso.is_not_null()
        # sem nenhum valor válido no grupo, nulo (e não NaN de 0/0)
        return (
            pl.when(valido.any())
            .then((pl.col(c) * peso).filter(valido).sum() / peso.filter(valido).sum())
            .alias(c)
        )

    agregado = (
        cov.join(municipios.select("cd_ibge", "amc_id"), on="cd_ibge")
        .group_by("amc_id")
        .agg(*(pl.col(c).sum() for c in extensivas), *(ponderada(c) for c in taxas))
    )
    agregado = deriva_covariaveis(agregado)
    if "area_km2" in cov.columns:
        agregado = agregado.with_columns(
            (pl.col("populacao") / pl.col("area_km2")).alias("densidade")
        )
    return agregado


def executa() -> None:
    raw = paths.RAW / "ibge" / "sidra"
    tabelas = [
        sidra_para_tabela(json.loads((raw / f"{nome}.json").read_text("utf8")), colunas)
        for nome, (_, colunas) in CONSULTAS.items()
    ]
    municipios = pl.read_parquet(paths.PROCESSED / "municipios.parquet")
    tabelas += [
        le_misocial(paths.RAW / "mds" / arquivo, colunas, municipios["cd_ibge"])
        for arquivo, colunas in MDS.items()
    ]
    cov = municipios.select("cd_ibge")
    for t in tabelas:
        cov = cov.join(t, on="cd_ibge", how="left")
    # a PAM responde "..." (não disponível) para municípios sem nenhuma lavoura (capitais e
    # cidades urbanas como Recife, Natal, Belo Horizonte): sem lavoura, sem soja
    cov = cov.with_columns(pl.col("area_soja_2021_ha", "area_soja_2025_ha").fill_null(0.0))
    # área de soja maior que o território é erro da fonte (Mariópolis/PR em 2025: 45 mil ha
    # num território de 23 mil ha); vira ausente
    cov = cov.with_columns(
        pl.when(pl.col("area_km2").is_null() | (pl.col(c) <= 100 * pl.col("area_km2")))
        .then(pl.col(c))
        .alias(c)
        for c in ("area_soja_2021_ha", "area_soja_2025_ha")
    )
    cov = deriva_covariaveis(cov).sort("cd_ibge")
    cov.write_parquet(paths.PROCESSED / "covariaveis_municipio.parquet")
    agrega_covariaveis_amc(cov, municipios).sort("amc_id").write_parquet(
        paths.PROCESSED / "covariaveis_amc.parquet"
    )


if __name__ == "__main__":
    executa()
