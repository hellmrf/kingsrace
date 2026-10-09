"""Decomposição da variação de votos de um candidato entre dois pleitos (LMDI).

V = A · t · v · s, com A = aptos, t = comparecimento/aptos, v = válidos/comparecimento e
s = votos/válidos. Em cada unidade, ΔV = L(V₁, V₀) · Σ Δln(fator), em que L é a média
logarítmica. A decomposição é exata (os termos somam ΔV) e aditiva entre unidades.
"""

import polars as pl

FATORES = {
    "c_eleitorado": ("aptos", None),
    "c_comparecimento": ("comparecimento", "aptos"),
    "c_validos": ("validos", "comparecimento"),
    "c_fatia": ("votos", "validos"),
}


def decompoe_votos(base: pl.DataFrame) -> pl.DataFrame:
    """Acrescenta `delta` e as contribuições `c_*` (mesma unidade de votos).

    `base` precisa de aptos, comparecimento, validos e votos com sufixos `_de` e `_para`.
    """
    v0, v1 = pl.col("votos_de"), pl.col("votos_para")
    # média logarítmica; quando V não muda, L(V, V) = V
    media_log = pl.when(v1 == v0).then(v0).otherwise((v1 - v0) / (v1.log() - v0.log()))

    def razao(num, den, sufixo):
        col = pl.col(f"{num}_{sufixo}")
        return col if den is None else col / pl.col(f"{den}_{sufixo}")

    return base.with_columns(
        delta=v1 - v0,
        **{
            nome: media_log * (razao(num, den, "para") / razao(num, den, "de")).log()
            for nome, (num, den) in FATORES.items()
        },
    )
