"""Painel por seção e por local de votação (presidente; 2022 e 2026), para a série G.

Uma linha por seção × turno, com os votos dos finalistas e de cada grupo de eliminados
(`data/reference/grupos_terceiros.csv`) e as contagens do detalhe por seção. O painel por
local soma as seções e acrescenta, em 2026, bairro e coordenadas do cadastro de locais.
O exterior fica de fora, como no painel municipal.
"""

import unicodedata

import polars as pl

from kingsrace import paths
from kingsrace.features.painel import classifica_votos, completa_turnout

ANOS = (2022, 2026)
CHAVE_SECAO = ["ano", "turno", "uf", "cd_tse", "zona", "secao"]
CHAVE_LOCAL = ["ano", "turno", "uf", "cd_tse", "zona", "nr_local"]
TURNOUT = ["aptos", "comparecimento", "abstencoes", "eleitores_nao_instalados"]
VOTOS = ["validos", "brancos", "nulos", "votos_pt", "votos_adv", "votos_outros"]


def grupos_do_ano(grupos: pl.DataFrame) -> list[str]:
    """Nomes de grupo em ordem estável (a do arquivo), sem repetição."""
    return list(dict.fromkeys(grupos["grupo"].to_list()))


def votos_por_secao(
    votos: pl.DataFrame, candidatos: pl.DataFrame, grupos: pl.DataFrame
) -> pl.DataFrame:
    """Votos válidos de cada seção em colunas: `votos_pt`, `votos_adv`, `votos_<grupo>`.

    votos: CHAVE_SECAO + nr_votavel + votos. Brancos, nulos e anulados ficam de fora (vêm do
    detalhe). `votos_outros` soma todo válido que não é dos finalistas. Falha se algum
    candidato `outro` com votos não tiver grupo.
    """
    classificados = classifica_votos(votos, candidatos).filter(
        pl.col("papel").is_in(["pt", "adversario", "outro"])
    )
    com_grupo = classificados.join(
        grupos.select("ano", "nr_votavel", "grupo"), on=["ano", "nr_votavel"], how="left"
    )
    sem_grupo = com_grupo.filter(
        (pl.col("papel") == "outro") & pl.col("grupo").is_null() & (pl.col("votos") > 0)
    )
    if sem_grupo.height:
        faltam = sem_grupo.select("ano", "nr_votavel").unique().sort("ano", "nr_votavel").rows()
        raise ValueError(f"candidatos eliminados sem grupo em grupos_terceiros.csv: {faltam}")

    nomes = grupos_do_ano(grupos)
    papel, grupo = pl.col("papel"), pl.col("grupo")
    return com_grupo.group_by(CHAVE_SECAO).agg(
        pl.col("votos").filter(papel == "pt").sum().alias("votos_pt"),
        pl.col("votos").filter(papel == "adversario").sum().alias("votos_adv"),
        pl.col("votos").filter(papel == "outro").sum().alias("votos_outros"),
        *(pl.col("votos").filter(grupo == g).sum().alias(f"votos_{g}") for g in nomes),
    )


def monta_painel_secao(
    votos: pl.DataFrame, detalhe: pl.DataFrame, municipios: pl.DataFrame
) -> pl.DataFrame:
    """Junta votos e detalhe por seção; falha se pt + adv + outros ≠ válidos em alguma seção.

    detalhe: CHAVE_SECAO + nr_local, aptos, comparecimento, abstencoes, validos, brancos.
    Seções sem votos (não instaladas ou anuladas) ficam com votos zero.
    """
    colunas_votos = [c for c in votos.columns if c.startswith("votos_")]
    painel = (
        detalhe.filter(pl.col("uf") != "ZZ")
        .pipe(completa_turnout)
        .join(votos, on=CHAVE_SECAO, how="left")
        .with_columns(pl.col(colunas_votos).fill_null(0))
        .join(municipios.select("cd_tse", "cd_ibge", "amc_id"), on="cd_tse", how="left")
    )
    if painel["cd_ibge"].null_count():
        raise ValueError("seções sem município IBGE correspondente")
    soma = pl.col("votos_pt") + pl.col("votos_adv") + pl.col("votos_outros")
    divergentes = painel.filter(soma != pl.col("validos"))
    if divergentes.height:
        raise ValueError(f"{divergentes.height} seções com pt + adv + outros ≠ válidos")
    return painel.select(
        *CHAVE_SECAO,
        "cd_ibge",
        "amc_id",
        "nr_local",
        *TURNOUT,
        *VOTOS,
        *(c for c in colunas_votos if c not in VOTOS),
    ).sort(CHAVE_SECAO)


def normaliza_nome(col: str) -> pl.Expr:
    """Nome de local para comparação: sem acento, maiúsculo, só letras e dígitos."""
    return (
        pl.col(col)
        .map_elements(
            lambda s: "".join(
                c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)
            ),
            return_dtype=pl.String,
        )
        .str.to_uppercase()
        .str.replace_all(r"[^A-Z0-9]+", " ")
        .str.strip_chars()
    )


def coordenadas(locais: pl.DataFrame) -> pl.DataFrame:
    """Um registro por local (1º turno, seção principal), com lat/lon numéricas.

    O TSE grava as coordenadas com vírgula decimal; valores fora do Brasil viram nulos.
    """
    graus = {
        c: pl.col(f"nr_{c}").str.replace(",", ".").cast(pl.Float64, strict=False)
        for c in ("latitude", "longitude")
    }
    return (
        locais.filter((pl.col("nr_turno") == 1) & (pl.col("ds_tipo_secao_agregada") == "Principal"))
        .select(
            pl.col("sg_uf").alias("uf"),
            pl.col("cd_municipio").alias("cd_tse"),
            pl.col("nr_zona").alias("zona"),
            pl.col("nr_local_votacao").alias("nr_local"),
            pl.col("nm_bairro").alias("bairro"),
            pl.col("nr_cep").alias("cep"),
            pl.col("ds_tipo_local").alias("tipo_local"),
            lat=graus["latitude"],
            lon=graus["longitude"],
        )
        .with_columns(
            pl.when(pl.col("lat").is_between(-34, 6) & pl.col("lon").is_between(-74, -28))
            .then(pl.struct("lat", "lon"))
            .alias("_ok")
        )
        .with_columns(pl.col("_ok").struct.field("lat"), pl.col("_ok").struct.field("lon"))
        .drop("_ok")
        .unique(["uf", "cd_tse", "zona", "nr_local"], keep="first", maintain_order=True)
    )


def monta_painel_local(
    painel_secao: pl.DataFrame, nomes: pl.DataFrame, coords: pl.DataFrame
) -> pl.DataFrame:
    """Soma as seções por local de votação.

    nomes: CHAVE_LOCAL + nm_local, endereco (do detalhe por seção, um por local e turno).
    coords: uf, cd_tse, zona, nr_local + bairro, cep, tipo_local, lat, lon (só 2026).
    """
    contagens = [
        c for c in painel_secao.columns if c in TURNOUT or c in VOTOS or c.startswith("votos_")
    ]
    return (
        painel_secao.group_by(*CHAVE_LOCAL, "cd_ibge", "amc_id")
        .agg(pl.len().alias("secoes"), *(pl.col(c).sum() for c in contagens))
        .join(nomes, on=CHAVE_LOCAL, how="left")
        .join(
            coords.with_columns(ano=pl.lit(2026, pl.Int16)),
            on=["ano", "uf", "cd_tse", "zona", "nr_local"],
            how="left",
        )
        .sort(CHAVE_LOCAL)
    )


def casa_locais(de: pl.DataFrame, para: pl.DataFrame) -> pl.DataFrame:
    """Casa locais de dois pleitos por município, zona e número, exigindo o mesmo nome.

    de, para: cd_tse, zona, nr_local, nm_local (+ o que mais vier, com sufixos _de/_para).
    Devolve só os pares com nome normalizado igual; os números de local se repetem entre
    pleitos para escolas diferentes, e o nome é a garantia de que é o mesmo lugar.
    """
    chave = ["cd_tse", "zona", "nr_local"]
    a = de.with_columns(_nome=normaliza_nome("nm_local"))
    b = para.with_columns(_nome=normaliza_nome("nm_local"))
    return (
        a.join(b, on=chave, how="inner", suffix="_para")
        .filter(pl.col("_nome") == pl.col("_nome_para"))
        .drop("_nome", "_nome_para")
    )


def executa() -> None:
    interim = paths.INTERIM / "tse"
    anos = pl.col("ano_eleicao").is_in(ANOS)
    votos = (
        pl.scan_parquet(interim / "votacao_secao" / "*" / "*.parquet")
        .filter(anos)
        .select(
            pl.col("ano_eleicao").cast(pl.Int16).alias("ano"),
            pl.col("nr_turno").alias("turno"),
            pl.col("sg_uf").alias("uf"),
            pl.col("cd_municipio").alias("cd_tse"),
            pl.col("nr_zona").alias("zona"),
            pl.col("nr_secao").alias("secao"),
            "nr_votavel",
            pl.col("qt_votos").alias("votos"),
        )
        .collect()
    )
    detalhe_bruto = pl.read_parquet(interim / "detalhe_secao" / "*" / "*.parquet").rename(
        {
            "ano_eleicao": "ano",
            "nr_turno": "turno",
            "sg_uf": "uf",
            "cd_municipio": "cd_tse",
            "nr_zona": "zona",
            "nr_secao": "secao",
            "nr_local_votacao": "nr_local",
            "nm_local_votacao": "nm_local",
            "ds_local_votacao_endereco": "endereco",
        }
    )
    detalhe = detalhe_bruto.select(
        *CHAVE_SECAO,
        "nr_local",
        pl.col("qt_aptos").alias("aptos"),
        pl.col("qt_comparecimento").alias("comparecimento"),
        pl.col("qt_abstencoes").alias("abstencoes"),
        pl.col("qt_votos_brancos").alias("brancos"),
    )
    candidatos = pl.read_csv(paths.REFERENCE / "candidatos.csv").with_columns(
        pl.col("ano").cast(pl.Int16)
    )
    grupos = pl.read_csv(paths.REFERENCE / "grupos_terceiros.csv").with_columns(
        pl.col("ano").cast(pl.Int16)
    )
    municipios = pl.read_parquet(paths.PROCESSED / "municipios.parquet")

    por_secao = votos_por_secao(votos, candidatos, grupos)
    # válidos = votos de candidato não anulado (como no painel municipal)
    detalhe = detalhe.join(
        por_secao.select(
            *CHAVE_SECAO, validos=pl.col("votos_pt") + pl.col("votos_adv") + pl.col("votos_outros")
        ),
        on=CHAVE_SECAO,
        how="left",
    ).with_columns(pl.col("validos").fill_null(0))
    painel = monta_painel_secao(por_secao, detalhe, municipios)

    nomes = (
        detalhe_bruto.filter(pl.col("uf") != "ZZ")
        .group_by(CHAVE_LOCAL)
        .agg(pl.col("nm_local", "endereco").drop_nulls().mode().first())
    )
    locais = pl.read_parquet(interim / "locais" / "ano=2026" / "*.parquet")
    painel_local = monta_painel_local(painel, nomes, coordenadas(locais))

    painel.write_parquet(paths.PROCESSED / "painel_secao.parquet")
    painel_local.write_parquet(paths.PROCESSED / "painel_local.parquet")


if __name__ == "__main__":
    executa()
