from datetime import date

import numpy as np
import polars as pl
import pytest

from kingsrace.models.previsao_2t import (
    alvo_das_pesquisas,
    aplica_transferencias,
    calibra_logits,
    calibra_nivel,
    estima_compressao,
    previsoes_por_variante,
)


def _votos():
    linhas = [
        (1, 13, "pt", 100),
        (1, 22, "adversario", 80),
        (1, 70, "outro", 10),
        (1, 55, "outro", 20),
        (1, 95, "branco", 5),
        (1, 28, "anulado", 3),
        (2, 13, "pt", 50),
        (2, 22, "adversario", 50),
        (2, 70, "outro", 0),
    ]
    return pl.DataFrame(linhas, schema=["cd_ibge", "nr_votavel", "papel", "votos"], orient="row")


TAXAS = pl.DataFrame({"nr_votavel": [70, 55], "p_pt": [0.5, 0.1], "p_adv": [0.3, 0.8]})


def test_transferencias_somam_fracoes_dos_eliminados_aos_finalistas():
    res = aplica_transferencias(_votos(), TAXAS).sort("cd_ibge")

    # 1: PT 100 + 0,5·10 + 0,1·20 = 107; adversário 80 + 0,3·10 + 0,8·20 = 99
    assert res.select("cd_ibge", "pt_est", "adv_est").rows() == [
        (1, pytest.approx(107.0), pytest.approx(99.0)),
        (2, pytest.approx(50.0), pytest.approx(50.0)),
    ]


def test_transferencias_falham_se_candidato_eliminado_nao_tem_taxa():
    taxas = TAXAS.filter(pl.col("nr_votavel") != 55)

    with pytest.raises(ValueError, match="55"):
        aplica_transferencias(_votos(), taxas)


def test_calibracao_atinge_o_alvo_nacional_e_preserva_a_ordem():
    pt, adv = np.array([60.0, 20.0, 45.0]), np.array([40.0, 80.0, 55.0])

    c, s = calibra_nivel(pt, adv, alvo=0.50)

    assert np.sum((pt + adv) * s) / np.sum(pt + adv) == pytest.approx(0.50, abs=1e-9)
    assert list(np.argsort(s)) == list(np.argsort(pt / (pt + adv)))
    assert c > 0  # o nível atual (≈0,417) estava abaixo do alvo


def test_calibracao_nao_mexe_quando_o_alvo_e_o_nivel_atual():
    pt, adv = np.array([60.0, 20.0]), np.array([40.0, 80.0])

    c, s = calibra_nivel(pt, adv, alvo=0.40)

    assert c == pytest.approx(0.0, abs=1e-9)
    assert s == pytest.approx([0.6, 0.2])


def _pesquisas():
    linhas = [
        ("A", 1, date(2026, 10, 2), 55.0, 45.0),  # viés de A no 1º turno: 0,55 − 0,50
        ("A", 2, date(2026, 10, 8), 52.0, 48.0),
        ("B", 2, date(2026, 10, 9), 50.0, 50.0),  # B sem pesquisa de 1º turno: viés médio
        ("A", 2, date(2026, 10, 20), 40.0, 60.0),  # depois do corte: ignorada
        ("C", 1, date(2026, 10, 1), 50.0, 50.0),  # viés de C: zero
        ("C", 2, date(2026, 10, 7), 46.0, 54.0),
    ]
    return pl.DataFrame(
        linhas, schema=["instituto", "turno", "campo_fim", "lula", "flavio"], orient="row"
    )


def test_alvo_corrige_cada_instituto_pelo_seu_vies_no_primeiro_turno():
    res = alvo_das_pesquisas(_pesquisas(), pt_2p_1t_real=0.50, lam=0.5, corte=date(2026, 10, 10))

    # viés médio = (0,05 + 0) / 2 = 0,025
    # A: 0,52 − 0,5·0,05 = 0,495 · B: 0,50 − 0,5·0,025 = 0,4875 · C: 0,46 − 0 = 0,46
    assert res["alvo"] == pytest.approx((0.495 + 0.4875 + 0.46) / 3)
    assert res["pesquisas_2t"] == 3


def test_alvo_sem_pesquisa_de_segundo_turno_ate_o_corte_falha():
    with pytest.raises(ValueError, match="2º turno"):
        alvo_das_pesquisas(_pesquisas(), pt_2p_1t_real=0.50, lam=0.5, corte=date(2026, 10, 5))


def test_estima_compressao_recupera_a_inclinacao_entre_turnos():
    rng = np.random.default_rng(0)
    lg1 = rng.normal(0.0, 1.0, 500)
    lg2 = lg1 - 0.09 - 0.014 * (lg1 - lg1.mean())  # deslocamento + compressão

    assert estima_compressao(lg1, lg2) == pytest.approx(-0.014)


def test_calibra_logits_atinge_alvo_com_base_arbitraria():
    base, peso = np.array([0.5, -1.0, 0.0]), np.array([100.0, 300.0, 50.0])

    c, s = calibra_logits(base, peso, alvo=0.45)

    assert np.sum(peso * s) / np.sum(peso) == pytest.approx(0.45, abs=1e-9)


def test_variantes_alinham_transferencias_pelo_municipio_e_nao_pela_ordem():
    # A e B empatados no 1º turno; as transferências favorecem o PT em A e o adversário em B,
    # mas chegam em ordem trocada (B antes de A)
    painel = pl.DataFrame(
        {
            "cd_ibge": [1, 2],
            "uf": ["SP", "SP"],
            "votos_pt": [50, 50],
            "votos_adv": [50, 50],
            "pt_2p": [0.5, 0.5],
            "pt_2p_logit": [0.0, 0.0],
        }
    )
    est = pl.DataFrame({"cd_ibge": [2, 1], "pt_est": [10.0, 90.0], "adv_est": [90.0, 10.0]})
    alvos = {"central": 0.5, "sem_correcao": 0.5, "correcao_total": 0.5}

    res = previsoes_por_variante(painel, est, alvos, compressao=0.0)
    g1 = dict(res.select("cd_ibge", "pt_2p_g1_transferencias").iter_rows())

    assert g1[1] > 0.5 > g1[2]
