"""Previsão do 2º turno por município (hipótese B4).

Duas partes, avaliadas separadamente depois da eleição:
- nível nacional: média das pesquisas de 2º turno, corrigida por λ × o viés de cada
  instituto no 1º turno (data/reference/pesquisas_2026.csv);
- geografia: três variantes congeladas juntas, todas calibradas no mesmo nível:
  G0 deslocamento uniforme em logit (central; venceu o backtest de 2022),
  G1 transferências dos eliminados por perfil (data/reference/transferencias_2t.csv),
  G2 uniforme + compressão entre turnos estimada em 2022.

Uso: python -m kingsrace.models.previsao_2t <versão> <data de corte AAAA-MM-DD>
"""

import hashlib
import json
import subprocess
import sys
from datetime import date, datetime

import numpy as np
import polars as pl

from kingsrace import paths

LAMBDAS = {"central": 0.5, "sem_correcao": 0.0, "correcao_total": 1.0}


def aplica_transferencias(votos: pl.DataFrame, taxas: pl.DataFrame) -> pl.DataFrame:
    """Votos estimados de PT e adversário no 2º turno, por município.

    votos: cd_ibge, nr_votavel, papel, votos (1º turno de um ano).
    taxas: nr_votavel, p_pt, p_adv — fração dos eleitores de cada candidato eliminado.
    Falha se algum candidato `outro` com votos não tiver taxa.
    """
    outros = votos.filter((pl.col("papel") == "outro") & (pl.col("votos") > 0))
    sem_taxa = outros.join(taxas, on="nr_votavel", how="anti")["nr_votavel"].unique().to_list()
    if sem_taxa:
        raise ValueError(f"candidatos eliminados sem taxa de transferência: {sorted(sem_taxa)}")

    com_taxa = votos.join(taxas.select("nr_votavel", "p_pt", "p_adv"), on="nr_votavel", how="left")
    papel = pl.col("papel")
    return com_taxa.group_by("cd_ibge").agg(
        pt_est=(
            pl.when(papel == "pt")
            .then(pl.col("votos"))
            .when(papel == "outro")
            .then(pl.col("votos") * pl.col("p_pt"))
            .otherwise(0)
        ).sum(),
        adv_est=(
            pl.when(papel == "adversario")
            .then(pl.col("votos"))
            .when(papel == "outro")
            .then(pl.col("votos") * pl.col("p_adv"))
            .otherwise(0)
        ).sum(),
    )


def _logit(p):
    p = np.clip(p, 1e-9, 1 - 1e-9)
    return np.log(p / (1 - p))


def calibra_nivel(pt: np.ndarray, adv: np.ndarray, alvo: float) -> tuple[float, np.ndarray]:
    """Desloca todos os municípios pelo mesmo `c` em logit até o total nacional ser `alvo`.

    Devolve (c, proporção do PT por município). O total nacional pondera pelos votos
    estimados (pt + adv).
    """
    return calibra_logits(_logit(pt / (pt + adv)), pt + adv, alvo)


def estima_compressao(lg1: np.ndarray, lg2: np.ndarray) -> float:
    """Inclinação b em lg2 − lg1 = c + b·(lg1 − média): b < 0 = compressão entre turnos."""
    centro = lg1 - lg1.mean()
    return float(np.sum(centro * (lg2 - lg1)) / np.sum(centro**2))


def calibra_logits(base: np.ndarray, peso: np.ndarray, alvo: float) -> tuple[float, np.ndarray]:
    """Como `calibra_nivel`, a partir de logits já ajustados e dos pesos de cada município."""

    def nacional(c):
        return np.sum(peso / (1 + np.exp(-(base + c)))) / np.sum(peso)

    baixo, alto = -10.0, 10.0
    for _ in range(200):
        meio = (baixo + alto) / 2
        if nacional(meio) < alvo:
            baixo = meio
        else:
            alto = meio
    c = (baixo + alto) / 2
    return c, 1 / (1 + np.exp(-(base + c)))


def alvo_das_pesquisas(
    pesquisas: pl.DataFrame, pt_2p_1t_real: float, lam: float, corte: date
) -> dict:
    """Nível nacional do PT entre os dois finalistas, segundo as pesquisas corrigidas.

    Para cada instituto, a pesquisa mais recente até `corte`. Viés do instituto = sua fatia
    do PT entre Lula e Flávio na última pesquisa de 1º turno menos o resultado real.
    Corrigido = fatia na pesquisa de 2º turno − λ · viés (viés médio para quem não tem
    pesquisa de 1º turno). Alvo = média dos corrigidos.
    """
    recentes = (
        pesquisas.filter(pl.col("campo_fim") <= corte)
        .with_columns(s=pl.col("lula") / (pl.col("lula") + pl.col("flavio")))
        .sort("campo_fim")
        .group_by("instituto", "turno")
        .last()
    )
    vies = recentes.filter(pl.col("turno") == 1).select(
        "instituto", vies=pl.col("s") - pt_2p_1t_real
    )
    segundo = recentes.filter(pl.col("turno") == 2)
    if segundo.is_empty():
        raise ValueError(f"nenhuma pesquisa de 2º turno até {corte}")

    vies_medio = vies["vies"].mean() if vies.height else 0.0
    detalhe = segundo.join(vies, on="instituto", how="left").with_columns(
        pl.col("vies").fill_null(vies_medio),
        corrigido=pl.col("s") - lam * pl.col("vies").fill_null(vies_medio),
    )
    return {
        "alvo": float(detalhe["corrigido"].mean()),
        "pesquisas_2t": detalhe.height,
        "vies_medio_1t": float(vies_medio),
        "detalhe": detalhe.select("instituto", "campo_fim", "s", "vies", "corrigido").sort(
            "instituto"
        ),
    }


def _sha256(caminho) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def compressao_2022() -> float:
    """Inclinação da compressão entre os turnos de 2022 (aprendida para a variante G2)."""
    p = pl.read_parquet(paths.PROCESSED / "painel_municipio.parquet").filter(pl.col("ano") == 2022)
    t = (
        p.filter(pl.col("turno") == 1)
        .select("cd_ibge", lg1="pt_2p_logit")
        .join(p.filter(pl.col("turno") == 2).select("cd_ibge", lg2="pt_2p_logit"), on="cd_ibge")
    )
    return estima_compressao(t["lg1"].to_numpy(), t["lg2"].to_numpy())


def gera_previsao(versao: str, corte: date) -> None:
    """Grava data/reference/previsoes/previsao_2t_2026_<versão>.{csv,json}.

    Colunas de previsão (fatia do PT entre os dois finalistas):
    - `pt_2p`: central, geografia G0 (deslocamento uniforme), nível com λ = 0,5;
    - `pt_2p_sem_correcao`, `pt_2p_correcao_total`: G0 com λ = 0 e λ = 1;
    - `pt_2p_g1_transferencias`, `pt_2p_g2_compressao`: geografias alternativas, nível central.
    """
    ref = paths.REFERENCE
    votos = pl.read_parquet(paths.PROCESSED / "votos_municipio.parquet").filter(
        (pl.col("ano") == 2026) & (pl.col("turno") == 1) & pl.col("cd_ibge").is_not_null()
    )
    taxas = pl.read_csv(ref / "transferencias_2t.csv").filter(pl.col("ano") == 2026)
    pesquisas = pl.read_csv(ref / "pesquisas_2026.csv", try_parse_dates=True)
    painel = (
        pl.read_parquet(paths.PROCESSED / "painel_municipio.parquet")
        .filter((pl.col("ano") == 2026) & (pl.col("turno") == 1))
        .sort("cd_ibge")
    )
    real_1t = painel["votos_pt"].sum() / (painel["votos_pt"].sum() + painel["votos_adv"].sum())
    pt1 = painel["votos_pt"].to_numpy().astype(float)
    adv1 = painel["votos_adv"].to_numpy().astype(float)
    lg1 = painel["pt_2p_logit"].to_numpy()
    est = painel.select("cd_ibge").join(aplica_transferencias(votos, taxas), on="cd_ibge")
    b = compressao_2022()

    alvos = {
        nome: alvo_das_pesquisas(pesquisas, real_1t, lam, corte) for nome, lam in LAMBDAS.items()
    }
    central = alvos["central"]["alvo"]
    variantes = {
        "pt_2p": calibra_nivel(pt1, adv1, central),
        "pt_2p_sem_correcao": calibra_nivel(pt1, adv1, alvos["sem_correcao"]["alvo"]),
        "pt_2p_correcao_total": calibra_nivel(pt1, adv1, alvos["correcao_total"]["alvo"]),
        "pt_2p_g1_transferencias": calibra_nivel(
            est["pt_est"].to_numpy(), est["adv_est"].to_numpy(), central
        ),
        "pt_2p_g2_compressao": calibra_logits(lg1 + b * (lg1 - lg1.mean()), pt1 + adv1, central),
    }
    previsao = (
        painel.select("cd_ibge", "uf", pt_2p_1t="pt_2p")
        .with_columns(
            *(pl.Series(nome, s) for nome, (_, s) in variantes.items()),
            votos_validos_est=pl.Series(pt1 + adv1).round(0).cast(pl.Int64),
        )
        .with_columns(pl.col("^pt_2p.*$").round(5))
    )

    meta = {
        "versao": versao,
        "corte_pesquisas": corte.isoformat(),
        "gerada_em": datetime.now().astimezone().isoformat(timespec="seconds"),
        "commit": subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=paths.ROOT
        ).stdout.strip(),
        "pt_2p_1t_real": real_1t,
        "compressao_2022": b,
        "deslocamento_logit": {nome: c for nome, (c, _) in variantes.items()},
        "niveis": {
            nome: {
                "lambda": LAMBDAS[nome],
                "alvo_nacional": a["alvo"],
                "pesquisas_2t": a["pesquisas_2t"],
                "vies_medio_1t": a["vies_medio_1t"],
                "detalhe": a["detalhe"]
                .with_columns(pl.col("campo_fim").cast(pl.String))
                .to_dicts(),
            }
            for nome, a in alvos.items()
        },
        "insumos_sha256": {
            f: _sha256(ref / f) for f in ("transferencias_2t.csv", "pesquisas_2026.csv")
        },
    }

    destino = ref / "previsoes"
    destino.mkdir(exist_ok=True)
    csv = destino / f"previsao_2t_2026_{versao}.csv"
    previsao.write_csv(csv)
    meta["previsao_sha256"] = _sha256(csv)
    (destino / f"previsao_2t_2026_{versao}.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf8"
    )
    for nome, a in alvos.items():
        print(f"nível {nome:15s} λ={LAMBDAS[nome]:.1f}  Lula {100 * a['alvo']:.2f}%")
    print(f"compressão 2022: b = {b:+.4f}")
    print(f"{csv} · sha256 {meta['previsao_sha256']}")


if __name__ == "__main__":
    gera_previsao(sys.argv[1], date.fromisoformat(sys.argv[2]))
