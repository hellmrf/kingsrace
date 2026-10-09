import polars as pl
import pytest

from kingsrace.features.religiao import OCUPACAO_RELIGIOSA, eh_religioso, religiosos_amc


@pytest.mark.parametrize(
    ("nome", "ocupacao", "esperado"),
    [
        ("PASTOR EURICO", "EMPRESÁRIO", True),
        ("Pastora Jerusa", "OUTROS", True),
        ("PR. MARCOS", None, True),
        ("PR JOÃO", "OUTROS", True),
        ("BISPO JOSÉ LUIZ", OCUPACAO_RELIGIOSA, True),
        ("APOSTOLO CESAR", "OUTROS", True),
        ("MISSIONÁRIA MICHELE", "OUTROS", True),
        ("PRESBÍTERO ANTÔNIO", "OUTROS", True),
        ("ZE PILINTRA", OCUPACAO_RELIGIOSA, True),  # ocupação basta, sem título
        ("PADRE JADER PEREIRA", OCUPACAO_RELIGIOSA, False),  # católico fica de fora
        ("FREI ANASTÁCIO", OCUPACAO_RELIGIOSA, False),
        ("JOÃO BISPO", "COMERCIANTE", False),  # sobrenome, não título
        ("PASTORAL DA TERRA", "OUTROS", False),
        ("PRISCILA SANTOS", "ADVOGADO", False),
        ("PR", "OUTROS", False),
        ("MARCO FELICIANO", None, False),  # sem título nem ocupação: não conta
    ],
)
def test_regra_da_e2c(nome, ocupacao, esperado):
    df = pl.DataFrame(
        {"nm_urna_candidato": [nome], "ds_ocupacao": [ocupacao]},
        schema={"nm_urna_candidato": pl.String, "ds_ocupacao": pl.String},
    )
    assert df.select(eh_religioso()).item() is esperado


def _entrada():
    votos = pl.DataFrame(
        {
            "ano_eleicao": [2014] * 4,
            "sg_uf": ["SP"] * 4,
            "cd_municipio": [1, 1, 2, 3],
            "sq_candidato": [10, 11, 10, 12],
            "nm_urna_candidato": ["PASTOR A", "B", "PASTOR A", "C"],
            "votos_validos": [30, 70, 5, 40],
        }
    )
    candidatos = pl.DataFrame(
        {
            "ano_eleicao": [2014, 2014],
            "sg_uf": ["SP", "SP"],
            "sq_candidato": [10, 11],  # o 12 não está no cadastro
            "ds_ocupacao": ["OUTROS", "OUTROS"],
        }
    )
    detalhe = pl.DataFrame(
        {
            "ano_eleicao": [2014] * 3,
            "cd_municipio": [1, 2, 3],
            "qt_total_votos_validos": [110, 10, 50],  # inclui votos de legenda
        }
    )
    municipios = pl.DataFrame({"cd_tse": [1, 2, 3], "amc_id": [100, 100, 300]})
    return votos, candidatos, detalhe, municipios


def test_agrega_por_amc_com_validos_de_deputado():
    res = religiosos_amc(*_entrada())

    assert res.select("amc_id", "ano", "votos_religiosos", "validos_deputado").rows() == [
        (100, 2014, 35, 120),
        (300, 2014, 0, 50),
    ]
    assert res["pct_religiosos"].to_list() == pytest.approx([100 * 35 / 120, 0.0])


def test_falha_com_municipio_sem_amc():
    votos, candidatos, detalhe, municipios = _entrada()

    with pytest.raises(ValueError, match="3"):
        religiosos_amc(votos, candidatos, detalhe, municipios.filter(pl.col("cd_tse") != 3))
