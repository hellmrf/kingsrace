"""Dados da página "O que os votos mostram" (reports/conjuntura/index.html).

Junta num só arquivo, `dados.js`, todos os números que a página mostra. Lê só o que o pipeline
já produziu (métricas dos notebooks, painel por AMC, tabelas de referência), refaz poucas
contas descritivas e confere os totais contra os oficiais antes de escrever.

    uv run python reports/conjuntura/gerar_dados.py

Conversão de logit para pontos percentuais: perto de 50%, Δp ≈ β · p(1 − p) = β · 0,25, a
mesma aproximação do ensaio da virada de 2018. Os textos da página dizem "cerca de".
"""

import csv
import json
import statistics
from datetime import date
from pathlib import Path

import polars as pl

from kingsrace import paths
from kingsrace.features.decomposicao import decompoe_votos

AQUI = Path(__file__).resolve().parent
RES = paths.ROOT / "resultados"
P, REF = paths.PROCESSED, paths.REFERENCE

PP_POR_LOGIT = 25.0  # p(1 − p) · 100 com p = 0,5
LOG_3MIL_300MIL = 4.605170185988092  # ln(300 mil / 3 mil)
ANOS = [2006, 2010, 2014, 2018, 2022, 2026]
REGIOES = {"N": "Norte", "NE": "Nordeste", "CO": "Centro-Oeste", "SE": "Sudeste", "S": "Sul"}


def metricas(notebook: str) -> dict:
    return json.loads((RES / notebook / "metrics.json").read_text())


def r(x: float, casas: int = 2) -> float:
    return round(float(x), casas)


def br(x: float, casas: int = 1) -> str:
    """Número no padrão brasileiro, com o sinal de menos tipográfico."""
    texto = f"{abs(x):,.{casas}f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return ("\u2212" if x < 0 else "") + texto


def pp(logit: float) -> float:
    return r(logit * PP_POR_LOGIT, 1)


# --- Fontes -----------------------------------------------------------------------------------

panorama = metricas("01_panorama")["panorama"]
tamanho = metricas("02_tamanho")
previsao = metricas("03_previsao_2t")["B4"]
decomp = metricas("04_decomposicao")
composicao = metricas("05_composicao")
serie = metricas("06_serie")
virada = metricas("07_virada_2018")["E0"]
mecanismos = metricas("08_mecanismos")

amc = pl.read_parquet(P / "painel_amc.parquet")
t1 = amc.filter(pl.col("turno") == 1)
votos = pl.read_parquet(P / "votos_municipio.parquet")
municipios = pl.read_parquet(P / "municipios.parquet")
geo = municipios.group_by("amc_id").agg(pl.col("regiao").first())

oficiais = {
    (row["ano"], row["turno"], row["nr_votavel"]): row["votos"]
    for row in pl.read_csv(REF / "totais_oficiais.csv").iter_rows(named=True)
}


def nacional(ano: int, turno: int) -> dict[str, int]:
    """Votos por candidato no país, com o exterior (votos_municipio inclui a UF ZZ)."""
    v = votos.filter((pl.col("ano") == ano) & (pl.col("turno") == turno))
    return dict(v.group_by("nm_votavel").agg(pl.col("votos").sum()).iter_rows())


# --- 1. Resumo e o 1º turno de 2026 -----------------------------------------------------------

n26 = nacional(2026, 1)
lula_22 = oficiais[(2022, 1, 13)]
lula_26 = n26["LUIZ INÁCIO LULA DA SILVA"]
flavio_26 = n26["FLAVIO NANTES BOLSONARO"]
assert lula_26 == oficiais[(2026, 1, 13)], "Lula 2026 não bate com o total oficial"
assert flavio_26 == oficiais[(2026, 1, 22)], "Flávio 2026 não bate com o total oficial"


def pleito(ano: int, sufixo: str) -> pl.DataFrame:
    return t1.filter(pl.col("ano") == ano).select(
        "amc_id",
        *(pl.col(c).alias(f"{c}_{sufixo}") for c in ("aptos", "comparecimento", "validos")),
        pl.col("votos_pt").alias(f"votos_{sufixo}"),
        pl.col("pt_2p_logit").alias(f"pt_logit_{sufixo}"),
    )


base = decompoe_votos(pleito(2022, "de").join(pleito(2026, "para"), on="amc_id")).join(
    geo, on="amc_id"
)

a6 = decomp["A6"]["componentes_mi"]
soma = a6["eleitorado"] + a6["comparecimento"] + a6["validos"] + a6["fatia"]
assert abs(soma - a6["variacao"]) < 0.01, "componentes da A6 não somam a variação"
assert abs(base["delta"].sum() / 1e6 - a6["variacao"]) < 0.01, "LMDI refeito difere da A6"

pt22_t1 = t1.filter(pl.col("ano") == 2022).select("amc_id", pt22="pt_2p")
pt26_t1 = t1.filter(pl.col("ano") == 2026).select("amc_id", pt26="pt_2p")
variacao_amc = pt22_t1.join(pt26_t1, on="amc_id").with_columns(
    delta=100 * (pl.col("pt26") - pl.col("pt22"))
)
n_amcs = variacao_amc.height
amcs_subiu = variacao_amc.filter(pl.col("delta") > 0).height

base_sem_exterior = int(base["votos_de"].sum())
cascata = {
    "inicio_mi": r(base_sem_exterior / 1e6),
    "fim_mi": r(base["votos_para"].sum() / 1e6),
    "passos": [
        {"rotulo": "Mais eleitores", "mi": r(a6["eleitorado"])},
        {"rotulo": "Comparecimento", "mi": r(a6["comparecimento"])},
        {"rotulo": "Brancos e nulos", "mi": r(a6["validos"])},
        {"rotulo": "Troca de voto", "mi": r(a6["fatia"])},
    ],
    "frac_desmobilizacao": r(100 * decomp["A6"]["frac_desmobilizacao"], 1),
}

regioes = [
    {
        "regiao": REGIOES[k],
        "sigla": k,
        "lula_mi": r(v["delta_votos_pt_mi"]),
        "flavio_mi": r(v["delta_votos_adv_mi"]),
        "outros_mi": r(v["delta_votos_outros_mi"]),
        "eleitores_mi": r(v["delta_aptos_mi"]),
    }
    for k, v in decomp["A6_adversario"].items()
]

faixas_lim = [5_000, 10_000, 20_000, 50_000, 100_000, 500_000]
faixas_rot = [
    "< 5 mil",
    "5–10 mil",
    "10–20 mil",
    "20–50 mil",
    "50–100 mil",
    "100–500 mil",
    "≥ 500 mil",
]
por_faixa = (
    base.with_columns(
        faixa=pl.col("aptos_de").bin_intervals(faixas_lim, labels=faixas_rot).cast(pl.String)
    )
    .join(variacao_amc.select("amc_id", delta_pp="delta"), on="amc_id")
    .group_by("faixa")
    .agg(
        pl.col("delta").sum().alias("perda"),
        pl.col("aptos_de").sum(),
        pl.len().alias("amcs"),
        pl.col("delta_pp").median().alias("mediana_pp"),
    )
    .with_columns(
        pct_perda=100 * pl.col("perda") / pl.col("perda").sum(),
        pct_eleitorado=100 * pl.col("aptos_de") / pl.col("aptos_de").sum(),
    )
)
faixas = [
    {
        "faixa": f,
        "amcs": row["amcs"],
        "pct_eleitorado": r(row["pct_eleitorado"], 1),
        "pct_perda": r(row["pct_perda"], 1),
        "mediana_pp": r(row["mediana_pp"], 1),
    }
    for f in faixas_rot
    for row in por_faixa.filter(pl.col("faixa") == f).iter_rows(named=True)
]
a8 = decomp["A8"]["menos_de_20mil"]

# --- 2. O país andou em bloco: a variação de cada município, eleição a eleição ---------------

LIM, PASSO = 30, 2  # histogramas de −30 a +30 pp, caixas de 2 pp (as pontas acumulam o resto)
distribuicoes = []
for de, para in zip(ANOS, ANOS[1:], strict=False):
    d = (
        t1.filter(pl.col("ano") == de)
        .select("amc_id", "aptos", p0="pt_2p")
        .join(t1.filter(pl.col("ano") == para).select("amc_id", p1="pt_2p"), on="amc_id")
        .with_columns(delta=100 * (pl.col("p1") - pl.col("p0")))
    )
    caixas = (
        d.with_columns(
            caixa=(pl.col("delta").clip(-LIM, LIM - 1e-9) / PASSO).floor().cast(pl.Int32) * PASSO
        )
        .group_by("caixa")
        .len()
        .sort("caixa")
    )
    contagem = dict(caixas.iter_rows())
    distribuicoes.append(
        {
            "transicao": f"{de}→{para}",
            "caixas": [contagem.get(c, 0) for c in range(-LIM, LIM, PASSO)],
            "mediana_pp": r(d["delta"].median(), 1),
            "dp_pp": r(d["delta"].std(), 1),
            "pct_caiu": r(100 * (d["delta"] < 0).mean(), 1),
            "p10_pp": r(d["delta"].quantile(0.10), 1),
            "p90_pp": r(d["delta"].quantile(0.90), 1),
        }
    )

# --- 3. Pesquisas do 1º turno contra o resultado ----------------------------------------------

resultado_2p = r(100 * lula_26 / (lula_26 + flavio_26))
pesquisas_1t = []
with open(REF / "pesquisas_2026.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        if row["turno"] != "1":
            continue
        lula, flavio = float(row["lula"]), float(row["flavio"])
        pesquisas_1t.append(
            {
                "instituto": row["instituto"],
                "campo_fim": row["campo_fim"],
                "lula": lula,
                "flavio": flavio,
                "lula_2p": r(100 * lula / (lula + flavio)),
            }
        )
pesquisas_1t.sort(key=lambda p: -p["lula_2p"])
vies_medio = r(sum(p["lula_2p"] for p in pesquisas_1t) / len(pesquisas_1t) - resultado_2p)

# --- 4. O 2º turno ----------------------------------------------------------------------------

n22_1, n22_2 = nacional(2022, 1), nacional(2022, 2)
outros_26 = sorted(
    (
        {"nome": nome, "votos": v}
        for nome, v in n26.items()
        if nome
        not in (
            "FLAVIO NANTES BOLSONARO",
            "LUIZ INÁCIO LULA DA SILVA",
            "VOTO NULO",
            "VOTO BRANCO",
            "LEONARDO ALVES DE ARAUJO",
        )
    ),
    key=lambda c: -c["votos"],
)
NOMES_CURTOS = {
    "AUGUSTO JORGE CURY": "Augusto Cury",
    "RENAN ANTONIO FERREIRA DOS SANTOS": "Renan Santos",
    "RONALDO RAMOS CAIADO": "Ronaldo Caiado",
    "ROMEU ZEMA NETO": "Romeu Zema",
}
for c in outros_26:
    c["nome_curto"] = NOMES_CURTOS.get(c["nome"], c["nome"].title())

t26 = t1.filter(pl.col("ano") == 2026)
# o painel não tem o exterior; comparecimento e abstenção do exterior ficam de fora (~1,5 mi
# de aptos), e a página diz "no Brasil"
abstencao_26 = int(t26["aptos"].sum() - t26["comparecimento"].sum())

segundo_turno = {
    "lula_1t": lula_26,
    "flavio_1t": flavio_26,
    "diferenca": flavio_26 - lula_26,
    "outros": outros_26,
    "outros_total": sum(c["votos"] for c in outros_26),
    "brancos": n26.get("VOTO BRANCO", 0),
    "nulos": n26.get("VOTO NULO", 0),
    "abstencao_brasil": abstencao_26,
    "aptos_brasil": int(t26["aptos"].sum()),
    "em_2022": {
        "lula_1t": oficiais[(2022, 1, 13)],
        "lula_2t": oficiais[(2022, 2, 13)],
        "bolsonaro_1t": oficiais[(2022, 1, 22)],
        "bolsonaro_2t": oficiais[(2022, 2, 22)],
    },
    "previsao": {
        "central": r(previsao["previsao"]["central_pct"], 1),
        "faixa_inf": r(previsao["previsao"]["correcao_total_pct"], 1),
        "faixa_sup": r(previsao["previsao"]["sem_correcao_pct"], 1),
        "primeiro_turno": r(previsao["previsao"]["primeiro_turno_pct"], 1),
        "congelada_em": "2026-10-08",
        "pesquisa": "Datafolha, 6 a 8/10: Lula 48% dos válidos",
    },
    "backtest_2022_rmse": {
        k: r(v["rmse_pp"]) for k, v in previsao["backtest_2022"].items() if isinstance(v, dict)
    },
}
assert abs(segundo_turno["previsao"]["central"] - 46.9) < 0.05, "previsão central mudou"
assert n22_1["LUIZ INÁCIO LULA DA SILVA"] == oficiais[(2022, 1, 13)]
assert n22_2["LUIZ INÁCIO LULA DA SILVA"] == oficiais[(2022, 2, 13)]

uf_22 = (
    t1.filter(pl.col("ano") == 2022)
    .group_by("uf")
    .agg(pl.col("votos_pt", "votos_adv", "aptos").sum().name.suffix("_22"))
)
uf_26 = t26.group_by("uf").agg(pl.col("votos_pt", "votos_adv", "aptos").sum().name.suffix("_26"))
ufs = []
for row in uf_22.join(uf_26, on="uf").sort("uf").iter_rows(named=True):
    ufs.append(
        {
            "uf": row["uf"],
            "aptos_26": row["aptos_26"],
            "lula_delta": row["votos_pt_26"] - row["votos_pt_22"],
            "flavio_delta": row["votos_adv_26"] - row["votos_adv_22"],
            "lula_2p_1t": r(
                100 * row["votos_pt_26"] / (row["votos_pt_26"] + row["votos_adv_26"]), 1
            ),
            "previsao_2t": r(previsao["por_uf"][row["uf"]]["central_pct"], 1),
        }
    )

# --- 5. Bolsa Família (A4) e a raiz de 2018 ---------------------------------------------------

a4 = composicao["A4"]
# desvio-padrão da cobertura (famílias por 100 habitantes), recuperado do efeito de 1 dp da A4a
dp_cobertura = composicao["A4a"]["efeito_1dp"] / composicao["A4a"]["beta"]
bolsa_familia = {
    "dp_cobertura": r(dp_cobertura, 1),
    # no nível: quanto o PT tinha a mais, por 1 dp de cobertura, em cada ano (painel da A4)
    "nivel_2022_pp": pp(a4["cobertura"]["b_2022"] * dp_cobertura),
    "nivel_2026_pp": pp(a4["cobertura"]["b_2026"] * dp_cobertura),
    "razao": r(a4["cobertura"]["razao"], 1),
    # 1 dp de cobertura (~7,6 famílias por 100 habitantes) no modelo de Δ (A4a)
    "efeito_1dp_pp": pp(composicao["A4a"]["efeito_1dp"]),
    "tamanho_1dp_pp": pp(tamanho["A1"]["M3_1dp"]["log_aptos_de"]),
}

transicoes = ["2006_2010", "2010_2014", "2014_2018", "2018_2022", "2022_2026"]
rot = [t.replace("_", "→") for t in transicoes]
c5 = serie["C5"]
e2a = mecanismos["E2a"]
desde_2014 = virada["acumulado"]["desde_2014"]
e0b = mecanismos["E0b"]
raiz = {
    "nacional": [{"ano": a, "pt_2p": r(serie["nacional"][str(a)]["pt_2p_pct"], 1)} for a in ANOS],
    # tamanho: diferença entre um município de 3 mil e um de 300 mil eleitores, em pp
    "tamanho": [
        {"transicao": t, "pp": r(c5[k]["coef"] * LOG_3MIL_300MIL * PP_POR_LOGIT, 1)}
        for t, k in zip(rot, transicoes, strict=True)
    ],
    # evangélicos: 1 dp a mais de % evangélica (Censo 2010), em pp
    "evangelicos": [
        {"transicao": t, "pp": pp(e2a[k]["coef"])} for t, k in zip(rot, transicoes, strict=True)
    ],
    "retencao_2026": [
        {
            "canal": "Choque das cidades grandes (tamanho)",
            "pct": r(100 * desde_2014["2026"]["coef"] / desde_2014["2018"]["coef"], 0),
        },
        {"canal": "% de evangélicos (Censo 2010)", "pct": r(100 * e0b["E2a"]["retencao_2026"], 0)},
        {"canal": "Templos evangélicos (CNPJ)", "pct": r(100 * e0b["E2b"]["retencao_2026"], 0)},
        {"canal": "Voto em pastores para deputado", "pct": r(100 * e0b["E2c"]["retencao_2026"], 0)},
    ],
    "congelamento": [
        {"transicao": t, "correlacao": r(virada["congelamento"]["turno1"][k]["Adversario"], 3)}
        for t, k in zip(rot, transicoes, strict=True)
    ],
}

# --- 6. Vereditos (o registro de hipóteses em linguagem simples) ------------------------------


def salto(id_: str) -> float:
    return pp(mecanismos[id_]["2014_2018"]["coef"])


vereditos = [
    {
        "id": "A1",
        "veredito": "sim",
        "pergunta": "Os municípios menores perderam mais em 2026?",
        "resposta": f"Sim. Entre um município de 3 mil e um de 300 mil eleitores, "
        f"{br(tamanho['A1']['R1_pp']['3mil_vs_300mil_pp']['M3'])} pontos a mais de queda "
        f"no menor, mesmo comparando lugares parecidos.",
    },
    {
        "id": "A4",
        "veredito": "sim",
        "pergunta": "O Bolsa Família segurou votos de Lula?",
        "resposta": f"Sim. A ligação entre cobertura do programa e voto no PT ficou "
        f"{br(bolsa_familia['razao'], 0)} vezes maior de 2022 para 2026.",
    },
    {
        "id": "A6",
        "veredito": "nao",
        "pergunta": "A queda foi abstenção (eleitor de Lula em casa)?",
        "resposta": f"Não. Comparecimento e brancos/nulos explicam "
        f"{br(cascata['frac_desmobilizacao'], 0)}% da perda; o resto é troca de voto.",
    },
    {
        "id": "A2",
        "veredito": "nao",
        "pergunta": "A expansão da soja explica a queda de 2026?",
        "resposta": "Não. Onde a soja avançou mais, a queda não foi maior.",
    },
    {
        "id": "A3",
        "veredito": "nao",
        "pergunta": "O crescimento evangélico de 2010 a 2022 explica 2026?",
        "resposta": "Não. O efeito evangélico é de 2018 e continua lá, mas não gera queda nova.",
    },
    {
        "id": "E2",
        "veredito": "sim",
        "pergunta": "As igrejas explicam a virada de 2018?",
        "resposta": f"Sim, as três medidas, em pontos por desvio: % de evangélicos "
        f"({br(salto('E2a'))}), templos no CNPJ ({br(salto('E2b'))}) e voto em pastores "
        f"({br(salto('E2c'))}). Nada antes de 2018.",
    },
    {
        "id": "E2d",
        "veredito": "nao",
        "pergunta": "Foi a Universal (aliada do PT até 2016) que virou?",
        "resposta": "Não. A pegada é maior onde os pastores eram de fora da base de Dilma.",
    },
    {
        "id": "E4a",
        "veredito": "nao",
        "pergunta": "Onde se perdeu mais emprego, o PT caiu mais em 2018?",
        "resposta": "Não. A recessão não deixou marca local no voto.",
    },
    {
        "id": "E4b",
        "veredito": "nao",
        "pergunta": "Onde petróleo, estaleiros e obras pesavam (Lava Jato), o PT caiu mais?",
        "resposta": "Não. Nenhuma marca local.",
    },
    {
        "id": "E5",
        "veredito": "nao",
        "pergunta": "Onde a violência subiu, o PT caiu mais em 2018?",
        "resposta": "Não. A violência cresceu mais no Norte e no Nordeste, onde o PT resistiu.",
    },
    {
        "id": "E7a",
        "veredito": "nao",
        "pergunta": "A explosão de MEIs afastou o eleitor do PT?",
        "resposta": "Não, com os controles.",
    },
    {
        "id": "E7b",
        "veredito": "antiga",
        "pergunta": "Onde há mais trabalhador por conta própria, o PT perde?",
        "resposta": "Sim, mas já era assim antes de 2018 e se aprofunda depois: divisão antiga.",
    },
]
assert decomp["A6"]["sustenta"] == 0 and composicao["A4"]["interacao_2026"]["sustenta"] == 1
assert all(mecanismos[k]["sustenta"] == 1 for k in ("E2a", "E2b", "E2c"))
assert all(mecanismos[k]["sustenta"] == 0 for k in ("E4a", "E4b", "E5", "E7a"))

# --- 7. Fontes novas: linha do tempo e pesquisas de 2025–2026 ---------------------------------


def le_csv(nome: str) -> list[dict]:
    caminho = REF / nome
    if not caminho.exists():
        return []
    with open(caminho, encoding="utf-8") as f:
        return list(csv.DictReader(f))


linha_do_tempo = le_csv("linha_do_tempo.csv")
# só os campos que a página usa; a fonte de cada linha fica no CSV
pesquisas_2t = [
    {
        **{k: p[k] for k in ("instituto", "campo_inicio", "campo_fim", "base", "conferido")},
        "lula": float(p["lula"]),
        "flavio": float(p["flavio"]),
        "lula_2p": r(100 * float(p["lula"]) / (float(p["lula"]) + float(p["flavio"])), 1),
    }
    for p in le_csv("pesquisas_serie_2025_2026.csv")
]
aprovacao = [
    {
        **{k: a[k] for k in ("instituto", "campo_inicio", "campo_fim")},
        "aprova": float(a["aprova"]),
        "desaprova": float(a["desaprova"]),
    }
    for a in le_csv("aprovacao_lula_2025_2026.csv")
]

# resumo mensal (mediana das pesquisas pelo mês de fim do campo), para o texto da seção 7
por_mes: dict[str, list[float]] = {}
for p in pesquisas_2t:
    por_mes.setdefault(p["campo_fim"][:7], []).append(p["lula_2p"])
pesquisas_mensal = [
    {"mes": m, "n": len(v), "mediana": r(statistics.median(v), 1)}
    for m, v in sorted(por_mes.items())
]

# --- Saída ------------------------------------------------------------------------------------

dados = {
    "gerado_em": date.today().isoformat(),
    "resumo": {
        "lula_22": lula_22,
        "lula_26": lula_26,
        "flavio_26": flavio_26,
        "perda": lula_26 - lula_22,
        "amcs": n_amcs,
        "amcs_subiu": amcs_subiu,
        "pt_2p_22": r(panorama["2022_1t"]["pt_2p_pct"]),
        "pt_2p_26": r(panorama["2026_1t"]["pt_2p_pct"]),
        "mediana_amc_pp": r(variacao_amc["delta"].median(), 1),
    },
    "cascata": cascata,
    "regioes": regioes,
    "faixas": faixas,
    "a8": {
        "pct_eleitorado": r(100 * a8["frac_eleitorado"], 1),
        "pct_perda": r(100 * a8["frac_perda"], 1),
    },
    "distribuicoes": {"de": -LIM, "passo": PASSO, "transicoes": distribuicoes},
    "pesquisas_1t": {
        "resultado_2p": resultado_2p,
        "vies_medio": vies_medio,
        "institutos": pesquisas_1t,
    },
    "segundo_turno": segundo_turno,
    "ufs": ufs,
    "bolsa_familia": bolsa_familia,
    "raiz": raiz,
    "vereditos": vereditos,
    "linha_do_tempo": linha_do_tempo,
    "pesquisas_2t": pesquisas_2t,
    "aprovacao": aprovacao,
    "pesquisas_mensal": pesquisas_mensal,
}

assert n_amcs == 5562, n_amcs
saida = AQUI / "dados.js"
saida.write_text(
    "// Gerado por reports/conjuntura/gerar_dados.py. Não editar à mão.\n"
    f"window.DADOS = {json.dumps(dados, ensure_ascii=False, indent=1)};\n",
    encoding="utf-8",
)
print(f"{saida.relative_to(paths.ROOT)}: {saida.stat().st_size / 1024:.0f} KB")
print(f"AMCs {n_amcs}, PT subiu em {amcs_subiu}; viés médio das pesquisas {vies_medio} pp")
print(
    f"linha do tempo: {len(linha_do_tempo)} eventos; pesquisas 2T: {len(pesquisas_2t)}; "
    f"aprovação: {len(aprovacao)}"
)
