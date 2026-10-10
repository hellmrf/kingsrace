from datetime import date

import polars as pl
import pytest

from kingsrace import paths
from kingsrace.features.cnpj import ativas_em, classifica


@pytest.fixture(scope="module")
def regras():
    return pl.read_csv(paths.REFERENCE / "denominacoes.csv")


@pytest.mark.parametrize(
    ("razao", "grupo", "denominacao"),
    [
        ("IGREJA EVANGELICA ASSEMBLEIA DE DEUS EM CAMPINAS", "evangelica", "Assembleia de Deus"),
        ("Igreja Evangélica Assembléia de Deus", "evangelica", "Assembleia de Deus"),
        ("IGREJA UNIVERSAL DO REINO DE DEUS", "evangelica", "Universal do Reino de Deus"),
        ("IGREJA BATISTA DA LAGOINHA", "evangelica", "Lagoinha"),  # antes de "Batista"
        ("PRIMEIRA IGREJA BATISTA EM SOBRAL", "evangelica", "Batista"),
        ("MINISTERIO APOSTOLICO FONTE DE VIDA", "evangelica", "Evangélica (genérica)"),
        ("COMUNIDADE EVANGELICA SARA NOSSA TERRA", "evangelica", "Sara Nossa Terra"),
        ("MITRA DIOCESANA DE CAMPOS", "catolica", "Católica"),
        ("PAROQUIA SAO JOSE", "catolica", "Católica"),
        ("IGREJA CATOLICA APOSTOLICA BRASILEIRA", "catolica", "Católica"),
        ("IGREJA MESSIANICA MUNDIAL DO BRASIL", "outra", "Outras religiões"),
        (
            "A IGREJA DE JESUS CRISTO DOS SANTOS DOS ULTIMOS DIAS",
            "outra",
            "Santos dos Últimos Dias (mórmons)",
        ),
        ("CENTRO ESPIRITA AMOR E CARIDADE", "espirita_afro", "Espírita ou espiritualista"),
        ("TENDA DE UMBANDA PAI JOAO", "espirita_afro", "Matriz africana"),
        ("ASSOCIACAO DE MORADORES DO BAIRRO", "indefinida", "Indefinida"),
    ],
)
def test_classifica_pela_primeira_regra_que_casa(regras, razao, grupo, denominacao):
    res = classifica(pl.DataFrame({"razao_social": [razao]}), regras)

    assert res.row(0, named=True) == {
        "razao_social": razao,
        "grupo": grupo,
        "denominacao": denominacao,
    }


def test_ativas_em_31_de_dezembro():
    df = pl.DataFrame(
        {
            "id": [1, 2, 3, 4],
            "data_inicio": [
                date(2010, 5, 1),
                date(2014, 12, 31),
                date(2015, 1, 1),
                date(2008, 1, 1),
            ],
            "data_fim": [None, date(2016, 6, 1), None, date(2014, 12, 31)],
        }
    )

    res = ativas_em(df, anos=[2013, 2014, 2015, 2016])

    anos = dict(res.group_by("id").agg(pl.col("ano").sort()).iter_rows())
    assert anos == {1: [2013, 2014, 2015, 2016], 2: [2014, 2015], 3: [2015, 2016], 4: [2013]}
