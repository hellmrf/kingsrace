# kingsrace

Análise exploratória de dados sobre as eleições presidenciais no Brasil, 2006–2026:
a geografia da queda de Lula entre 2022 e 2026, as transferências entre o 1º e o
2º turno de 2026 e a série histórica do voto petista.

O plano de pesquisa está em [docs/plano.md](docs/plano.md).

## Setup

Requer [uv](https://docs.astral.sh/uv/) e [just](https://just.systems/).

```sh
just setup     # uv sync + filtro nbstripout no git
just pull      # baixa os dados versionados do remoto R2 (depois de configurado)
just test
```

### Remoto de dados (Cloudflare R2), uma vez por máquina

Crie um bucket no R2 e um token de API com permissão *Object Read & Write* nesse bucket.

```sh
uv run dvc remote add -d r2 s3://<bucket>/dvc
uv run dvc remote modify r2 endpointurl https://<ACCOUNT_ID>.r2.cloudflarestorage.com
# credenciais só no config.local (fora do git)
uv run dvc remote modify --local r2 access_key_id <ACCESS_KEY_ID>
uv run dvc remote modify --local r2 secret_access_key <SECRET_ACCESS_KEY>
```

## Estrutura

```
data/
  raw/          fontes originais, imutáveis — versionadas pelo DVC, nunca pelo git
  interim/      intermediários descartáveis
  processed/    saídas do pipeline (dvc repro)
  reference/    tabelas pequenas feitas à mão, versionadas no git
src/kingsrace/  ingest → harmonize → features → models → viz
notebooks/      numerados (01_panorama … 08_mecanismos); saídas removidas no commit
resultados/     métricas e gráficos de cada notebook, registrados pelo DVCLive (D8)
reports/        relatório Quarto; notebooks/ guarda as cópias executadas (cache do DVC)
docs/           plano, decisões, hipóteses, dicionário de dados
tests/          esquemas e reconciliação com totais oficiais
```

## Fluxo de dados

- **Fonte nova:** `uv run dvc import-url <url> data/raw/<fonte>/`. Depois, commit do
  `.dvc` gerado e `just push`.
- **Versão nova de uma fonte** (ex.: TSE após o 2º turno): `uv run dvc update <arquivo>.dvc`.
- **Reconstruir derivados:** `just repro`.

## Resultados: métricas, gráficos e experimentos

Cada notebook é uma etapa do pipeline (`nb_01_panorama` … `nb_08_mecanismos`) e registra,
pelo DVCLive, os números e gráficos de cada hipótese em `resultados/<notebook>/`
(decisão D8). Os nomes começam pelo ID da hipótese: `A1/M3/beta`, `E2a/salto/p`,
`B4/backtest_2022/G0/rmse_pp`; `<ID>/sustenta` é o veredito (0/1) pelo critério registrado.

```sh
just resultados                    # roda os notebooks pendentes; mostra o que mudou desde o commit
just resultados nb_08_mecanismos   # só um notebook (e o que vier antes dele no pipeline)
just compara main                  # métricas e gráficos desta revisão contra a main
uv run dvc plots diff HEAD~3       # gráficos lado a lado (abre dvc_plots/index.html)
uv run dvc exp show -A --only-changed  # tabela de métricas por commit, em todos os commits
uv run dvc pull reports/notebooks  # notebooks executados, com todas as saídas
```

- **No VS Code**, a extensão do DVC mostra as métricas por commit (aba *Experiments*) e os
  gráficos de várias revisões lado a lado (aba *Plots*). As tabelas de coeficientes usam o
  template `.dvc/plots/coeficientes.json`: ponto e IC de 95%, uma cor por revisão.
- **Experimentos** servem só para exploração, com os parâmetros da seção `exploracao` do
  `params.yaml` (ex.: `uv run dvc exp run nb_06_serie -S exploracao.c3_grupos=5`, depois
  `uv run dvc exp show --only-changed`). Um resultado confirmatório é o que está comitado.
- **Rodar um notebook à mão** grava os mesmos arquivos em `resultados/`: serve de rascunho.
  Antes de comitar, `just resultados` (o `dvc status` deve ficar limpo).

Decisões de projeto e cuidados metodológicos em [docs/decisoes.md](docs/decisoes.md).
O andamento e os achados ficam em [docs/diario.md](docs/diario.md).
