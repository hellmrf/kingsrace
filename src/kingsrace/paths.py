"""Caminhos canônicos do projeto, independentes do diretório de trabalho."""

import os
from pathlib import Path

# Dentro de uma etapa do DVC, a raiz é a do repositório que está rodando: num
# `dvc exp run --temp` ou na fila de experimentos, uma cópia em .dvc/tmp/exps, enquanto o
# pacote (instalado em modo editável) continua apontando para a área de trabalho.
ROOT = Path(os.environ.get("DVC_ROOT") or Path(__file__).resolve().parents[2])

DATA = ROOT / "data"
RAW = DATA / "raw"  # imutável; versionado pelo DVC
INTERIM = DATA / "interim"  # intermediários descartáveis
PROCESSED = DATA / "processed"  # saídas do pipeline (dvc repro)
REFERENCE = DATA / "reference"  # tabelas pequenas feitas à mão, versionadas no git

NOTEBOOKS = ROOT / "notebooks"
REPORTS = ROOT / "reports"
