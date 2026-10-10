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

# `dvc status` sem os avisos de etapa congelada: todo `dvc import-url` é congelado
status *args:
    @echo "\$ uv run dvc status {{args}}\n"
    @uv run dvc status {{args}} 2>&1 | grep -v "is frozen. Its dependencies are not going to be shown"

# Roda os notebooks pendentes pelo DVC e mostra as métricas que mudaram desde o último
# commit (D8). Limpa antes as saídas dos notebooks: o DVC calcula o hash do .ipynb com elas.
resultados *args:
    uv run nbstripout notebooks/*.ipynb
    uv run dvc repro {{args}}
    uv run dvc metrics diff

# Compara métricas e gráficos com outra revisão (gráficos em dvc_plots/index.html)
compara rev="main":
    uv run dvc metrics diff {{rev}}
    uv run dvc plots diff {{rev}}

# Sincroniza dados versionados com o remoto R2
push:
    uv run dvc push

pull:
    uv run dvc pull

# Gera e grava a previsão do 2º turno (ex.: just previsao v2 2026-10-24)
previsao versao corte:
    uv run python -m kingsrace.models.previsao_2t {{versao}} {{corte}}

# Dados do site a partir das saídas do DVC (etapas site_*), depois monta _site/ (D12)
site:
    uv run dvc repro site_segundo_turno
    uv run python -m kingsrace.publica build

# Prévia local do site em http://localhost:8000
site-serve porta="8000":
    uv run python -m kingsrace.publica serve {{porta}}

# Pesquisa nova (linha em data/reference/pesquisas_serie_2025_2026.csv): refaz a G6, os dados do
# site e o build, e mostra o que mudou nas métricas desde o último commit
pesquisas:
    uv run dvc repro pesquisas site_segundo_turno
    uv run python -m kingsrace.publica build
    uv run dvc metrics diff --targets resultados/pesquisas/metrics.json
