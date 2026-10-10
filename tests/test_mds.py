import polars as pl
import pytest

from kingsrace.ingest.mds import le_misocial

CSV = (
    "codigo_ibge,anomes,qtd_familias_beneficiarias_bolsa_familia_i\n"
    "210173,202609,2026\n"
    "355030,202609,500000\n"
)


def test_converte_codigo_de_6_digitos_e_renomeia_colunas(tmp_path):
    arq = tmp_path / "bf.csv"
    arq.write_text(CSV)
    codigos = pl.Series([2101731, 3550308, 1100015])

    res = le_misocial(arq, {"qtd_familias_beneficiarias_bolsa_familia_i": "familias_bf"}, codigos)

    assert res.sort("cd_ibge").rows() == [(2101731, 2026.0), (3550308, 500000.0)]
    assert res.columns == ["cd_ibge", "familias_bf"]


def test_falha_com_codigo_sem_municipio_correspondente(tmp_path):
    arq = tmp_path / "bf.csv"
    arq.write_text(CSV)

    with pytest.raises(ValueError, match="355030"):
        le_misocial(arq, {"qtd_familias_beneficiarias_bolsa_familia_i": "f"}, pl.Series([2101731]))
