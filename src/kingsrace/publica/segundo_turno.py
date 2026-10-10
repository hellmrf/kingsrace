"""Dados da página "Como virar" (site/paginas/segundo-turno/), só com saídas do DVC (D12).

Lê as métricas e os gráficos das etapas `segundo_turno` e `pesquisas` (resultados/), a
previsão congelada da B4 (resultados/03_previsao_2t/) e as tabelas de data/processed/.
Seleciona, ordena e renomeia; não faz conta nova. Grava em site/dados/segundo-turno/:

- `pagina.json`: os números do texto (o build os grava no HTML);
- `graficos.json`: os dados de cada gráfico, com os mesmos nomes do `dvc plots`;
- `municipios.json`: a tabela da busca por município;
- `locais/<código IBGE>.json`: locais de votação de cada município, para a busca;
- `listas/<UF>.csv`: os mesmos locais por estado, para baixar.

Uso: python -m kingsrace.publica dados segundo-turno
"""

import polars as pl

from kingsrace import paths
from kingsrace.features.base import geografia_amc
from kingsrace.publica import comum

ETAPA = "segundo_turno"
DESTINO = comum.DADOS / "segundo-turno"
TABELAS = paths.PROCESSED / "segundo_turno"
GRAFICOS = [
    "G1_entre_turnos",
    "G1_estoques_2026",
    "G2_cenarios",
    "G2_efeito_por_origem",
    "G2_transicao_BR",
    "G3_reserva_uf",
    "G4_fatia_uf",
    "G4_fatia_faixa",
]
ROTULO_ORIGEM = {
    "pt": "Eleitores de Lula",
    "adv": "Eleitores de Flávio",
    "cury": "Augusto Cury",
    "renan": "Renan Santos",
    "caiado": "Ronaldo Caiado",
    "zema": "Romeu Zema",
    "direita": "Outros à direita",
    "esquerda": "Outros à esquerda",
    "bn": "Brancos e nulos",
    "abst": "Quem não votou",
    "tebet": "Simone Tebet",
    "ciro": "Ciro Gomes",
}
ROTULO_CENARIO = {
    "perfil": "Cada eliminado como o mais parecido de 2022",
    "como_tebet": "Todos como os eleitores de Tebet",
    "como_ciro": "Todos como os eleitores de Ciro",
    "como_direita": "Todos como a direita de 2022",
}


def pagina(m: dict, b4: dict, governador: pl.DataFrame, g6: dict) -> dict:
    g = lambda caminho: comum.metrica(m, caminho)  # noqa: E731
    gov26 = governador.filter(pl.col("ano") == 2026)
    com = gov26.filter("tem_2t")["uf"].sort().to_list()
    return {
        "diferenca_mi": g("G1/diferenca_mi"),
        "estoques_mi": g("G1/estoques_mi"),
        "taxa_necessaria": g("G1/taxa_necessaria"),
        "entre_turnos": g("G1/entre_turnos"),
        "cenarios": {
            nome: {**valores, "rotulo": ROTULO_CENARIO[nome]}
            for nome, valores in g("G2/cenarios").items()
        },
        "efeito_perfil_mi": g("G2/efeito_perfil_mi"),
        "matriz": g("G2/BR"),
        "validacao": g("G2/validacao"),
        "padrao_2022": g("G2/padrao_2022"),
        "g3": g("G3/BR"),
        "locais_casados": g("G3/locais/casados"),
        "licao_2022": g("G3/licao_2022"),
        "g3b": g("G3b"),
        "governador_2t_2026": com,
        "sem_governador_2026": gov26.filter(~pl.col("tem_2t"))["uf"].sort().to_list(),
        "g4": g("G4/componentes_mi"),
        "g4_faixa_mil": g("G4/fatia_mil"),
        "b4_central_pct": comum.metrica(b4, "B4/previsao/central_pct"),
        "b4_primeiro_turno_pct": comum.metrica(b4, "B4/previsao/primeiro_turno_pct"),
        "b4_faixa_pct": [
            comum.metrica(b4, "B4/previsao/correcao_total_pct"),
            comum.metrica(b4, "B4/previsao/sem_correcao_pct"),
        ],
        "valor_1pct_mi": g("G1/valor_1pct_mi"),
        "exterior_margem_mi": g("G1/exterior_margem_mi"),
        "calculadora": {
            "n": {
                k: g(f"G1/estoques_mi/{k}")
                for k in ("pt", "adv", "eliminados", "esquerda", "bn", "abst")
            },
            "padrao_2022": g("G2/padrao_2022"),
            "exterior_mi": g("G1/exterior_margem_mi"),
        },
        "rotulo_origem": ROTULO_ORIGEM,
        "g6": {
            k: comum.metrica(g6, f"G6/{k}")
            for k in (
                "n_pesquisas",
                "n_institutos_na_janela",
                "real_1t",
                "media",
                "modelo",
                "distancia_pp",
                "distancia_mi",
                "margem_mi",
                "votos_dos_dois_1t_mi",
                "cruzamentos/n",
                "vies_medio_1t",
            )
        },
    }


def municipios(reserva: pl.DataFrame, nomes: pl.DataFrame) -> pl.DataFrame:
    coords = pl.read_parquet(paths.PROCESSED / "coordenadas_municipio.parquet")
    return (
        reserva.join(nomes, on="cd_ibge")
        .join(coords.select("cd_ibge", "lat", "lon"), on="cd_ibge", how="left")
        .select(
            "cd_ibge", "nome", "uf", "aptos", "p_lula", "abstencao", "nao_votou", "reserva",
            "rendimento_pp", "perdidos", "votos_eliminados", "lat", "lon",
        )
        .sort("uf", "nome")
    )  # fmt: skip


COLUNAS_LOCAL = {
    "nm_local": "nome",
    "endereco": "endereco",
    "bairro": "bairro",
    "cd_ibge": "cd_ibge",
    "zona": "zona",
    "nr_local": "nr_local",
    "aptos": "aptos",
    "abstencao": "abstencao",
    "nao_votou": "nao_votou",
    "p_lula": "p_lula",
    "reserva": "reserva",
    "rendimento_pp": "rendimento_pp",
    "perdidos": "perdidos",
    "lat": "lat",
    "lon": "lon",
}


# janelas entre o 1º e o 2º turno de cada eleição com 2º turno citada na página
JANELAS_ENTRE_TURNOS = [("2006-10-02", "2006-10-29"), ("2022-10-03", "2022-10-30"),
                        ("2026-10-05", "2026-10-25")]  # fmt: skip


def documentado_entre_turnos() -> pl.DataFrame:
    """Eventos da linha do tempo (G7) que caem entre os turnos de 2006, 2022 e 2026."""
    t = pl.read_csv(paths.REFERENCE / "linha_do_tempo.csv")
    dentro = pl.any_horizontal(
        pl.col("data").is_between(pl.lit(a), pl.lit(b)) for a, b in JANELAS_ENTRE_TURNOS
    )
    return t.filter(dentro & ~pl.col("faixa").eq("urnas")).sort("data")


def tabela_pesquisas() -> pl.DataFrame:
    """Pesquisas do 2º turno com viés e corrigido (etapa pesquisas) e a procedência (série)."""
    g6 = pl.read_parquet(paths.PROCESSED / "pesquisas" / "pesquisas_2t.parquet")
    serie = pl.read_csv(paths.REFERENCE / "pesquisas_serie_2025_2026.csv", try_parse_dates=True)
    institutos = pl.read_csv(paths.REFERENCE / "institutos.csv")
    procedencia = (
        serie.join(institutos, left_on="instituto", right_on="nome", how="left")
        .select(
            pl.col("instituto_right").alias("instituto"), "campo_fim", "amostra", "lula", "flavio",
            "fonte", "url", pl.col("conferido").fill_null("não"),
        )
    )  # fmt: skip
    return (
        g6.join(procedencia, on=["instituto", "campo_fim"], how="left")
        .with_columns(pl.col("campo_inicio", "campo_fim").cast(pl.String))
        .sort("campo_fim", "instituto", descending=[True, False])
    )


def amcs() -> pl.DataFrame:
    """Ex-eleitores (G4) por AMC, com nome, UF e centro eleitoral, para o mapa "conversar"."""
    ex = pl.read_parquet(TABELAS / "ex_eleitores_amc.parquet").select(
        "amc_id", fatia=pl.col("c_fatia"), delta=pl.col("delta")
    )
    municipios_ = pl.read_parquet(paths.PROCESSED / "municipios.parquet")
    geo = geografia_amc(municipios_).select("amc_id", "nome", "uf")
    coords = pl.read_parquet(paths.PROCESSED / "coordenadas_amc.parquet")
    return (
        ex.join(geo, on="amc_id")
        .join(coords.select("amc_id", "lat", "lon"), on="amc_id", how="left")
        .sort("amc_id")
    )


def arredonda(df: pl.DataFrame) -> pl.DataFrame:
    """Só formatação: frações com 3 casas, votos inteiros, coordenadas com 5 casas (~1 m)."""
    fracoes = [c for c in ("abstencao", "p_lula") if c in df.columns]
    votos = [
        c
        for c in ("reserva", "rendimento_pp", "perdidos", "votos_eliminados", "fatia", "delta")
        if c in df.columns
    ]
    coords = [c for c in ("lat", "lon") if c in df.columns]
    return df.with_columns(
        pl.col(fracoes).round(3), pl.col(votos).round(0).cast(pl.Int64), pl.col(coords).round(5)
    )


def executa() -> None:
    m = comum.metricas(ETAPA)
    b4 = comum.metricas("03_previsao_2t")
    governador = pl.read_parquet(TABELAS / "governador_2t.parquet")
    oficial = comum.oficial(2026, 1, 22) - comum.oficial(2026, 1, 13)
    if abs(comum.metrica(m, "G1/diferenca_mi") * 1e6 - oficial) > 0.5:
        raise ValueError("G1/diferenca_mi não bate com os totais oficiais do TSE")

    g6 = comum.metricas("pesquisas")
    comum.grava_json(
        DESTINO / "pagina.json",
        pagina(m, b4, governador, g6)
        | {
            "pesquisas": tabela_pesquisas().to_dicts(),
            "documentado": documentado_entre_turnos().to_dicts(),
            "evidencias": pl.read_csv(paths.REFERENCE / "evidencias_mobilizacao.csv").to_dicts(),
        },
    )
    graficos = {n: comum.grafico(ETAPA, n) for n in GRAFICOS}
    graficos |= {n: comum.grafico("pesquisas", n) for n in ("G6_media", "G6_pesquisas")}
    comum.grava_json(DESTINO / "graficos.json", graficos)

    nomes = pl.read_parquet(paths.PROCESSED / "municipios.parquet").select("cd_ibge", "nome")
    tabela = arredonda(municipios(pl.read_parquet(TABELAS / "reserva_municipio.parquet"), nomes))
    comum.grava_json(DESTINO / "municipios.json", tabela.to_dicts())
    ufs = tabela.select("cd_ibge", "uf")

    comum.grava_json(DESTINO / "amcs.json", arredonda(amcs()).to_dicts())

    locais = pl.read_parquet(TABELAS / "reserva_local.parquet").select(
        *(pl.col(c).alias(a) for c, a in COLUNAS_LOCAL.items())
    )
    locais = arredonda(locais).sort("rendimento_pp", descending=True)
    for (cd_ibge,), parte in locais.group_by("cd_ibge", maintain_order=True):
        comum.grava_json(DESTINO / "locais" / f"{cd_ibge}.json", parte.drop("cd_ibge").to_dicts())
    (DESTINO / "listas").mkdir(parents=True, exist_ok=True)
    com_municipio = locais.join(nomes.rename({"nome": "municipio"}), on="cd_ibge")
    for (uf,), parte in (
        com_municipio.join(ufs, on="cd_ibge").sort("uf").group_by("uf", maintain_order=True)
    ):
        parte.drop("uf").sort("municipio", "rendimento_pp", descending=[False, True]).write_csv(
            DESTINO / "listas" / f"{uf}.csv"
        )
