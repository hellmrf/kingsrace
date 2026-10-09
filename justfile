# Receitas do dia a dia. O pipeline de dados em si vive no dvc.yaml (a partir do M0b).

default:
    @just --list

# Instala dependências e configura o filtro que limpa saídas de notebooks no git
setup:
    uv sync
    uv run nbstripout --install --attributes .gitattributes

# Testes (esquemas, reconciliação com totais oficiais)
test *args:
    uv run pytest {{args}}

lint:
    uv run ruff check .
    uv run ruff format --check .

fmt:
    uv run ruff check --fix .
    uv run ruff format .

# Reconstrói as etapas do pipeline cujas entradas mudaram
repro *args:
    uv run dvc repro {{args}}

# Sincroniza dados versionados com o remoto R2
push:
    uv run dvc push

pull:
    uv run dvc pull

# Gera e grava a previsão do 2º turno (ex.: just previsao v2 2026-10-24)
previsao versao corte:
    uv run python -m kingsrace.models.previsao_2t {{versao}} {{corte}}
