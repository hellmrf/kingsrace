import zipfile

import polars as pl

from kingsrace.ingest.tse import csv_zip_para_parquet

CSV_TSE = (
    '"ANO_ELEICAO";"NR_TURNO";"NM_MUNICIPIO";"CD_CARGO";"QT_VOTOS";"DS_IGNORADA"\n'
    '"2022";"1";"SELVÍRIA";"1";"138";"x"\n'
    "2022;1;JOÃO PESSOA;1;7;y\n"
    '"2022";"1";"SELVÍRIA";"3";"99";"z"\n'
)


def _zip_tse(tmp_path):
    caminho = tmp_path / "amostra.zip"
    with zipfile.ZipFile(caminho, "w") as z:
        z.writestr("amostra_BR.csv", CSV_TSE.encode("latin-1"))
        z.writestr("leiame.pdf", b"%PDF")
    return caminho


def test_converte_csv_latin1_do_zip_em_parquet_tipado_e_filtrado(tmp_path):
    destino = tmp_path / "saida" / "data.parquet"

    csv_zip_para_parquet(
        _zip_tse(tmp_path),
        membro="amostra_BR.csv",
        destino=destino,
        colunas={
            "ANO_ELEICAO": "SMALLINT",
            "NR_TURNO": "TINYINT",
            "NM_MUNICIPIO": "VARCHAR",
            "QT_VOTOS": "INTEGER",
        },
        filtro="CD_CARGO = '1'",
    )

    df = pl.read_parquet(destino)
    assert df.columns == ["ano_eleicao", "nr_turno", "nm_municipio", "qt_votos"]
    assert df.schema["qt_votos"] == pl.Int32
    assert df.rows() == [(2022, 1, "SELVÍRIA", 138), (2022, 1, "JOÃO PESSOA", 7)]
