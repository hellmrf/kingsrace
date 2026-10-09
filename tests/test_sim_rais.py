import struct

import polars as pl

from kingsrace.ingest.rais import colunas
from kingsrace.ingest.sim import conta_homicidios, le_dbf


def _dbf(caminho, campos, registros, excluidos=()):
    """Escreve um DBF mínimo: campos de texto (nome, tamanho) e registros."""
    largura = 1 + sum(t for _, t in campos)
    cabecalho = 32 + 32 * len(campos) + 1
    dados = bytearray(struct.pack("<BBBBIHH20x", 3, 26, 1, 1, len(registros), cabecalho, largura))
    for nome, tam in campos:
        dados += nome.encode().ljust(11, b"\0") + b"C" + b"\0" * 4 + bytes([tam, 0]) + b"\0" * 14
    dados += b"\r"
    for i, r in enumerate(registros):
        dados += b"*" if i in excluidos else b" "
        for (_, tam), valor in zip(campos, r, strict=True):
            dados += valor.encode().ljust(tam)
    caminho.write_bytes(bytes(dados) + b"\x1a")


def test_le_dbf_campos_pedidos_sem_excluidos(tmp_path):
    arq = tmp_path / "x.dbf"
    campos = [("DTOBITO", 8), ("CAUSABAS", 4), ("CODMUNRES", 6)]
    _dbf(
        arq,
        campos,
        [
            ("01012012", "X954", "355030"),
            ("02012012", "I219", "120040"),
            ("03012012", "Y350", "330455"),
        ],
        excluidos={1},
    )

    res = le_dbf(arq, ["CAUSABAS", "CODMUNRES"])

    assert res.rows() == [("X954", "355030"), ("Y350", "330455")]


def test_homicidio_e_agressao_mais_intervencao_legal():
    obitos = pl.DataFrame(
        {
            "CAUSABAS": ["X850", "X999", "Y099", "Y350", "Y369", "Y100", "X849", "W748", "Y370"],
            "CODMUNRES": ["355030"] * 9,
        }
    )

    res = conta_homicidios(obitos, 2012)

    assert res.select("cd_ibge6", "homicidios", "ano").rows() == [(355030, 5, 2012)]


def test_rais_acha_colunas_nos_dois_layouts(tmp_path):
    antigo = tmp_path / "a.txt"
    antigo.write_text(
        "CNAE 2.0 Classe;Qtd Vínculos Ativos;Município;CNAE 2.0 Subclasse\n", encoding="latin-1"
    )
    novo = tmp_path / "b.txt"
    novo.write_text(
        '"Qtd Vínculos Ativos","Município - Código","CNAE 2.0 Subclasse - Codigo"\n',
        encoding="latin-1",
    )

    assert colunas(antigo) == (
        ";",
        {
            "municipio": "Município",
            "vinculos": "Qtd Vínculos Ativos",
            "subclasse": "CNAE 2.0 Subclasse",
        },
    )
    assert colunas(novo)[0] == ","
    assert colunas(novo)[1]["municipio"] == "Município - Código"
