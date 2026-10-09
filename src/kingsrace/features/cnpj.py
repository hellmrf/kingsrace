"""Igrejas (E2b) e MEIs (E7a) por AMC e ano, a partir do CNPJ (ingest/receita.py).

- Igrejas: estabelecimentos com CNAE 9491-0/00 ativos em 31/12 de cada ano (início até a
  data e sem baixa, nulidade ou inaptidão até ela), classificados pela razão social com a
  lista de data/reference/denominacoes.csv (primeira regra que casar, na ordem de prioridade).
- MEIs: estoque em 31/12 de cada ano, já calculado na ingestão.
- Por habitante: população do Censo 2022 em todos os anos (a única disponível no projeto).
"""

import polars as pl

from kingsrace import paths
from kingsrace.harmonize.municipios import casa_municipios, le_ibge

ANOS = range(2006, 2027)


def normaliza(col: str) -> pl.Expr:
    """Maiúsculas, sem acentos, espaços simples."""
    return (
        pl.col(col)
        .fill_null("")
        .str.normalize("NFKD")
        .str.replace_all(r"\p{Mn}", "")
        .str.to_uppercase()
        .str.replace_all(r"\s+", " ")
        .str.strip_chars()
    )


def classifica(
    df: pl.DataFrame, regras: pl.DataFrame, coluna: str = "razao_social"
) -> pl.DataFrame:
    """Acrescenta `grupo` e `denominacao` pela primeira regra que casar (ou "indefinida")."""
    nome = normaliza(coluna)
    ordenadas = regras.with_row_index("_linha").sort("prioridade", "_linha")
    grupo = denominacao = None
    for r in reversed(list(ordenadas.iter_rows(named=True))):
        casa = nome.str.contains(r["padrao"])
        grupo = (
            pl.when(casa)
            .then(pl.lit(r["grupo"]))
            .otherwise(grupo if grupo is not None else pl.lit("indefinida"))
        )
        denominacao = (
            pl.when(casa)
            .then(pl.lit(r["denominacao"]))
            .otherwise(denominacao if denominacao is not None else pl.lit("Indefinida"))
        )
    return df.with_columns(grupo=grupo, denominacao=denominacao)


def ativas_em(df: pl.DataFrame, anos=ANOS) -> pl.DataFrame:
    """Uma linha por estabelecimento × ano em que estava ativo em 31/12."""
    datas = pl.DataFrame({"ano": list(anos)}).with_columns(data=pl.date(pl.col("ano"), 12, 31))
    return (
        df.join(datas, how="cross")
        .filter(
            (pl.col("data_inicio") <= pl.col("data"))
            & (pl.col("data_fim").is_null() | (pl.col("data_fim") > pl.col("data")))
        )
        .drop("data")
    )


def mapa_receita(mun_receita: pl.DataFrame, ibge: pl.DataFrame, overrides: pl.DataFrame):
    """Código de município da Receita → cd_ibge (exterior e códigos sem UF ficam de fora)."""
    fonte = mun_receita.filter(pl.col("uf").is_not_null() & (pl.col("uf") != "EX")).select(
        pl.col("municipio").cast(pl.Int32).alias("cd_receita"), "uf", "nome"
    )
    return casa_municipios(fonte, ibge, overrides, codigo="cd_receita")


def por_amc(df: pl.DataFrame, mapa: pl.DataFrame, municipios: pl.DataFrame) -> pl.DataFrame:
    """Junta `amc_id` pelo município da Receita; falha se algum código ficar sem par."""
    df = df.with_columns(pl.col("municipio").cast(pl.Int32).alias("cd_receita"))
    sem_par = df.join(mapa, on="cd_receita", how="anti").filter(pl.col("uf") != "EX")
    if sem_par.height:
        codigos = sem_par["cd_receita"].unique().sort().to_list()
        raise ValueError(f"municípios da Receita sem correspondência: {codigos[:20]}")
    return df.join(mapa, on="cd_receita").join(municipios.select("cd_ibge", "amc_id"), on="cd_ibge")


def executa() -> None:
    interim = paths.INTERIM / "receita"
    municipios = pl.read_parquet(paths.PROCESSED / "municipios.parquet")
    ibge = le_ibge(paths.RAW / "ibge" / "municipios.json").select("cd_ibge", "uf", "nome")
    mapa = mapa_receita(
        pl.read_parquet(interim / "municipios_receita.parquet"),
        ibge,
        pl.read_csv(paths.REFERENCE / "municipios_overrides_receita.csv"),
    )
    populacao = pl.read_parquet(paths.PROCESSED / "covariaveis_amc.parquet").select(
        "amc_id", "populacao"
    )

    regras = pl.read_csv(paths.REFERENCE / "denominacoes.csv")
    religiosas = classifica(pl.read_parquet(interim / "religiosas.parquet"), regras)
    ativas = por_amc(ativas_em(religiosas), mapa, municipios)
    ativas.group_by("amc_id", "ano", "grupo", "denominacao").len("igrejas").sort(
        "amc_id", "ano", "denominacao"
    ).write_parquet(paths.PROCESSED / "igrejas_denominacao_amc.parquet")

    igrejas = ativas.group_by("amc_id", "ano").agg(
        igrejas=pl.len(),
        igrejas_evangelicas=(pl.col("grupo") == "evangelica").sum(),
    )
    meis = (
        por_amc(pl.read_parquet(interim / "mei_estoque.parquet"), mapa, municipios)
        .group_by("amc_id", "ano")
        .agg(pl.col("meis").sum())
    )
    grade = (
        municipios.select("amc_id")
        .unique()
        .join(pl.DataFrame({"ano": list(ANOS)}, schema={"ano": pl.Int32}), how="cross")
    )
    (
        grade.join(igrejas.cast({"ano": pl.Int32}), on=["amc_id", "ano"], how="left")
        .join(meis.cast({"ano": pl.Int32}), on=["amc_id", "ano"], how="left")
        .with_columns(pl.col("igrejas", "igrejas_evangelicas", "meis").fill_null(0))
        .join(populacao, on="amc_id", how="left")
        .with_columns(
            evangelicas_10mil=1e4 * pl.col("igrejas_evangelicas") / pl.col("populacao"),
            meis_100hab=100 * pl.col("meis") / pl.col("populacao"),
        )
        .drop("populacao")
        .sort("amc_id", "ano")
        .write_parquet(paths.PROCESSED / "cnpj_amc.parquet")
    )


if __name__ == "__main__":
    executa()
