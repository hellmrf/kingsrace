"""Detalhe da votação por seção e locais de votação do TSE (presidente), para a série G.

Fica fora de `tse.py` para não invalidar as etapas que já dependem dele. O detalhe por seção
traz aptos, comparecimento, brancos e nulos de cada seção, e o nome e o endereço do local; o
cadastro de locais traz bairro e coordenadas (só o de 2026 está ingerido).
"""

from kingsrace import paths
from kingsrace.ingest.tse import csv_zip_para_parquet

DETALHE_SECAO = {
    "ANO_ELEICAO": "SMALLINT",
    "NR_TURNO": "TINYINT",
    "SG_UF": "VARCHAR",
    "CD_MUNICIPIO": "INTEGER",
    "NR_ZONA": "INTEGER",
    "NR_SECAO": "INTEGER",
    "QT_APTOS": "BIGINT",
    "QT_COMPARECIMENTO": "BIGINT",
    "QT_ABSTENCOES": "BIGINT",
    "QT_VOTOS_NOMINAIS": "BIGINT",
    "QT_VOTOS_BRANCOS": "BIGINT",
    "QT_VOTOS_NULOS": "BIGINT",
    "QT_VOTOS_ANULADOS_APU_SEP": "BIGINT",
    "NR_LOCAL_VOTACAO": "INTEGER",
    "NM_LOCAL_VOTACAO": "VARCHAR",
    "DS_LOCAL_VOTACAO_ENDERECO": "VARCHAR",
    "ST_SECAO_INSTALADA": "VARCHAR",
    "ST_SECAO_ANULADA": "VARCHAR",
}

# Coordenadas ficam como texto: o TSE usa vírgula decimal ("-9,9440411").
LOCAL_VOTACAO = {
    "NR_TURNO": "TINYINT",
    "SG_UF": "VARCHAR",
    "CD_MUNICIPIO": "INTEGER",
    "NM_MUNICIPIO": "VARCHAR",
    "NR_ZONA": "INTEGER",
    "NR_SECAO": "INTEGER",
    "DS_TIPO_SECAO_AGREGADA": "VARCHAR",
    "NR_SECAO_PRINCIPAL": "INTEGER",
    "NR_LOCAL_VOTACAO": "INTEGER",
    "NM_LOCAL_VOTACAO": "VARCHAR",
    "DS_TIPO_LOCAL": "VARCHAR",
    "DS_ENDERECO": "VARCHAR",
    "NM_BAIRRO": "VARCHAR",
    "NR_CEP": "VARCHAR",
    "NR_LATITUDE": "VARCHAR",
    "NR_LONGITUDE": "VARCHAR",
    "QT_ELEITOR_SECAO": "INTEGER",
}


def converte_detalhe_secao(ano: int) -> None:
    raw, interim = paths.RAW / "tse", paths.INTERIM / "tse"
    csv_zip_para_parquet(
        raw / "detalhe_votacao_secao" / f"detalhe_votacao_secao_{ano}.zip",
        membro=f"detalhe_votacao_secao_{ano}_BR.csv",  # o _BR só tem presidente
        destino=interim / "detalhe_secao" / f"ano={ano}" / "data.parquet",
        colunas=DETALHE_SECAO,
        filtro="CD_CARGO = '1'",
    )


def converte_locais(ano: int) -> None:
    raw, interim = paths.RAW / "tse", paths.INTERIM / "tse"
    csv_zip_para_parquet(
        raw / "eleitorado_local_votacao" / f"eleitorado_local_votacao_{ano}.zip",
        membro=f"eleitorado_local_votacao_{ano}_BRASIL.csv",
        destino=interim / "locais" / f"ano={ano}" / "data.parquet",
        colunas=LOCAL_VOTACAO,
    )


if __name__ == "__main__":
    import sys

    # python -m kingsrace.ingest.tse_secao detalhe 2022  |  ... locais 2026
    {"detalhe": converte_detalhe_secao, "locais": converte_locais}[sys.argv[1]](int(sys.argv[2]))
