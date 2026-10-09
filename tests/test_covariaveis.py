import polars as pl
import pytest

from kingsrace.features.covariaveis import agrega_covariaveis_amc, deriva_covariaveis


def test_deriva_per_capita_participacoes_e_preta_parda():
    base = pl.DataFrame(
        {
            "cd_ibge": [1],
            "populacao": [100.0],
            "pib_2023": [1000.0],  # mil reais
            "va_2023": [120.0],
            "va_agro_2023": [30.0],
            "va_adm_2023": [12.0],
            "pct_preta": [10.0],
            "pct_parda": [40.0],
        }
    )

    r = deriva_covariaveis(base).row(0, named=True)

    assert r["pib_pc_2023"] == pytest.approx(10_000.0)  # reais por habitante
    assert r["pct_va_agro_2023"] == pytest.approx(25.0)
    assert r["pct_va_adm_2023"] == pytest.approx(10.0)
    assert r["pct_preta_parda"] == pytest.approx(50.0)


def test_agrega_amc_soma_populacao_e_pondera_taxas_pela_populacao():
    cov = pl.DataFrame(
        {
            "cd_ibge": [11, 12, 13, 20],
            "populacao": [100.0, 300.0, None, 50.0],  # 13: instalado depois do Censo
            "area_km2": [10.0, 30.0, None, 5.0],
            "pct_evangelica": [10.0, 30.0, None, 40.0],
        }
    )
    municipios = pl.DataFrame({"cd_ibge": [11, 12, 13, 20], "amc_id": [9, 9, 9, 20]})

    res = agrega_covariaveis_amc(cov, municipios).sort("amc_id")

    assert res.select("amc_id", "populacao", "area_km2").rows() == [
        (9, 400.0, 40.0),
        (20, 50.0, 5.0),
    ]
    assert res["pct_evangelica"].to_list() == pytest.approx([25.0, 40.0])
    assert res["densidade"].to_list() == pytest.approx([10.0, 10.0])


def test_participacao_no_va_e_nula_quando_va_total_nao_e_positivo():
    # Cachoeira Dourada (GO), 2021: VA total negativo (usina hidrelétrica na crise hídrica)
    base = pl.DataFrame(
        {"cd_ibge": [1], "va_2021": [-227726.0], "va_agro_2021": [95420.0], "va_adm_2021": [1.0]}
    )

    r = deriva_covariaveis(base).row(0, named=True)

    assert (r["pct_va_agro_2021"], r["pct_va_adm_2021"]) == (None, None)
