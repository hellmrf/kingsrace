import polars as pl
import pytest

from kingsrace.features.secao import (
    casa_locais,
    coordenadas,
    monta_painel_secao,
    votos_por_secao,
)

CANDIDATOS = pl.DataFrame(
    {
        "ano": [2026, 2026, 2026],
        "nr_votavel": [13, 22, 28],
        "papel": ["pt", "adversario", "anulado"],
    }
).with_columns(pl.col("ano").cast(pl.Int16))
GRUPOS = pl.DataFrame(
    {"ano": [2026, 2026], "nr_votavel": [70, 80], "grupo": ["cury", "esquerda"]}
).with_columns(pl.col("ano").cast(pl.Int16))
SECAO = {"ano": 2026, "turno": 1, "uf": "AC", "cd_tse": 1392, "zona": 9}


def _votos(linhas):
    return pl.DataFrame(
        [{**SECAO, "secao": s, "nr_votavel": n, "votos": v} for s, n, v in linhas]
    ).with_columns(pl.col("ano").cast(pl.Int16), pl.col("turno").cast(pl.Int8))


def test_votos_por_secao_separa_finalistas_e_grupos_e_ignora_branco_nulo_anulado():
    votos = _votos(
        [(1, 13, 10), (1, 22, 7), (1, 70, 3), (1, 80, 1), (1, 95, 2), (1, 96, 4), (1, 28, 5)]
    )

    res = votos_por_secao(votos, CANDIDATOS, GRUPOS).row(0, named=True)

    assert (res["votos_pt"], res["votos_adv"], res["votos_outros"]) == (10, 7, 4)
    assert (res["votos_cury"], res["votos_esquerda"]) == (3, 1)


def test_votos_por_secao_falha_com_eliminado_sem_grupo():
    with pytest.raises(ValueError, match="sem grupo"):
        votos_por_secao(_votos([(1, 13, 10), (1, 14, 2)]), CANDIDATOS, GRUPOS)


def _detalhe(secoes):
    return pl.DataFrame(
        [{**SECAO, "secao": s, "nr_local": 1023, "aptos": a, "comparecimento": c,
          "abstencoes": a - c, "brancos": b, "validos": v} for s, a, c, b, v in secoes]
    ).with_columns(pl.col("ano").cast(pl.Int16), pl.col("turno").cast(pl.Int8))  # fmt: skip


MUNICIPIOS = pl.DataFrame({"cd_tse": [1392], "cd_ibge": [1200401], "amc_id": [1200401]})


def test_painel_secao_zera_votos_de_secao_sem_votacao_e_calcula_nulos_por_residuo():
    votos = votos_por_secao(_votos([(1, 13, 10), (1, 22, 7), (1, 70, 3)]), CANDIDATOS, GRUPOS)
    detalhe = _detalhe([(1, 30, 25, 1, 20), (2, 10, 0, 0, 0)])

    painel = monta_painel_secao(votos, detalhe, MUNICIPIOS)

    s1, s2 = painel.rows(named=True)
    assert s1["nulos"] == 25 - 20 - 1 and s1["cd_ibge"] == 1200401
    assert (s2["votos_pt"], s2["votos_adv"], s2["validos"]) == (0, 0, 0)


def test_painel_secao_falha_se_votos_nao_somam_os_validos():
    votos = votos_por_secao(_votos([(1, 13, 10), (1, 22, 7)]), CANDIDATOS, GRUPOS)

    with pytest.raises(ValueError, match="≠ válidos"):
        monta_painel_secao(votos, _detalhe([(1, 30, 25, 1, 18)]), MUNICIPIOS)


def test_coordenadas_le_virgula_decimal_e_anula_fora_do_brasil():
    locais = pl.DataFrame(
        {
            "nr_turno": [1, 1, 2, 1],
            "sg_uf": ["AC"] * 4,
            "cd_municipio": [1392] * 4,
            "nr_zona": [9] * 4,
            "nr_local_votacao": [1554, 1023, 1554, 1040],
            "ds_tipo_secao_agregada": ["Principal"] * 4,
            "nm_bairro": ["X", "Y", "X", "Z"],
            "nr_cep": ["1"] * 4,
            "ds_tipo_local": ["Convencional"] * 4,
            "nr_latitude": ["-9,9440411", "0", "-9,9440411", "-9,98"],
            "nr_longitude": ["-67,8709324", "0", "-67,8709324", "-67,82"],
        }
    ).with_columns(pl.col("nr_turno").cast(pl.Int8))

    res = coordenadas(locais).sort("nr_local")

    assert res["nr_local"].to_list() == [1023, 1040, 1554]  # 2º turno descartado
    assert res.filter(pl.col("nr_local") == 1554)["lat"].item() == pytest.approx(-9.9440411)
    assert res.filter(pl.col("nr_local") == 1023)["lat"].item() is None  # (0, 0) é o Atlântico


def test_casa_locais_exige_o_mesmo_nome_alem_do_numero():
    de = pl.DataFrame(
        {"cd_tse": [1, 1], "zona": [9, 9], "nr_local": [10, 20],
         "nm_local": ["Escola Estadual João", "EMEF Maria"], "votos": [5, 6]}
    )  # fmt: skip
    para = pl.DataFrame(
        {"cd_tse": [1, 1], "zona": [9, 9], "nr_local": [10, 20],
         "nm_local": ["ESCOLA ESTADUAL  JOAO", "Centro Comunitário"], "votos": [7, 8]}
    )  # fmt: skip

    res = casa_locais(de, para)

    assert res.select("nr_local", "votos", "votos_para").rows() == [(10, 5, 7)]


def test_centro_eleitoral_pondera_pelos_aptos_e_ignora_local_sem_coordenada():
    from kingsrace.features.coordenadas import centros

    locais = pl.DataFrame(
        {
            "cd_ibge": [1, 1, 1],
            "aptos": [300, 100, 500],
            "lat": [-10.0, -12.0, None],
            "lon": [-40.0, -44.0, -50.0],
        }
    )
    c = centros(locais, "cd_ibge").row(0, named=True)
    assert c["lat"] == pytest.approx(-10.5) and c["lon"] == pytest.approx(-41.0)
    assert c["locais_com_coordenada"] == 2
