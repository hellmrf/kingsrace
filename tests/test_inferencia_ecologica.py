import numpy as np
import polars as pl
import pytest

from kingsrace.models.inferencia_ecologica import agrega, estima, grams_por_grupo, resolve

B_VERDADE = np.array(
    [
        [0.95, 0.01, 0.01, 0.03],  # finalista A
        [0.01, 0.95, 0.01, 0.03],  # finalista B
        [0.50, 0.30, 0.10, 0.10],  # eliminado
        [0.10, 0.15, 0.05, 0.70],  # abstenção
    ]
)


def _secoes(n_mun=300, por_mun=8, ruido=0.0, semente=1):
    rng = np.random.default_rng(semente)
    linhas = []
    for m in range(n_mun):
        base = rng.dirichlet([6, 5, 1.5, 3])
        for _ in range(por_mun):
            x = rng.dirichlet(base * 40)
            aptos = int(rng.integers(150, 400))
            y = x @ B_VERDADE + rng.normal(0, ruido, 4)
            y = np.clip(y, 1e-6, None)
            y = y / y.sum()
            o, d = np.round(x * aptos).astype(int), np.round(y * aptos).astype(int)
            linhas.append({"mun": m, "aptos": aptos, **{f"o{i}": o[i] for i in range(4)},
                           **{f"d{i}": d[i] for i in range(4)}})  # fmt: skip
    return pl.DataFrame(linhas)


ORIGENS, DESTINOS = [f"o{i}" for i in range(4)], [f"d{i}" for i in range(4)]


def test_recupera_matriz_conhecida_sem_ruido():
    g = grams_por_grupo(_secoes(), ORIGENS, DESTINOS, "mun")
    b, _, _ = estima(g, reps=0)
    assert np.abs(b - B_VERDADE).max() < 0.02
    assert np.allclose(b.sum(axis=1), 1.0)


def test_ic_do_bootstrap_cobre_a_verdade_com_ruido():
    g = grams_por_grupo(_secoes(ruido=0.01), ORIGENS, DESTINOS, "mun")
    b, reps, n = estima(g, reps=60, semente=3)
    inf, sup = np.percentile(reps, [2.5, 97.5], axis=0)
    verdade = B_VERDADE
    dentro = (inf - 0.01 <= verdade) & (verdade <= sup + 0.01)
    cobertos = dentro.mean()
    assert cobertos >= 0.85
    assert (reps >= 0).all() and np.allclose(reps.sum(axis=2), 1.0)
    assert n.shape == (4,)


def test_restricoes_valem_mesmo_quando_o_mqo_livre_sairia_do_intervalo():
    # destino quase todo explicado pela origem 0: o MQO livre daria pesos negativos
    from kingsrace.models.inferencia_ecologica import Gram

    xx = np.array([[2.0, 1.0], [1.0, 2.0]])
    xy = np.array([[2.5, -0.5], [0.4, 1.6]])
    b = resolve(Gram(xx, xy, np.ones(2)))
    assert (b >= 0).all() and np.allclose(b.sum(axis=1), 1.0)


def test_agrega_pondera_cada_linha_pelos_votos_da_origem():
    b1, b2 = np.array([[1.0, 0.0]]), np.array([[0.0, 1.0]])
    res = agrega([b1, b2], [np.array([3.0]), np.array([1.0])])
    assert res == pytest.approx(np.array([[0.75, 0.25]]))
