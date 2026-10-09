import polars as pl
import pytest

from kingsrace.ingest.ibge import sidra_para_tabela

CABECALHO = {
    "NC": "Nível Territorial (Código)",
    "V": "Valor",
    "D1C": "Município (Código)",
    "D2C": "Variável (Código)",
    "D3C": "Ano (Código)",
    "D4C": "Religião (Código)",
}


def _linha(mun, var, ano, cat, valor):
    return {"NC": "6", "V": valor, "D1C": mun, "D2C": var, "D3C": ano, "D4C": cat}


COLUNAS = {
    ("1000140", "2022", "95277"): "pct_evangelica",
    ("1000140", "2022", "2836"): "pct_sem_religiao",
}


def test_converte_resposta_do_sidra_em_tabela_larga_por_municipio():
    linhas = [
        CABECALHO,
        _linha("3550308", "1000140", "2022", "95277", "23.17"),
        _linha("3550308", "1000140", "2022", "2836", "13.49"),
        _linha("3550308", "1000140", "2022", "95263", "50.72"),  # não pedida: ignorada
        _linha("1100015", "1000140", "2022", "95277", "41.10"),
        _linha("1100015", "1000140", "2022", "2836", "..."),
    ]

    res = sidra_para_tabela(linhas, COLUNAS).sort("cd_ibge")

    assert res.schema["cd_ibge"] == pl.Int64
    assert res.columns == ["cd_ibge", "pct_evangelica", "pct_sem_religiao"]
    assert res.rows() == [(1100015, 41.10, None), (3550308, 23.17, 13.49)]


def test_traco_e_zero_absoluto_na_convencao_do_ibge():
    linhas = [
        CABECALHO,
        _linha("1", "1000140", "2022", "95277", "-"),
        _linha("1", "1000140", "2022", "2836", "1.0"),
    ]

    assert sidra_para_tabela(linhas, COLUNAS)["pct_evangelica"].to_list() == [0.0]


@pytest.mark.parametrize("suprimido", ["...", "X", ".."])
def test_valores_suprimidos_viram_nulos(suprimido):
    linhas = [
        CABECALHO,
        _linha("1", "1000140", "2022", "95277", suprimido),
        _linha("1", "1000140", "2022", "2836", "1.0"),
    ]

    assert sidra_para_tabela(linhas, COLUNAS)["pct_evangelica"].to_list() == [None]


def test_falha_quando_coluna_pedida_nao_aparece_na_resposta():
    linhas = [CABECALHO, _linha("1", "1000140", "2022", "95277", "1.0")]

    with pytest.raises(ValueError, match="pct_sem_religiao"):
        sidra_para_tabela(linhas, COLUNAS)
