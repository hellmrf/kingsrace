"""Painel municipal de votação presidencial: contagens, papéis dos candidatos e métricas."""

import polars as pl

from kingsrace import paths

BRANCO, NULO = 95, 96

# aptos = comparecimento + abstencoes + eleitores_nao_instalados (seções não instaladas)
# comparecimento = validos + brancos + nulos (nulos inclui votos anulados)
TURNOUT = [
    "aptos",
    "comparecimento",
    "abstencoes",
    "eleitores_nao_instalados",
    "validos",
    "brancos",
    "nulos",
]
CONTAGENS = [*TURNOUT, "votos_pt", "votos_adv", "votos_outros"]


def classifica_votos(votos: pl.DataFrame, candidatos: pl.DataFrame) -> pl.DataFrame:
    """Acrescenta `papel` (pt, adversario, anulado, branco, nulo, outro) por ano e número."""
    return votos.join(
        candidatos.select("ano", "nr_votavel", "papel"), on=["ano", "nr_votavel"], how="left"
    ).with_columns(
        pl.when(pl.col("papel").is_not_null())
        .then(pl.col("papel"))
        .when(pl.col("nr_votavel") == BRANCO)
        .then(pl.lit("branco"))
        .when(pl.col("nr_votavel") == NULO)
        .then(pl.lit("nulo"))
        .otherwise(pl.lit("outro"))
        .alias("papel")
    )


def adiciona_metricas(df: pl.DataFrame) -> pl.DataFrame:
    pt, adv = pl.col("votos_pt"), pl.col("votos_adv")
    pt_2p = pt / (pt + adv)
    return df.with_columns(
        pt_validos=pt / pl.col("validos"),
        adv_validos=adv / pl.col("validos"),
        pt_2p=pt_2p,
        pt_2p_logit=(pt_2p / (1 - pt_2p)).log(),
        pt_aptos=pt / pl.col("aptos"),
        abstencao=pl.col("abstencoes") / pl.col("aptos"),
    )


def monta_painel(
    votos: pl.DataFrame, detalhe: pl.DataFrame, municipios: pl.DataFrame
) -> pl.DataFrame:
    """Uma linha por município IBGE × ano × turno; exclui o exterior.

    votos: ano, turno, uf, cd_tse, nr_votavel, votos, papel (seção ou zona).
    detalhe: ano, turno, uf, cd_tse + colunas de TURNOUT (por zona).
    Falha se pt + adversário + outros ≠ válidos.
    """
    chave = ["ano", "turno", "cd_tse"]
    por_papel = (
        votos.filter(pl.col("uf") != "ZZ")
        .group_by(chave)
        .agg(
            (pl.col("votos").filter(pl.col("papel") == p).sum().alias(f"votos_{c}"))
            for p, c in [("pt", "pt"), ("adversario", "adv"), ("outro", "outros")]
        )
    )
    turnout = (
        detalhe.filter(pl.col("uf") != "ZZ")
        .group_by([*chave, "uf"])
        .agg(pl.col(c).sum() for c in TURNOUT)
    )
    painel = (
        turnout.join(por_papel, on=chave, how="left")
        .with_columns(pl.col("votos_pt", "votos_adv", "votos_outros").fill_null(0))
        .join(municipios.select("cd_tse", "cd_ibge"), on="cd_tse")
    )

    soma = pl.col("votos_pt") + pl.col("votos_adv") + pl.col("votos_outros")
    divergentes = painel.filter(soma != pl.col("validos"))
    if divergentes.height:
        exemplos = divergentes.select("cd_ibge", "ano", "turno").head(10).rows()
        raise ValueError(
            f"{divergentes.height} municípios com pt + adv + outros ≠ válidos "
            f"(algum voto anulado faltando em candidatos.csv?): {exemplos}"
        )

    return adiciona_metricas(painel.select("cd_ibge", "ano", "turno", "uf", *CONTAGENS))


def agrega_amc(painel: pl.DataFrame, municipios: pl.DataFrame) -> pl.DataFrame:
    """Soma as contagens por área mínima comparável e recalcula as métricas."""
    return adiciona_metricas(
        painel.join(municipios.select("cd_ibge", "amc_id"), on="cd_ibge")
        .group_by("amc_id", "ano", "turno")
        .agg(pl.col("uf").first(), *(pl.col(c).sum() for c in CONTAGENS))
        .sort("amc_id", "ano", "turno")
    )


def votos_por_municipio(secao: pl.LazyFrame, candidatos: pl.DataFrame) -> pl.DataFrame:
    """Agrega a votação por seção em município × candidato, com papel (inclui exterior)."""
    votos = (
        secao.group_by("ano", "turno", "uf", "cd_tse", "nr_votavel", "nm_votavel")
        .agg(pl.col("votos").sum())
        .collect()
    )
    return classifica_votos(votos, candidatos).sort("ano", "turno", "uf", "cd_tse", "nr_votavel")


def executa() -> None:
    interim = paths.INTERIM / "tse"
    secao = pl.scan_parquet(interim / "votacao_secao" / "*" / "*.parquet").select(
        pl.col("ano_eleicao").cast(pl.Int16).alias("ano"),
        pl.col("nr_turno").alias("turno"),
        pl.col("sg_uf").alias("uf"),
        pl.col("cd_municipio").alias("cd_tse"),
        "nr_votavel",
        "nm_votavel",
        pl.col("qt_votos").alias("votos"),
    )
    detalhe = pl.read_parquet(interim / "detalhe_munzona" / "*" / "*.parquet").select(
        pl.col("ano_eleicao").cast(pl.Int16).alias("ano"),
        pl.col("nr_turno").alias("turno"),
        pl.col("sg_uf").alias("uf"),
        pl.col("cd_municipio").alias("cd_tse"),
        pl.col("qt_aptos").alias("aptos"),
        pl.col("qt_comparecimento").alias("comparecimento"),
        pl.col("qt_abstencoes").alias("abstencoes"),
        pl.col("qt_eleitores_secoes_nao_instaladas").alias("eleitores_nao_instalados"),
        pl.col("qt_total_votos_validos").alias("validos"),
        pl.col("qt_votos_brancos").alias("brancos"),
        pl.col("qt_total_votos_nulos").alias("nulos"),
    )
    candidatos = pl.read_csv(paths.REFERENCE / "candidatos.csv").with_columns(
        pl.col("ano").cast(pl.Int16)
    )
    municipios = pl.read_parquet(paths.PROCESSED / "municipios.parquet")

    votos = votos_por_municipio(secao, candidatos).join(
        municipios.select("cd_tse", "cd_ibge"), on="cd_tse", how="left"
    )
    painel = monta_painel(votos, detalhe, municipios).sort("cd_ibge", "ano", "turno")

    votos.write_parquet(paths.PROCESSED / "votos_municipio.parquet")
    painel.write_parquet(paths.PROCESSED / "painel_municipio.parquet")
    agrega_amc(painel, municipios).write_parquet(paths.PROCESSED / "painel_amc.parquet")


if __name__ == "__main__":
    executa()
