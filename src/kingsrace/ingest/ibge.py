"""Covariáveis municipais do IBGE (Censo 2022 e PIB dos Municípios) via API do SIDRA.

Cada consulta em CONSULTAS vira um arquivo bruto em data/raw/ibge/sidra/<nome>.json
(importado com `dvc import-url` a partir de `url(nome)`) e um conjunto de colunas.
As chaves das colunas são os códigos das dimensões D2C, D3C, ... de cada linha da
resposta: variável, ano e categorias das classificações, nessa ordem.
"""

import polars as pl

SIDRA = "https://apisidra.ibge.gov.br/values"
SUPRIMIDOS = {"-", "..", "...", "X"}

# nome: (caminho da consulta, {(variável, ano, *categorias): coluna})
CONSULTAS: dict[str, tuple[str, dict[tuple[str, ...], str]]] = {
    "populacao": (
        "t/4714/n6/all/v/93,6318,614/p/2022",
        {
            ("93", "2022"): "populacao",
            ("6318", "2022"): "area_km2",
            ("614", "2022"): "densidade",
        },
    ),
    "situacao": (
        "t/9923/n6/all/v/1000093/p/2022/c1/1",
        {("1000093", "2022", "1"): "pct_urbana"},
    ),
    "idade": (
        "t/9515/n6/all/v/10612,10613/p/2022",
        {("10612", "2022"): "indice_envelhecimento", ("10613", "2022"): "idade_mediana"},
    ),
    "cor_raca": (
        "t/9605/n6/all/v/1000093/p/2022/c86/2776,2777,2779",
        {
            ("1000093", "2022", "2776"): "pct_branca",
            ("1000093", "2022", "2777"): "pct_preta",
            ("1000093", "2022", "2779"): "pct_parda",
        },
    ),
    "alfabetizacao": (
        "t/9543/n6/all/v/2513/p/2022/c2/6794/c86/95251/c287/100362",
        {("2513", "2022", "6794", "95251", "100362"): "taxa_alfabetizacao"},
    ),
    "religiao": (
        "t/9537/n6/all/v/1000140/p/2022/c133/95263,95277,2836/c2/6794/c58/95253",
        {
            ("1000140", "2022", "95263", "6794", "95253"): "pct_catolica",
            ("1000140", "2022", "95277", "6794", "95253"): "pct_evangelica",
            ("1000140", "2022", "2836", "6794", "95253"): "pct_sem_religiao",
        },
    ),
    "renda": (
        "t/10295/n6/all/v/13431,13534/p/2022/c2/6794/c86/95251/c58/95253",
        {
            ("13431", "2022", "6794", "95251", "95253"): "renda_pc_media",
            ("13534", "2022", "6794", "95251", "95253"): "renda_pc_mediana",
        },
    ),
    "renda_fontes": (
        "t/10297/n6/all/v/13504/p/2022/c11308/79452",
        {("13504", "2022", "79452"): "pct_renda_outras_fontes"},
    ),
    "pib": (
        "t/5938/n6/all/v/37,498,513,525/p/2021,2023",
        # o valor adicionado por setor de 2023 ainda não saiu por município (vem "...");
        # para 2023 só há o PIB total
        {
            ("37", "2021"): "pib_2021",
            ("37", "2023"): "pib_2023",
            ("498", "2021"): "va_2021",
            ("513", "2021"): "va_agro_2021",
            ("525", "2021"): "va_adm_2021",
        },
    ),
}


def url(nome: str) -> str:
    return f"{SIDRA}/{CONSULTAS[nome][0]}"


def sidra_para_tabela(linhas: list[dict], colunas: dict[tuple[str, ...], str]) -> pl.DataFrame:
    """Converte a resposta do SIDRA (1ª linha = cabeçalho) em uma linha por município.

    Valores suprimidos pelo IBGE ("-", "..", "...", "X") viram nulos. Falha se alguma
    coluna pedida não aparecer na resposta (consulta e mapeamento desalinhados).
    """
    dims = sorted(
        (k for k in linhas[0] if k[0] == "D" and k.endswith("C") and k != "D1C"),
        key=lambda k: int(k[1:-1]),
    )
    registros = []
    for r in linhas[1:]:
        coluna = colunas.get(tuple(r[d] for d in dims))
        if coluna is not None:
            valor = None if r["V"] in SUPRIMIDOS else float(r["V"])
            registros.append({"cd_ibge": int(r["D1C"]), "coluna": coluna, "valor": valor})

    ausentes = set(colunas.values()) - {r["coluna"] for r in registros}
    if ausentes:
        raise ValueError(f"colunas ausentes na resposta do SIDRA: {sorted(ausentes)}")

    largo = pl.DataFrame(
        registros, schema={"cd_ibge": pl.Int64, "coluna": pl.String, "valor": pl.Float64}
    ).pivot(on="coluna", index="cd_ibge", values="valor")
    return largo.select("cd_ibge", *dict.fromkeys(colunas.values()))
