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


def test_agrega_amc_sem_nenhum_valor_valido_da_nulo_e_nao_nan():
    cov = pl.DataFrame(
        {"cd_ibge": [11, 12], "populacao": [100.0, 300.0], "pct_sem_religiao": [None, None]},
        schema_overrides={"pct_sem_religiao": pl.Float64},
    )
    municipios = pl.DataFrame({"cd_ibge": [11, 12], "amc_id": [9, 9]})

    res = agrega_covariaveis_amc(cov, municipios)

    assert res["pct_sem_religiao"].to_list() == [None]


def test_deriva_expansao_da_soja_crescimento_evangelico_e_cobertura_de_transferencias():
    base = pl.DataFrame(
        {
            "cd_ibge": [1],
            "populacao": [10_000.0],
            "area_km2": [1_000.0],  # = 100 mil hectares
            "area_soja_2021_ha": [10_000.0],
            "area_soja_2025_ha": [15_000.0],
            "pct_evangelica": [30.0],
            "pct_evangelica_2010": [20.0],
            "familias_ab_2022": [1_000.0],
            "familias_bf_2026": [1_500.0],
        }
    )

    r = deriva_covariaveis(base).row(0, named=True)

    assert r["soja_2021_pct_territorio"] == pytest.approx(10.0)
    assert r["exp_soja_pct_territorio"] == pytest.approx(5.0)
    assert r["delta_evangelica"] == pytest.approx(10.0)
    assert r["familias_ab_100hab_2022"] == pytest.approx(10.0)
    assert r["familias_bf_100hab_2026"] == pytest.approx(15.0)


def test_agrega_amc_soma_contagens_e_recalcula_derivadas_das_somas():
    # 13 foi instalado depois do Censo (sem população), mas tem famílias no Bolsa Família
    cov = pl.DataFrame(
        {
            "cd_ibge": [11, 12, 13],
            "populacao": [100.0, 300.0, None],
            "area_km2": [10.0, 30.0, None],
            "familias_bf_2026": [10.0, 30.0, 5.0],
        }
    )
    municipios = pl.DataFrame({"cd_ibge": [11, 12, 13], "amc_id": [9, 9, 9]})

    r = agrega_covariaveis_amc(cov, municipios).row(0, named=True)

    assert r["familias_bf_2026"] == pytest.approx(45.0)
    assert r["familias_bf_100hab_2026"] == pytest.approx(100 * 45 / 400)
