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
notebooks/      numerados (01_sanidade, 10_eda_2022_2026, ...); saídas removidas no commit
reports/        relatório Quarto
docs/           plano, decisões, hipóteses, dicionário de dados
tests/          esquemas e reconciliação com totais oficiais
```

## Fluxo de dados

- **Fonte nova:** `uv run dvc import-url <url> data/raw/<fonte>/`. Depois, commit do
  `.dvc` gerado e `just push`.
- **Versão nova de uma fonte** (ex.: TSE após o 2º turno): `uv run dvc update <arquivo>.dvc`.
- **Reconstruir derivados:** `just repro`.

Decisões de projeto e cuidados metodológicos em [docs/decisoes.md](docs/decisoes.md).
