import csv

import pytest

from kingsrace.ingest.receita import registra_fonte

FONTE = {
    "versao": "2026-09",
    "arquivo": "Estabelecimentos1.zip",
    "url": "https://exemplo/Estabelecimentos1.zip",
    "md5": "abc",
    "tamanho": 10,
}


def _linhas(arq):
    return list(csv.DictReader(arq.open()))


def test_anota_fonte_nova_em_ordem(tmp_path):
    fontes = tmp_path / "fontes.csv"
    registra_fonte(FONTE, fontes)
    registra_fonte(FONTE | {"arquivo": "Estabelecimentos0.zip", "md5": "def"}, fontes)

    assert [linha["arquivo"] for linha in _linhas(fontes)] == [
        "Estabelecimentos0.zip",
        "Estabelecimentos1.zip",
    ]


def test_mesmo_md5_nao_duplica(tmp_path):
    fontes = tmp_path / "fontes.csv"
    registra_fonte(FONTE, fontes)
    registra_fonte(FONTE, fontes)

    assert len(_linhas(fontes)) == 1


def test_md5_diferente_na_mesma_versao_para_a_ingestao(tmp_path):
    fontes = tmp_path / "fontes.csv"
    registra_fonte(FONTE, fontes)

    with pytest.raises(ValueError, match="mudou na origem"):
        registra_fonte(FONTE | {"md5": "outro"}, fontes)
