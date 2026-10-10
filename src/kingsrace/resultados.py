"""Resultados versionados dos notebooks: métricas, coeficientes e gráficos (decisão D8).

Cada notebook abre um `Live` do DVCLive em resultados/<notebook>/ e registra ali o que hoje
vai para docs/hipoteses.md, com o ID da hipótese no começo do nome (`A1/M3/beta`):

- `metrics.json`: números (coeficientes, ICs, p-valores, vereditos 0/1); fica no git;
- `plots/custom/<nome>.json`: tabelas de coeficientes com IC, desenhadas pelo template
  `.dvc/plots/coeficientes.json` (várias revisões lado a lado); ficam no git;
- `plots/images/<nome>.png`: os gráficos Altair do notebook; vão para o cache do DVC (R2).

O `dvc.yaml` declara esses arquivos em cada etapa `nb_*` (o DVCLive não mexe no dvc.yaml).
Rodar o notebook à mão grava os mesmos arquivos: vale como rascunho até um `dvc repro`.
"""

import math
import os
import re
import unicodedata
from collections.abc import Mapping
from io import BytesIO
from typing import TYPE_CHECKING, Any

import altair as alt
import numpy as np
import polars as pl
import yaml

from kingsrace import paths

if TYPE_CHECKING:
    import pyfixest as pf
    from dvclive import Live

DIR = paths.ROOT / "resultados"
COLUNAS_COEF = ("rotulo", "coef", "ic_inf", "ic_sup")
NOME = re.compile(r"^[A-Za-z0-9_-]+(/[A-Za-z0-9_-]+)*$")


def em_lote() -> bool:
    """True quando o notebook roda dentro do `dvc repro`/`dvc exp run` (via papermill)."""
    return "DVC_STAGE" in os.environ or os.environ.get("KINGSRACE_LOTE") == "1"


def configura_altair() -> None:
    """Em lote, SVG estático (o widget Jupyter incharia o notebook executado)."""
    if em_lote():
        alt.renderers.enable("svg")
    else:
        alt.renderers.enable("jupyter", offline=True)


def params(secao: str) -> dict[str, Any]:
    return yaml.safe_load((paths.ROOT / "params.yaml").read_text())[secao]


def abre(notebook: str) -> "Live":
    """`Live` do notebook (nome sem extensão), recomeçando do zero a cada execução."""
    if not (paths.NOTEBOOKS / f"{notebook}.ipynb").exists():
        raise FileNotFoundError(f"notebooks/{notebook}.ipynb não existe")
    return abre_etapa(notebook)


def abre_etapa(etapa: str) -> "Live":
    """`Live` de uma etapa do pipeline (módulo ou notebook), em resultados/<etapa>/ (D12)."""
    from dvclive import Live

    return Live(
        dir=str(DIR / etapa),
        resume=False,
        report=None,
        save_dvc_exp=False,
        dvcyaml=False,
        cache_images=False,
        monitor_system=False,
    )


def chave(rotulo: object) -> str:
    """Trecho de nome de métrica a partir de um rótulo: '2014→2018' → '2014_2018'."""
    decomposto = unicodedata.normalize("NFKD", str(rotulo))
    sem_acento = "".join(c for c in decomposto if not unicodedata.combining(c))
    return re.sub(r"[^A-Za-z0-9-]+", "_", sem_acento).strip("_")


def metrica(live: "Live", nome: str, valor: float | int | bool) -> None:
    """Registra um número e já grava o metrics.json (uma execução pela metade fica salva)."""
    if not NOME.match(nome):
        raise ValueError(f"nome de métrica inválido: {nome!r} (use A-Z, 0-9, _, - e /)")
    if isinstance(valor, bool | np.bool_):
        valor = int(valor)
    elif not isinstance(valor, int):
        valor = float(valor)  # também escalares numpy
    if isinstance(valor, float) and not math.isfinite(valor):
        raise ValueError(f"{nome}: valor não finito ({valor})")
    live.log_metric(nome, valor, plot=False)
    live.make_summary()


def metricas(live: "Live", prefixo: str, valores: Mapping[str, float | int | bool]) -> None:
    for nome, valor in valores.items():
        metrica(live, f"{prefixo}/{nome}", valor)


def ajuste(
    live: "Live", prefixo: str, fit: "pf.Feols", termo: str, *, sustenta: bool | None = None
) -> None:
    """Coeficiente de um termo do pyfixest: beta, IC 95%, p e número de observações."""
    t = fit.tidy().loc[termo]
    valores = {
        "beta": t["Estimate"],
        "ic_inf": t["2.5%"],
        "ic_sup": t["97.5%"],
        "p": t["Pr(>|t|)"],
        "n": int(fit._N),
    }
    if sustenta is not None:
        valores["sustenta"] = sustenta
    metricas(live, prefixo, valores)


def coeficientes(
    live: "Live",
    nome: str,
    df: pl.DataFrame,
    *,
    rotulo: str = "rotulo",
    coef: str = "coef",
    ic_inf: str = "ic_inf",
    ic_sup: str = "ic_sup",
) -> None:
    """Tabela de coeficientes com IC para o template `coeficientes` (uma linha por rótulo)."""
    linhas = df.select(
        pl.col(rotulo).cast(pl.String).alias("rotulo"),
        pl.col(coef).cast(pl.Float64).alias("coef"),
        pl.col(ic_inf).cast(pl.Float64).alias("ic_inf"),
        pl.col(ic_sup).cast(pl.Float64).alias("ic_sup"),
    ).to_dicts()
    live.log_plot(nome, linhas, x="rotulo", y="coef", template="coeficientes")


def serie(live: "Live", nome: str, df: pl.DataFrame, x: str, y: str | list[str]) -> None:
    """Dados de um gráfico em plots/custom/<nome>.json, para o `dvc plots` (D12).

    O template, o eixo e os rótulos ficam declarados no dvc.yaml. É também o que a página
    pública redesenha: mesmo nome, mesmos dados.
    """
    if not NOME.match(nome):
        raise ValueError(f"nome de gráfico inválido: {nome!r}")
    live.log_plot(nome, df.to_dicts(), x=x, y=y)


def grafico(live: "Live", nome: str, chart: alt.TopLevelMixin, escala: float = 2.0):
    """Salva o gráfico como PNG (tema do projeto) e o devolve para aparecer na célula."""
    from PIL import Image

    buf = BytesIO()
    chart.save(buf, format="png", scale_factor=escala)
    buf.seek(0)
    live.log_image(f"{nome}.png", Image.open(buf))
    return chart
