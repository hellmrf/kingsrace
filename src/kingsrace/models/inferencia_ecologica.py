"""Matriz de transição entre turnos por inferência ecológica (série G2; depois, a B1).

Em cada seção s, as frações de aptos no 1º turno (origens, x_s) e no 2º (destinos, y_s) se
ligam por y_s ≈ x_s · B, em que B[k, j] é a fração dos eleitores da origem k que foram para o
destino j. B sai de mínimos quadrados ponderados pelos aptos, com B ≥ 0 e cada linha somando 1
(o modelo de Goodman com as restrições contábeis).

O problema só depende das somas X'WX e X'WY, então cada município entra por suas matrizes de
Gram. O bootstrap reamostra municípios e só soma matrizes, sem refazer as contas por seção.
A taxa é suposta constante dentro de cada unidade de estimação (a UF); essa é a principal
fonte de viés, e por isso há uma checagem por faixa de tamanho.
"""

from dataclasses import dataclass

import numpy as np
import polars as pl
from scipy.optimize import minimize


@dataclass(frozen=True)
class Gram:
    """Somas suficientes de um conjunto de seções: X'WX (K×K), X'WY (K×J) e N (votos de origem)."""

    xx: np.ndarray
    xy: np.ndarray
    n: np.ndarray

    def __add__(self, outro: "Gram") -> "Gram":
        return Gram(self.xx + outro.xx, self.xy + outro.xy, self.n + outro.n)


def gram(x: np.ndarray, y: np.ndarray, peso: np.ndarray) -> Gram:
    """x, y: frações por seção (linhas somam 1); peso: aptos. N = Σ peso · x (contagens)."""
    xw = x * peso[:, None]
    return Gram(xw.T @ x, xw.T @ y, xw.sum(axis=0))


def resolve(g: Gram, chute: np.ndarray | None = None) -> np.ndarray:
    """B (K×J) que minimiza Σ w‖y − xB‖² com B ≥ 0 e linhas somando 1.

    As somas são divididas pelo peso total: na escala de votos (~10⁵ ou mais), o SLSQP para no
    ponto de partida e ainda declara sucesso.
    """
    k, j = g.xy.shape
    escala = float(g.n.sum()) or 1.0
    xx, xy = g.xx / escala, g.xy / escala

    def objetivo(v):
        b = v.reshape(k, j)
        r = xx @ b - xy
        return float(np.sum(b * (xx @ b)) - 2 * np.sum(b * xy)), (2 * r).ravel()

    linhas = [
        {
            "type": "eq",
            "fun": lambda v, i=i: v.reshape(k, j)[i].sum() - 1.0,
            "jac": _jac_linha(i, k, j),
        }
        for i in range(k)
    ]
    inicio = np.full(k * j, 1.0 / j) if chute is None else chute.ravel()
    res = minimize(
        objetivo,
        inicio,
        jac=True,
        bounds=[(0.0, 1.0)] * (k * j),
        constraints=linhas,
        method="SLSQP",
        options={"maxiter": 500, "ftol": 1e-14},
    )
    if not res.success:
        raise RuntimeError(f"otimização não convergiu: {res.message}")
    return np.clip(res.x.reshape(k, j), 0.0, 1.0)


def _jac_linha(i: int, k: int, j: int):
    grad = np.zeros((k, j))
    grad[i] = 1.0
    grad = grad.ravel()
    return lambda v: grad


def grams_por_grupo(
    df: pl.DataFrame, origens: list[str], destinos: list[str], grupo: str, peso: str = "aptos"
) -> dict:
    """Gram de cada valor de `grupo` (ex.: município). Colunas de origem e destino em contagem.

    As frações são calculadas aqui: origens sobre a soma das origens, destinos sobre a soma
    dos destinos (cada uma soma o eleitorado da seção no seu turno).
    """
    saida = {}
    for chave, parte in df.group_by(grupo, maintain_order=True):
        xo = parte.select(origens).to_numpy().astype(float)
        yo = parte.select(destinos).to_numpy().astype(float)
        tot_x, tot_y = xo.sum(axis=1), yo.sum(axis=1)
        ok = (tot_x > 0) & (tot_y > 0)
        if not ok.any():
            continue
        saida[chave[0]] = gram(
            xo[ok] / tot_x[ok, None], yo[ok] / tot_y[ok, None], parte[peso].to_numpy()[ok]
        )
    return saida


def estima(
    grams: dict, reps: int = 200, semente: int = 0
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """B pontual e o bootstrap (reps × K × J) reamostrando os grupos (municípios) com reposição.

    Devolve (B, réplicas, N): N são os votos de cada origem no conjunto completo.
    """
    lista = list(grams.values())
    total = _soma(lista)
    b = resolve(total)
    rng = np.random.default_rng(semente)
    replicas = np.empty((reps, *b.shape))
    for r in range(reps):
        contagem = np.bincount(rng.integers(0, len(lista), len(lista)), minlength=len(lista))
        replicas[r] = resolve(_soma(lista, contagem), chute=b)
    return b, replicas, total.n


def _soma(lista: list[Gram], contagem: np.ndarray | None = None) -> Gram:
    if contagem is None:
        contagem = np.ones(len(lista))
    xx = sum(c * g.xx for c, g in zip(contagem, lista, strict=True) if c)
    xy = sum(c * g.xy for c, g in zip(contagem, lista, strict=True) if c)
    n = sum(c * g.n for c, g in zip(contagem, lista, strict=True) if c)
    return Gram(xx, xy, n)


def agrega(bs: list[np.ndarray], ns: list[np.ndarray]) -> np.ndarray:
    """Matriz de várias unidades (UFs), cada linha ponderada pelos votos da origem na unidade."""
    num = sum(n[:, None] * b for b, n in zip(bs, ns, strict=True))
    den = sum(ns)
    return num / np.where(den > 0, den, 1.0)[:, None]
