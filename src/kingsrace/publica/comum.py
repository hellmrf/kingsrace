"""Leitura das saídas do DVC, formato brasileiro e gravação determinística (D12)."""

import json
import math
from pathlib import Path
from typing import Any

import polars as pl

from kingsrace import paths

RESULTADOS = paths.ROOT / "resultados"
SITE = paths.ROOT / "site"
DADOS = SITE / "dados"
MENOS = "−"  # sinal de menos tipográfico


def metricas(etapa: str) -> dict:
    """metrics.json de uma etapa do DVC (módulo ou notebook)."""
    return json.loads((RESULTADOS / etapa / "metrics.json").read_text())


def metrica(m: dict, caminho: str) -> Any:
    """Valor de `m` no caminho 'G1/diferenca_mi'; falha com o caminho inteiro se faltar."""
    atual = m
    for parte in caminho.split("/"):
        if not isinstance(atual, dict) or parte not in atual:
            raise KeyError(f"métrica ausente: {caminho}")
        atual = atual[parte]
    return atual


def grafico(etapa: str, nome: str) -> list[dict]:
    """Dados de um gráfico declarado no dvc.yaml (plots/custom/<nome>.json)."""
    return json.loads((RESULTADOS / etapa / "plots" / "custom" / f"{nome}.json").read_text())


def oficial(ano: int, turno: int, nr_votavel: int) -> int:
    """Total oficial do TSE (data/reference/totais_oficiais.csv)."""
    t = pl.read_csv(paths.REFERENCE / "totais_oficiais.csv").filter(
        (pl.col("ano") == ano) & (pl.col("turno") == turno) & (pl.col("nr_votavel") == nr_votavel)
    )
    if t.height != 1:
        raise KeyError(f"total oficial ausente: {ano}, {turno}º turno, nº {nr_votavel}")
    return int(t["votos"].item())


def br(x: float, casas: int = 1) -> str:
    """Número no padrão brasileiro: 1.234,5 e −0,3."""
    texto = f"{abs(x):,.{casas}f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return (MENOS if round(x, casas) < 0 else "") + texto


def sinal(x: float, casas: int = 1) -> str:
    """Como `br`, com + nos positivos."""
    return ("+" if round(x, casas) > 0 else "") + br(x, casas)


def pct(fracao: float, casas: int = 1) -> str:
    """Fração como porcentagem: 0,037 → '3,7%'."""
    return br(100 * fracao, casas) + "%"


def mi(milhoes: float, casas: int = 1) -> str:
    """Milhões de votos por extenso curto: 2,2 → '2,2 milhões'; 1,0 → '1,0 milhão'."""
    return br(milhoes, casas) + (" milhão" if round(abs(milhoes), casas) < 2 else " milhões")


def mil(milhares: float) -> str:
    """Milhares arredondados: 186,7 → '187 mil'."""
    return br(milhares, 0) + " mil"


def _limpa(obj: Any) -> Any:
    if isinstance(obj, float):
        if not math.isfinite(obj):
            raise ValueError("valor não finito nos dados do site")
        return round(obj, 6)
    if isinstance(obj, dict):
        return {str(k): _limpa(v) for k, v in obj.items()}
    if isinstance(obj, list | tuple):
        return [_limpa(v) for v in obj]
    return obj


def grava_json(caminho: Path, obj: Any) -> None:
    """JSON determinístico: chaves ordenadas, floats com 6 casas, sem NaN, UTF-8."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    texto = json.dumps(_limpa(obj), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    caminho.write_text(texto + "\n", encoding="utf-8")
