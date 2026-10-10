from datetime import date

import polars as pl
import pytest

from kingsrace.features import pesquisas as fp
from kingsrace.models.pesquisas import media_diaria

INSTITUTOS = pl.DataFrame(
    {"nome": ["Vox", "Vox Brasil", "Datafolha"], "instituto": ["Vox", "Vox", "Datafolha"]}
)


def _serie(linhas):
    return pl.DataFrame(
        [
            {
                "instituto": i,
                "campo_inicio": f,
                "campo_fim": f,
                "lula": lu,
                "flavio": fl,
                "base": "total",
                "fonte": "x",
            }
            for i, f, lu, fl in linhas
        ]
    )


PRIMEIRO = pl.DataFrame(
    {
        "instituto": ["Vox", "Datafolha"],
        "turno": [1, 1],
        "campo_inicio": [date(2026, 10, 1)] * 2,
        "campo_fim": [date(2026, 10, 1)] * 2,
        "lula": [52.0, 50.0],
        "flavio": [48.0, 50.0],
        "base": ["validos"] * 2,
        "fonte": ["x"] * 2,
    }
)


def test_canoniza_unifica_nomes_e_falha_com_nome_desconhecido():
    s = _serie([("Vox Brasil", date(2026, 10, 7), 44.2, 42.7)])
    assert fp.canoniza(s, INSTITUTOS)["instituto"].to_list() == ["Vox"]
    with pytest.raises(ValueError, match="Ipespe"):
        fp.canoniza(_serie([("Ipespe", date(2026, 10, 7), 47, 53)]), INSTITUTOS)


def test_para_previsao_so_leva_ao_2o_turno_o_que_terminou_depois_do_1o():
    serie = _serie(
        [("Vox Brasil", date(2026, 10, 3), 40, 40), ("Vox Brasil", date(2026, 10, 7), 44.2, 42.7)]
    )
    t = fp.para_previsao(PRIMEIRO, serie, INSTITUTOS)
    assert t.filter(pl.col("turno") == 2)["campo_fim"].to_list() == [date(2026, 10, 7)]
    assert t.filter(pl.col("turno") == 1).height == 2


def test_media_diaria_corrige_pelo_vies_do_proprio_instituto_e_respeita_a_janela():
    serie = _serie(
        [("Vox Brasil", date(2026, 10, 7), 50, 50), ("Datafolha", date(2026, 10, 8), 46, 54)]
    )
    t = fp.para_previsao(PRIMEIRO, serie, INSTITUTOS).with_columns(
        s=pl.col("lula") / (pl.col("lula") + pl.col("flavio"))
    )
    m = media_diaria(t, real_1t=0.50, ate=date(2026, 10, 30))
    dia7 = m.filter(pl.col("data") == date(2026, 10, 7)).row(0, named=True)
    # Vox superestimou Lula em 2 pp no 1º turno: corrigido (λ = 0,5) = 0,50 − 0,01
    assert dia7["institutos"] == 1 and dia7["corrigida"] == pytest.approx(0.49)
    dia8 = m.filter(pl.col("data") == date(2026, 10, 8)).row(0, named=True)
    assert dia8["institutos"] == 2 and dia8["bruta"] == pytest.approx((0.50 + 0.46) / 2)
    # 14 dias depois da última pesquisa ainda conta; no 15º, as duas já saíram da janela
    assert m["data"].max() == date(2026, 10, 22)
