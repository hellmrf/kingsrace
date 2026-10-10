"""Bolsa Família e Auxílio Brasil por município (MDS, serviço MiSocial/VIS DATA).

Arquivos brutos em data/raw/mds/ (dvc import-url das consultas em CONSULTAS).
O MiSocial identifica o município pelo código IBGE de 6 dígitos (sem o verificador).
"""

from pathlib import Path

import polars as pl

MISOCIAL = "https://aplicacoes.mds.gov.br/sagi/servicos/misocial"

# arquivo: colunas do MiSocial → nomes no projeto
CONSULTAS = {
    "auxilio_brasil_202209.csv": {
        "pab_qtd_fam_benef_i": "familias_ab_2022",
        "pab_valor_pago_d": "valor_ab_2022",
    },
    "bolsa_familia_202609.csv": {
        "qtd_familias_beneficiarias_bolsa_familia_i": "familias_bf_2026",
        "qtd_pessoas_beneficiarias_bolsa_familia_i": "pessoas_bf_2026",
        "valor_repassado_bolsa_familia_f": "valor_bf_2026",
    },
}


def le_misocial(caminho: Path, colunas: dict[str, str], codigos_ibge: pl.Series) -> pl.DataFrame:
    """Lê um CSV do MiSocial e devolve `cd_ibge` (7 dígitos) + `colunas` renomeadas.

    Falha se algum código de 6 dígitos não corresponder a um município conhecido.
    """
    mapa = pl.DataFrame({"cd_ibge": codigos_ibge.cast(pl.Int64)}).with_columns(
        cod6=pl.col("cd_ibge") // 10
    )
    bruto = pl.read_csv(caminho, schema_overrides={"codigo_ibge": pl.Int64})
    sem_par = bruto.join(mapa, left_on="codigo_ibge", right_on="cod6", how="anti")
    if sem_par.height:
        raise ValueError(f"códigos do MiSocial sem município: {sem_par['codigo_ibge'].to_list()}")
    return bruto.join(mapa, left_on="codigo_ibge", right_on="cod6").select(
        "cd_ibge", *(pl.col(orig).cast(pl.Float64).alias(novo) for orig, novo in colunas.items())
    )
