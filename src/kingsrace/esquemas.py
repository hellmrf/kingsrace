"""Esquemas pandera das tabelas de data/processed (significado em docs/dicionario_dados.md)."""

import pandera.polars as pa
import polars as pl

UFS = [
    "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA",
    "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO",
]  # fmt: skip

PAPEIS = ["pt", "adversario", "outro", "anulado", "branco", "nulo"]


# o pandera exige um Field novo por coluna
def contagem():
    return pa.Field(ge=0)


def proporcao():
    return pa.Field(in_range={"min_value": 0, "max_value": 1})


class Municipios(pa.DataFrameModel):
    cd_tse: pl.Int32 = pa.Field(unique=True)
    cd_ibge: pl.Int64 = pa.Field(unique=True, in_range={"min_value": 1100000, "max_value": 5399999})
    nome: pl.String
    uf: pl.String = pa.Field(isin=UFS)
    regiao: pl.String = pa.Field(isin=["N", "NE", "SE", "S", "CO"])
    cd_regiao_intermediaria: pl.Int64
    regiao_intermediaria: pl.String
    cd_regiao_imediata: pl.Int64
    regiao_imediata: pl.String
    amc_id: pl.Int64

    class Config:
        strict = True


class VotosMunicipio(pa.DataFrameModel):
    ano: pl.Int16
    turno: pl.Int8 = pa.Field(isin=[1, 2])
    uf: pl.String = pa.Field(isin=[*UFS, "ZZ"])
    cd_tse: pl.Int32
    nr_votavel: pl.Int32
    nm_votavel: pl.String
    votos: pl.Int32 = contagem()
    papel: pl.String = pa.Field(isin=PAPEIS)
    cd_ibge: pl.Int64 = pa.Field(nullable=True)  # nulo só no exterior

    class Config:
        strict = True
        unique = ["ano", "turno", "cd_tse", "nr_votavel"]


class PainelMunicipio(pa.DataFrameModel):
    cd_ibge: pl.Int64
    ano: pl.Int16
    turno: pl.Int8 = pa.Field(isin=[1, 2])
    uf: pl.String = pa.Field(isin=UFS)
    aptos: pl.Int32 = contagem()
    comparecimento: pl.Int32 = contagem()
    abstencoes: pl.Int32 = contagem()
    eleitores_nao_instalados: pl.Int32 = contagem()
    validos: pl.Int32 = contagem()
    brancos: pl.Int32 = contagem()
    nulos: pl.Int32 = contagem()
    votos_pt: pl.Int32 = contagem()
    votos_adv: pl.Int32 = contagem()
    votos_outros: pl.Int32 = contagem()
    pt_validos: pl.Float64 = proporcao()
    adv_validos: pl.Float64 = proporcao()
    pt_2p: pl.Float64 = proporcao()
    pt_2p_logit: pl.Float64
    pt_aptos: pl.Float64 = proporcao()
    abstencao: pl.Float64 = proporcao()

    class Config:
        strict = True
        unique = ["cd_ibge", "ano", "turno"]
