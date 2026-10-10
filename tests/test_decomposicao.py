import polars as pl
import pytest

from kingsrace.features.decomposicao import decompoe_votos


def _base(a0, t0, v0, s0, a1, t1, v1, s1):
    comp0, comp1 = a0 * t0, a1 * t1
    val0, val1 = comp0 * v0, comp1 * v1
    return pl.DataFrame(
        {
            "aptos_de": [a0], "comparecimento_de": [comp0], "validos_de": [val0],
            "votos_de": [val0 * s0],
            "aptos_para": [a1], "comparecimento_para": [comp1], "validos_para": [val1],
            "votos_para": [val1 * s1],
        }
    )  # fmt: skip


def test_so_o_eleitorado_cresce_toda_a_variacao_vai_para_eleitorado():
    # V: 100·0,8·0,9·0,5 = 36 → 110·0,8·0,9·0,5 = 39,6
    r = decompoe_votos(_base(100, 0.8, 0.9, 0.5, 110, 0.8, 0.9, 0.5)).row(0, named=True)

    assert r["delta"] == pytest.approx(3.6)
    assert r["c_eleitorado"] == pytest.approx(3.6)
    assert (r["c_comparecimento"], r["c_validos"], r["c_fatia"]) == pytest.approx((0, 0, 0))


def test_comparecimento_cai_e_fatia_sobe():
    # V: 36 → 100·0,7·0,9·0,6 = 37,8; L = 1,8/ln(1,05) = 36,8926
    # comparecimento: L·ln(0,875) = −4,9264 · fatia: L·ln(1,2) = +6,7262
    r = decompoe_votos(_base(100, 0.8, 0.9, 0.5, 100, 0.7, 0.9, 0.6)).row(0, named=True)

    assert r["delta"] == pytest.approx(1.8)
    assert r["c_comparecimento"] == pytest.approx(-4.9264, abs=1e-3)
    assert r["c_fatia"] == pytest.approx(6.7262, abs=1e-3)
    soma = r["c_eleitorado"] + r["c_comparecimento"] + r["c_validos"] + r["c_fatia"]
    assert soma == pytest.approx(r["delta"])


def test_sem_variacao_nao_divide_por_zero():
    r = decompoe_votos(_base(100, 0.8, 0.9, 0.5, 100, 0.8, 0.9, 0.5)).row(0, named=True)

    assert r["delta"] == 0
    assert r["c_fatia"] == 0
