import json
import shutil
import subprocess

import pytest

from kingsrace import paths
from kingsrace.publica import build, comum


def test_formato_brasileiro():
    assert comum.br(1234.56) == "1.234,6"
    assert comum.br(-0.04) == "0,0"  # arredonda para zero: sem sinal de menos
    assert comum.br(-2.25, 2) == "−2,25"
    assert comum.sinal(1.0) == "+1,0" and comum.sinal(-1.0) == "−1,0"
    assert comum.pct(0.0369) == "3,7%"
    assert comum.mi(2.2) == "2,2 milhões" and comum.mi(1.04) == "1,0 milhão"
    assert comum.mil(186.7) == "187 mil"


def test_metrica_por_caminho_falha_com_o_caminho_inteiro():
    m = {"G1": {"diferenca_mi": 2.2}}
    assert comum.metrica(m, "G1/diferenca_mi") == 2.2
    with pytest.raises(KeyError, match="G1/outra"):
        comum.metrica(m, "G1/outra")


def test_grava_json_e_deterministico_e_recusa_nan(tmp_path):
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    comum.grava_json(a, {"b": 1.23456789, "a": [1, 2.0]})
    comum.grava_json(b, {"a": [1, 2.0], "b": 1.23456789})
    assert a.read_bytes() == b.read_bytes()
    assert json.loads(a.read_text())["b"] == 1.234568
    with pytest.raises(ValueError):
        comum.grava_json(tmp_path / "c.json", {"x": float("nan")})


@pytest.mark.skipif(
    not (comum.DADOS / "segundo-turno" / "pagina.json").exists(),
    reason="dados do site ausentes; rode `just site`",
)
def test_build_monta_todas_as_paginas_sem_numero_faltando(tmp_path):
    geradas = build.monta(tmp_path / "_site")  # StrictUndefined: um número que falta derruba
    nomes = {p.relative_to(tmp_path / "_site").as_posix() for p in geradas}
    assert {"index.html", "segundo-turno/index.html"} <= nomes
    html = (tmp_path / "_site" / "segundo-turno" / "index.html").read_text()
    assert "—" not in html.split("<main>")[1].split("data-calc-valor")[0]  # nada vazio no texto
    # todo arquivo de dados citado na página existe
    for uf in json.loads((comum.DADOS / "segundo-turno" / "pagina.json").read_text())[
        "sem_governador_2026"
    ]:
        assert (tmp_path / "_site" / "dados" / "segundo-turno" / "listas" / f"{uf}.csv").exists()


@pytest.mark.skipif(shutil.which("node") is None, reason="node ausente")
@pytest.mark.skipif(
    not (comum.DADOS / "segundo-turno" / "pagina.json").exists(), reason="dados do site ausentes"
)
def test_calculadora_js_reproduz_o_cenario_do_dvc():
    pagina = json.loads((comum.DADOS / "segundo-turno" / "pagina.json").read_text())
    calc = pagina["calculadora"]
    modulo = (paths.ROOT / "site" / "estatico" / "js" / "componentes" / "calculadora.js").as_uri()
    script = (
        f"import {{ margem }} from {json.dumps(modulo)};"
        f"const c = {json.dumps(calc)};"
        "console.log(margem(c.n, c.padrao_2022, c.exterior_mi));"
    )
    saida = subprocess.run(
        ["node", "--input-type=module", "-e", script], capture_output=True, text=True, check=True
    ).stdout
    # as taxas vão ao JSON com 6 casas; × ~55 milhões de eleitores, o erro fica em dezenas de
    # votos (a página mostra décimos de milhão)
    assert float(saida) == pytest.approx(pagina["cenarios"]["perfil"]["margem_mi"], abs=1e-4)
