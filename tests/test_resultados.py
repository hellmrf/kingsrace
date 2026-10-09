import json

import altair as alt
import numpy as np
import polars as pl
import pytest
import vl_convert as vlc
import yaml
from dvc_render.vega import VegaRenderer

from kingsrace import paths, resultados


@pytest.fixture
def live(tmp_path, monkeypatch):
    monkeypatch.setattr(resultados, "DIR", tmp_path)
    live = resultados.abre("08_mecanismos")
    yield live
    live.end()


def _metrics(live):
    return json.loads((resultados.DIR / "08_mecanismos" / "metrics.json").read_text())


def test_metrica_aninha_e_grava_na_hora(live):
    resultados.metrica(live, "E2a/salto/beta", -0.098)
    resultados.metrica(live, "E2a/sustenta", np.float64(-0.1) < 0)  # numpy.bool_
    resultados.metrica(live, "E2a/n", np.int64(5000))
    assert _metrics(live) == {"E2a": {"salto": {"beta": -0.098}, "sustenta": 1, "n": 5000.0}}


@pytest.mark.parametrize("nome", ["E2a.salto", "2014→2018", "A1//beta", "evangélica"])
def test_metrica_recusa_nome_invalido(live, nome):
    with pytest.raises(ValueError, match="inválido"):
        resultados.metrica(live, nome, 1.0)


def test_chave():
    assert resultados.chave("2014→2018") == "2014_2018"
    assert resultados.chave("Centro-Oeste") == "Centro-Oeste"
    assert resultados.chave("sem controles") == "sem_controles"
    assert resultados.chave("Região Sul") == "Regiao_Sul"


def test_metrica_recusa_nan(live):
    with pytest.raises(ValueError, match="não finito"):
        resultados.metrica(live, "A1/beta", float("nan"))


def test_coeficientes_gera_tabela(live):
    df = pl.DataFrame(
        {"transicao": ["2010→2014", "2014→2018"], "coef": [0.007, -0.091]}
    ).with_columns(ic_inf=pl.col("coef") - 0.02, ic_sup=pl.col("coef") + 0.02)
    resultados.coeficientes(live, "E2a_event_study", df, rotulo="transicao")
    arquivo = resultados.DIR / "08_mecanismos" / "plots" / "custom" / "E2a_event_study.json"
    linhas = json.loads(arquivo.read_text())
    assert [set(linha) for linha in linhas] == [set(resultados.COLUNAS_COEF)] * 2
    assert linhas[1]["rotulo"] == "2014→2018"


def test_grafico_gera_png(live):
    chart = alt.Chart(pl.DataFrame({"x": [1, 2], "y": [3, 4]})).mark_point().encode(x="x", y="y")
    assert resultados.grafico(live, "teste", chart) is chart
    png = resultados.DIR / "08_mecanismos" / "plots" / "images" / "teste.png"
    assert png.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_template_coeficientes_compila():
    pontos = [
        {"rotulo": r, "coef": c, "ic_inf": c - 0.02, "ic_sup": c + 0.02, "rev": rev}
        | {"filename": "x.json", "field": "coef"}
        for rev in ("main", "HEAD")
        for r, c in [("2010→2014", 0.007), ("2014→2018", -0.091)]
    ]
    spec = VegaRenderer(
        pontos,
        "E2a",
        template="coeficientes",
        template_dir=str(paths.ROOT / ".dvc" / "plots"),
        x="rotulo",
        y="coef",
    ).get_filled_template()
    assert vlc.vegalite_to_svg(spec).startswith("<svg")


def test_todo_notebook_tem_etapa():
    etapas = yaml.safe_load((paths.ROOT / "dvc.yaml").read_text())["stages"]
    for nb in sorted(paths.NOTEBOOKS.glob("*.ipynb")):
        etapa = etapas[f"nb_{nb.stem}"]
        assert f"notebooks/{nb.name}" in etapa["deps"]
        assert f"resultados/{nb.stem}/metrics.json" in [next(iter(m)) for m in etapa["metrics"]]
