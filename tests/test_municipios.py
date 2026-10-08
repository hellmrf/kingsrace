import polars as pl
import pytest

from kingsrace.harmonize.municipios import ErroCorrespondencia, casa_municipios, normaliza_nome


@pytest.mark.parametrize(
    ("nome", "esperado"),
    [
        ("Olho d'Água das Flores", "OLHO D AGUA DAS FLORES"),
        ("OLHO D ÁGUA DAS FLORES", "OLHO D AGUA DAS FLORES"),
        ("Olhos-d'Água", "OLHOS D AGUA"),
        ("  São   Paulo ", "SAO PAULO"),
    ],
)
def test_normaliza_nome_iguala_grafias_tse_e_ibge(nome, esperado):
    assert normaliza_nome(nome) == esperado


def _ibge():
    return pl.DataFrame(
        {
            "cd_ibge": [2201804, 4302501, 5203559, 2905008],
            "uf": ["PI", "RS", "GO", "BA"],
            "nome": ["Bom Jesus", "Bom Jesus", "Bom Jesus de Goiás", "Barra d'Alcântara"],
        }
    )


def _sem_overrides():
    return pl.DataFrame(schema={"cd_tse": pl.Int64, "cd_ibge": pl.Int64})


def test_casa_por_uf_e_nome():
    tse = pl.DataFrame({"cd_tse": [10, 20], "uf": ["RS", "PI"], "nome": ["BOM JESUS", "BOM JESUS"]})

    res = casa_municipios(tse, _ibge().filter(pl.col("uf") != "GO"), _sem_overrides())

    assert dict(res.select("cd_tse", "cd_ibge").iter_rows()) == {10: 4302501, 20: 2201804}


def test_override_resolve_municipio_renomeado():
    tse = pl.DataFrame({"cd_tse": [92690], "uf": ["GO"], "nome": ["BOM JESUS"]})
    overrides = pl.DataFrame({"cd_tse": [92690], "cd_ibge": [5203559]})

    res = casa_municipios(tse, _ibge(), overrides)

    assert dict(res.select("cd_tse", "cd_ibge").iter_rows()) == {92690: 5203559}


def test_override_prevalece_sobre_casamento_por_nome():
    tse = pl.DataFrame({"cd_tse": [10], "uf": ["PI"], "nome": ["BOM JESUS"]})
    overrides = pl.DataFrame({"cd_tse": [10], "cd_ibge": [2905008]})

    res = casa_municipios(tse, _ibge(), overrides)

    assert dict(res.select("cd_tse", "cd_ibge").iter_rows()) == {10: 2905008}


def test_falha_quando_codigo_tse_fica_sem_par():
    tse = pl.DataFrame({"cd_tse": [1, 2], "uf": ["PI", "SP"], "nome": ["BOM JESUS", "INEXISTENTE"]})

    with pytest.raises(ErroCorrespondencia, match="INEXISTENTE"):
        casa_municipios(tse, _ibge(), _sem_overrides())


def test_falha_quando_dois_codigos_tse_apontam_para_o_mesmo_ibge():
    tse = pl.DataFrame({"cd_tse": [1, 2], "uf": ["PI", "PI"], "nome": ["BOM JESUS", "BOM  JESUS"]})

    with pytest.raises(ErroCorrespondencia, match="2201804"):
        casa_municipios(tse, _ibge(), _sem_overrides())
