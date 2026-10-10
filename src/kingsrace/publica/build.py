"""Monta o site estático em _site/: templates Jinja + site/estatico + site/dados (D12).

Cada página é `site/paginas/<caminho>.html.j2` e recebe, além do contexto comum, o conteúdo
de `site/dados/<pasta da página>/pagina.json` (os números do texto). `StrictUndefined` faz
o build falhar se um número faltar, em vez de publicar um buraco. Os caminhos são relativos
(`raiz`), então o mesmo build serve em localhost e em hellmrf.github.io/kingsrace/.
"""

import json
import os
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

from kingsrace import paths
from kingsrace.publica import comum

SITE = comum.SITE
SAIDA = paths.ROOT / "_site"


def ambiente() -> Environment:
    env = Environment(
        loader=FileSystemLoader([SITE / "modelos", SITE / "paginas"]),
        undefined=StrictUndefined,
        autoescape=select_autoescape(["html", "j2"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters.update(br=comum.br, sinal=comum.sinal, pct=comum.pct, mi=comum.mi, mil=comum.mil)
    return env


def paginas() -> list[Path]:
    """Templates de página, relativos a site/paginas (ex.: segundo-turno/index.html.j2)."""
    return sorted(p.relative_to(SITE / "paginas") for p in (SITE / "paginas").rglob("*.html.j2"))


def _commit() -> str:
    if sha := os.environ.get("GITHUB_SHA"):
        return sha[:7]
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True, cwd=paths.ROOT,
        ).stdout.strip()  # fmt: skip
    except (OSError, subprocess.CalledProcessError):
        return "local"


def contexto(pagina: Path) -> dict:
    pasta = pagina.parent.as_posix()
    dados = SITE / "dados" / (pasta if pasta != "." else "capa") / "pagina.json"
    profundidade = len(pagina.parent.parts)
    return {
        "raiz": "../" * profundidade,
        "pasta": pasta,
        "commit": _commit(),
        "montado_em": datetime.now(UTC).strftime("%d/%m/%Y %H:%M UTC"),
        **(json.loads(dados.read_text()) if dados.exists() else {}),
    }


def monta(saida: Path = SAIDA) -> list[Path]:
    """Refaz _site/ do zero e devolve as páginas geradas."""
    if saida.exists():
        shutil.rmtree(saida)
    shutil.copytree(SITE / "estatico", saida / "estatico")
    if (SITE / "dados").exists():
        shutil.copytree(SITE / "dados", saida / "dados")
    env = ambiente()
    geradas = []
    for pagina in paginas():
        destino = saida / pagina.with_suffix("")  # tira o .j2
        destino.parent.mkdir(parents=True, exist_ok=True)
        html = env.get_template(pagina.as_posix()).render(**contexto(pagina))
        destino.write_text(html, encoding="utf-8")
        geradas.append(destino)
    (saida / ".nojekyll").write_text("")  # o Pages serve pastas com _ e arquivos como estão
    return geradas
