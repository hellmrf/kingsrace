"""Caminhos canônicos do projeto, independentes do diretório de trabalho."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DATA = ROOT / "data"
RAW = DATA / "raw"  # imutável; versionado pelo DVC
INTERIM = DATA / "interim"  # intermediários descartáveis
PROCESSED = DATA / "processed"  # saídas do pipeline (dvc repro)
REFERENCE = DATA / "reference"  # tabelas pequenas feitas à mão, versionadas no git

NOTEBOOKS = ROOT / "notebooks"
REPORTS = ROOT / "reports"
