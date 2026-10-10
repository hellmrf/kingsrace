import polars as pl
import pytest

from kingsrace.features.mecanismos import e4a_emprego, e5_homicidios, e7a_mei, por_amc_ibge6


def test_por_amc_soma_municipios_e_descarta_ignorados():
    municipios = pl.DataFrame({"cd_ibge": [3550308, 3509502, 3304557], "amc_id": [1, 1, 2]})
    df = pl.DataFrame(
        {"cd_ibge6": [355030, 350950, 330455, 350000], "ano": [2012] * 4, "n": [10, 5, 7, 99]},
        schema_overrides={"cd_ibge6": pl.Int32},
    )

    res = por_amc_ibge6(df, municipios, ["n"])

    assert res.rows() == [(1, 2012, 15), (2, 2012, 7)]


def test_e4a_usa_a_janela_de_cada_transicao():
    anos = [2006, 2009, 2010, 2013, 2014, 2017, 2018, 2021, 2022, 2025]
    emprego = pl.DataFrame(
        {"amc_id": [1] * 10, "ano": anos, "vinculos": [100.0] * 10}
    ).with_columns(vinculos=pl.when(pl.col("ano") == 2017).then(50.0).otherwise(pl.col("vinculos")))

    res = dict(e4a_emprego(emprego).select("de", "x").iter_rows())

    assert res[2014] == pytest.approx(-0.6931, abs=1e-4)  # log(50) − log(100)
    assert res[2010] == 0


def test_e5_taxa_por_100_mil_com_populacao_do_ano_do_meio():
    homic = pl.DataFrame(
        {"amc_id": [1] * 6, "ano": [2011, 2012, 2013, 2015, 2016, 2017], "homicidios": [3] * 6}
    ).with_columns(homicidios=pl.when(pl.col("ano") >= 2015).then(6).otherwise(3))
    cov = pl.DataFrame(
        {"amc_id": [1], **{f"pop_{a}": [100_000] for a in (2004, 2008, 2012, 2016, 2020, 2024)}}
    ).with_columns(pop_2016=pl.lit(200_000))

    res = e5_homicidios(homic, cov).filter(pl.col("de") == 2014)

    # 2011–13: 9 / (3 × 100 mil) = 3 por 100 mil; 2015–17: 18 / (3 × 200 mil) = 3
    assert res["x"].item() == pytest.approx(0.0)


def test_e7a_aberturas_liquidas_sem_2006():
    anos = list(range(2006, 2027))
    cnpj = pl.DataFrame({"amc_id": [1] * len(anos), "ano": anos, "meis_100hab": anos}).cast(
        {"meis_100hab": pl.Float64}
    )

    res = dict(e7a_mei(cnpj).select("de", "x").iter_rows())

    assert res == {2010: 3.0, 2014: 3.0, 2018: 3.0, 2022: 3.0}


def test_e5_transicao_sem_dados_do_trienio_fica_de_fora():
    # só 2011–2017: a transição 2014 tem os dois triênios; a 2010 (2007–09 → 2011–13) não
    homic = pl.DataFrame(
        {"amc_id": [1] * 6, "ano": [2011, 2012, 2013, 2015, 2016, 2017], "homicidios": [3] * 6}
    )
    cov = pl.DataFrame(
        {"amc_id": [1], **{f"pop_{a}": [100_000] for a in (2004, 2008, 2012, 2016, 2020, 2024)}}
    )

    assert e5_homicidios(homic, cov)["de"].to_list() == [2014]


def test_e5_populacao_zero_fica_sem_taxa():
    homic = pl.DataFrame(
        {"amc_id": [1] * 6, "ano": [2011, 2012, 2013, 2015, 2016, 2017], "homicidios": [0] * 6}
    )
    cov = pl.DataFrame(
        {"amc_id": [1], **{f"pop_{a}": [100_000] for a in (2004, 2008, 2016, 2020, 2024)}}
    ).with_columns(pop_2012=pl.lit(0))

    assert e5_homicidios(homic, cov).height == 0
