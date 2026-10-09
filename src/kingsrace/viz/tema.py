"""Tema Altair e paleta do projeto (paleta de referência validada da skill dataviz).

Convenções:
- séries categóricas na ordem fixa de SERIES (nunca cíclica; > 3 séries → facetas);
- variação do voto (divergente): rumo ao PT = vermelho, rumo ao adversário = azul,
  ponto médio cinza — segue a convenção de cor partidária usada na imprensa.
"""

import altair as alt

SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]  # azul, laranja, água
SEQUENCIAL = "#2a78d6"
DIVERGENTE = {"pt": "#e34948", "meio": "#f0efec", "adversario": "#2a78d6"}

SUPERFICIE = "#fcfcfb"
TINTA = {"primaria": "#0b0b0b", "secundaria": "#52514e", "apagada": "#898781"}
GRADE, EIXO = "#e1e0d9", "#c3c2b7"
FONTE = 'system-ui, -apple-system, "Segoe UI", sans-serif'


def escala_divergente(limite: float) -> alt.Scale:
    """Escala divergente simétrica em [-limite, limite], com o cinza exatamente no zero."""
    return alt.Scale(
        domain=[-limite, 0, limite],
        range=[DIVERGENTE["adversario"], DIVERGENTE["meio"], DIVERGENTE["pt"]],
        interpolate="lab",
        clamp=True,
    )


@alt.theme.register("kingsrace", enable=True)
def tema() -> alt.theme.ThemeConfig:
    return {
        "config": {
            "background": SUPERFICIE,
            "font": FONTE,
            "view": {"stroke": None},
            "title": {"color": TINTA["primaria"], "fontSize": 14, "anchor": "start"},
            "axis": {
                "labelColor": TINTA["apagada"],
                "titleColor": TINTA["secundaria"],
                "gridColor": GRADE,
                "domainColor": EIXO,
                "tickColor": EIXO,
                "titleFontWeight": "normal",
            },
            "legend": {"labelColor": TINTA["secundaria"], "titleColor": TINTA["secundaria"]},
            "header": {"labelColor": TINTA["secundaria"], "titleColor": TINTA["secundaria"]},
            "range": {"category": SERIES},
            "line": {"strokeWidth": 2},
            "point": {"size": 64},
        }
    }
