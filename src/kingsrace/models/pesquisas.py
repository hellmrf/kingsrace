"""G6: as pesquisas do 2º turno de 2026 ao lado do modelo (registro em docs/hipoteses.md).

Para cada dia desde 05/10, a média das pesquisas (a mais recente de cada instituto nos
últimos 14 dias), bruta e corrigida pelo viés de cada instituto no 1º turno (λ = 0, 0,5 e 1,
a correção da B4). A média é comparada com a previsão v1 da B4 e com a fatia de Lula em cada
cenário da G2 ("padrão de 2022"). Os cruzamentos por voto no 1º turno, quando houver, são
comparados com o saldo de cada grupo na G2.

Grava em data/processed/pesquisas/ e registra métricas e gráficos em resultados/pesquisas/
(D12). Uma pesquisa nova é uma linha em pesquisas_serie_2025_2026.csv e um `dvc repro`.

Uso: python -m kingsrace.models.pesquisas
"""

from __future__ import annotations

import json
from datetime import date, timedelta

import polars as pl

from kingsrace import paths, resultados
from kingsrace.features import pesquisas as fp
from kingsrace.models.previsao_2t import LAMBDAS, alvo_das_pesquisas

SAIDA = paths.PROCESSED / "pesquisas"
JANELA = timedelta(days=14)


def fatia_real_1t() -> float:
    painel = pl.read_parquet(paths.PROCESSED / "painel_municipio.parquet").filter(
        (pl.col("ano") == 2026) & (pl.col("turno") == 1)
    )
    return float(painel["votos_pt"].sum() / (painel["votos_pt"].sum() + painel["votos_adv"].sum()))


def votos_dos_dois_1t() -> float:
    """Votos de Lula + Flávio no 1º turno, com o exterior: a escala para ler pp em votos."""
    v = pl.read_parquet(paths.PROCESSED / "votos_municipio.parquet").filter(
        (pl.col("ano") == 2026)
        & (pl.col("turno") == 1)
        & pl.col("papel").is_in(["pt", "adversario"])
    )
    return float(v["votos"].sum())


def media_diaria(tabela: pl.DataFrame, real_1t: float, ate: date) -> pl.DataFrame:
    """Uma linha por dia de 05/10 até `ate`: institutos na janela e média por λ."""
    linhas = []
    dia = fp.INICIO_2T
    while dia <= ate:
        janela = tabela.filter((pl.col("turno") == 1) | (pl.col("campo_fim") >= dia - JANELA))
        if janela.filter((pl.col("turno") == 2) & (pl.col("campo_fim") <= dia)).height:
            alvos = {n: alvo_das_pesquisas(janela, real_1t, lam, dia) for n, lam in LAMBDAS.items()}
            linhas.append(
                {
                    "data": dia,
                    "institutos": alvos["central"]["pesquisas_2t"],
                    "bruta": alvos["sem_correcao"]["alvo"],
                    "corrigida": alvos["central"]["alvo"],
                    "correcao_total": alvos["correcao_total"]["alvo"],
                }
            )
        dia += timedelta(days=1)
    return pl.DataFrame(linhas)


def por_instituto(tabela: pl.DataFrame, real_1t: float, ate: date) -> pl.DataFrame:
    """Cada pesquisa do 2º turno, com o viés do instituto e o valor corrigido (λ = 0,5)."""
    linhas = []
    for row in tabela.filter(pl.col("turno") == 2).iter_rows(named=True):
        um = tabela.filter((pl.col("turno") == 1) | (pl.col("campo_fim") == row["campo_fim"]))
        um = um.filter((pl.col("turno") == 1) | (pl.col("instituto") == row["instituto"]))
        det = alvo_das_pesquisas(um, real_1t, LAMBDAS["central"], row["campo_fim"])["detalhe"]
        d = det.filter(pl.col("instituto") == row["instituto"]).row(0, named=True)
        linhas.append(
            {
                **{k: row[k] for k in ("instituto", "campo_inicio", "campo_fim", "base")},
                "s": d["s"],
                "vies": d["vies"],
                "corrigido": d["corrigido"],
            }
        )
    return pl.DataFrame(linhas).sort("campo_fim", "instituto")


def cruzamentos(cruz: pl.DataFrame, institutos: pl.DataFrame, efeito_g2: dict) -> pl.DataFrame:
    """Saldo Lula − Flávio entre os válidos de cada grupo do 1º turno, contra o da G2."""
    if cruz.is_empty():
        return pl.DataFrame(
            schema={
                "instituto": pl.String,
                "campo_fim": pl.Date,
                "grupo_1t": pl.String,
                "saldo_pesquisa": pl.Float64,
                "saldo_g2": pl.Float64,
            }
        )
    return (
        fp.canoniza(cruz, institutos)
        .with_columns(
            saldo_pesquisa=(pl.col("lula") - pl.col("flavio")) / (pl.col("lula") + pl.col("flavio"))
        )
        .with_columns(
            saldo_g2=pl.col("grupo_1t").replace_strict(
                efeito_g2, default=None, return_dtype=pl.Float64
            )
        )
        .select("instituto", "campo_fim", "grupo_1t", "saldo_pesquisa", "saldo_g2")
    )


def executa() -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    primeiro, serie, institutos = fp.le()
    tabela = fp.para_previsao(primeiro, serie, institutos).with_columns(
        s=pl.col("lula") / (pl.col("lula") + pl.col("flavio"))
    )
    real_1t = fatia_real_1t()
    ate = tabela.filter(pl.col("turno") == 2)["campo_fim"].max()
    media = media_diaria(tabela, real_1t, ate)
    pesquisas = por_instituto(tabela, real_1t, ate)

    g = json.loads((paths.ROOT / "resultados" / "segundo_turno" / "metrics.json").read_text())
    cenarios = {nome: v["pt_2p"] for nome, v in g["G2"]["cenarios"].items()}
    v1 = json.loads((paths.REFERENCE / "previsoes" / "previsao_2t_2026_v1.json").read_text())
    b4_v1 = v1["niveis"]["central"]["alvo_nacional"]
    # saldo por eleitor de cada grupo no cenário `perfil` da G2 (para os cruzamentos)
    padrao = g["G2"]["padrao_2022"]
    saldo_g2 = {
        "lula": 1 - padrao["perda_base"],
        "flavio": -(1 - padrao["perda_flavio"]),
        "eliminados": padrao["saldo_eliminados"],
        "branco_nulo": padrao["saldo_bn"],
    }
    cruz = cruzamentos(
        pl.read_csv(paths.REFERENCE / "pesquisas_2t_cruzamentos.csv", try_parse_dates=True),
        institutos,
        saldo_g2,
    )

    media.write_parquet(SAIDA / "media_diaria.parquet")
    pesquisas.write_parquet(SAIDA / "pesquisas_2t.parquet")
    cruz.write_parquet(SAIDA / "cruzamentos.parquet")

    live = resultados.abre_etapa("pesquisas")
    m = resultados.metrica
    ultima = media.row(-1, named=True)
    m(live, "G6/n_pesquisas", pesquisas.height)
    m(live, "G6/n_institutos_na_janela", ultima["institutos"])
    m(live, "G6/ultimo_fim_de_campo", int(ate.strftime("%Y%m%d")))
    m(live, "G6/real_1t", real_1t)
    vies = alvo_das_pesquisas(tabela, real_1t, LAMBDAS["central"], ate)["vies_medio_1t"]
    m(live, "G6/vies_medio_1t", vies)  # erro médio dos institutos na fatia de Lula, 1º turno
    resultados.metricas(
        live,
        "G6/media",
        {
            "bruta": ultima["bruta"],
            "corrigida": ultima["corrigida"],
            "correcao_total": ultima["correcao_total"],
        },
    )
    m(live, "G6/modelo/b4_v1", b4_v1)
    for nome, f in cenarios.items():
        m(live, f"G6/modelo/{nome}", f)
        m(live, f"G6/distancia_pp/{nome}", 100 * (ultima["corrigida"] - f))
    m(live, "G6/distancia_pp/b4_v1", 100 * (ultima["corrigida"] - b4_v1))
    # em votos: margem = (2s − 1) · V, com V = votos dos dois no 1º turno (escala, não previsão)
    v = votos_dos_dois_1t()
    m(live, "G6/votos_dos_dois_1t_mi", v / 1e6)
    for nome in ("bruta", "corrigida", "correcao_total"):
        m(live, f"G6/margem_mi/{nome}", (2 * ultima[nome] - 1) * v / 1e6)
    for nome, f in cenarios.items():
        m(live, f"G6/distancia_mi/{nome}", 2 * (ultima["corrigida"] - f) * v / 1e6)
    for row in pesquisas.iter_rows(named=True):
        chave = f"{resultados.chave(row['instituto'])}_{row['campo_fim'].strftime('%m%d')}"
        resultados.metricas(
            live, f"G6/pesquisas/{chave}", {"s": row["s"], "corrigido": row["corrigido"]}
        )
    m(live, "G6/cruzamentos/n", cruz.height)

    resultados.serie(
        live,
        "G6_media",
        media.select(
            pl.col("data").cast(pl.String), (pl.col("bruta", "corrigida", "correcao_total") * 100)
        ),
        x="data",
        y=["bruta", "corrigida", "correcao_total"],
    )
    resultados.serie(
        live,
        "G6_pesquisas",
        pesquisas.select(
            "instituto", pl.col("campo_fim").cast(pl.String), (pl.col("s", "corrigido") * 100)
        ),
        x="campo_fim",
        y=["s", "corrigido"],
    )
    modelo = pl.DataFrame(
        [
            {
                "rotulo": "pesquisas (média corrigida)",
                "coef": 100 * ultima["corrigida"],
                "ic_inf": 100 * ultima["correcao_total"],
                "ic_sup": 100 * ultima["bruta"],
            },
            {
                "rotulo": "previsão v1 (B4, 8/10)",
                "coef": 100 * b4_v1,
                "ic_inf": 100 * b4_v1,
                "ic_sup": 100 * b4_v1,
            },
        ]
        + [
            {
                "rotulo": f"padrão de 2022: {nome}",
                "coef": 100 * g["G2"]["cenarios"][nome]["pt_2p"],
                "ic_inf": 100 * g["G2"]["cenarios"][nome]["pt_2p_inf"],
                "ic_sup": 100 * g["G2"]["cenarios"][nome]["pt_2p_sup"],
            }
            for nome in cenarios
        ]
    )
    resultados.coeficientes(live, "G6_modelo", modelo)
    live.end()


if __name__ == "__main__":
    executa()
