"""Painel municipal de votação presidencial: contagens, papéis dos candidatos e métricas."""

import polars as pl

from kingsrace import paths

BRANCO, NULO, ANULADO_EM_SEPARADO = 95, 96, 97  # 97: seções anuladas pela Justiça Eleitoral

# aptos = comparecimento + abstencoes + eleitores_nao_instalados (resíduo; ver completa_turnout)
# comparecimento = validos + brancos + nulos (resíduo: inclui anulados e apurados em separado)
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


def remapeia_transito(df, mapa: pl.DataFrame):
    """Atribui à capital os votos da pseudo-UF "VT" (voto em trânsito com código próprio, 2010).

    A partir de 2018 o TSE já conta o voto em trânsito no município onde ele é dado; isto
    deixa 2010 consistente com os demais anos. Funciona em DataFrame ou LazyFrame com
    colunas `uf` e `cd_tse`; mapa: cd_tse_vt, uf, cd_tse_capital (data/reference).
    """
    m = mapa.select(
        pl.col("cd_tse_vt").cast(pl.Int32),
        pl.col("uf").alias("_uf_capital"),
        pl.col("cd_tse_capital").cast(pl.Int32).alias("_cd_capital"),
    )
    if isinstance(df, pl.LazyFrame):
        m = m.lazy()
    return (
        df.with_columns(pl.col("cd_tse").cast(pl.Int32))
        .join(m, left_on="cd_tse", right_on="cd_tse_vt", how="left", maintain_order="left")
        .with_columns(
            pl.coalesce("_uf_capital", "uf").alias("uf"),
            pl.coalesce("_cd_capital", "cd_tse").alias("cd_tse"),
        )
        .drop("_uf_capital", "_cd_capital")
    )


def completa_turnout(detalhe):
    """Define `nulos` e `eleitores_nao_instalados` pelos resíduos das contagens do TSE.

    O sentido das colunas de nulos do TSE muda entre anos (em 2006 há duas colunas que
    diferem; em 2010 e 2018 parte dos votos está em "anulados e apurados em separado"; em
    2026 os votos anulados de candidato entram no "total de nulos"). Os resíduos fecham sempre:
    nulos = comparecimento − válidos − brancos (todo voto não válido e não branco);
    eleitores_nao_instalados = aptos − comparecimento − abstenções.
    """
    return detalhe.with_columns(
        nulos=pl.col("comparecimento") - pl.col("validos") - pl.col("brancos"),
        eleitores_nao_instalados=pl.col("aptos") - pl.col("comparecimento") - pl.col("abstencoes"),
    )


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
        .when(pl.col("nr_votavel") == ANULADO_EM_SEPARADO)
        .then(pl.lit("anulado"))
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
    detalhe = (
        pl.read_parquet(interim / "detalhe_munzona" / "*" / "*.parquet")
        .select(
            pl.col("ano_eleicao").cast(pl.Int16).alias("ano"),
            pl.col("nr_turno").alias("turno"),
            pl.col("sg_uf").alias("uf"),
            pl.col("cd_municipio").alias("cd_tse"),
            pl.col("qt_aptos").alias("aptos"),
            pl.col("qt_comparecimento").alias("comparecimento"),
            pl.col("qt_abstencoes").alias("abstencoes"),
            pl.col("qt_total_votos_validos").alias("validos"),
            pl.col("qt_votos_brancos").alias("brancos"),
        )
        .pipe(completa_turnout)
    )
    transito = pl.read_csv(paths.REFERENCE / "voto_transito_2010.csv")
    secao, detalhe = remapeia_transito(secao, transito), remapeia_transito(detalhe, transito)
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
