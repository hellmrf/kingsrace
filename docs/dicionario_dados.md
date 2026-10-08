# Dicionário de dados

Tabelas de `data/processed/`, geradas por `just repro` (etapas em `dvc.yaml`). O esquema
executável está em `src/kingsrace/esquemas.py`; este arquivo explica o significado.
Pleitos disponíveis: os de `params.yaml` (hoje 2022 1T/2T e 2026 1T).

## `municipios.parquet`

- **Grão:** uma linha por município (5.571), união dos códigos TSE de todos os pleitos.
- **Origem:** etapa `municipios` — códigos TSE do detalhe por zona + API de localidades do
  IBGE + `data/reference/municipios_overrides.csv` + `data/reference/amc.csv`.

| Coluna | Tipo | Descrição |
|---|---|---|
| `cd_tse` | Int32 | código do município no TSE (estável entre pleitos; o nome pode mudar) |
| `cd_ibge` | Int64 | código IBGE de 7 dígitos |
| `nome`, `uf` | String | nome oficial (IBGE) e sigla da UF |
| `regiao` | String | N, NE, SE, S, CO |
| `cd_regiao_intermediaria`, `regiao_intermediaria` | Int64, String | região geográfica intermediária (IBGE 2017) |
| `cd_regiao_imediata`, `regiao_imediata` | Int64, String | região geográfica imediata (IBGE 2017) |
| `amc_id` | Int64 | área mínima comparável: o próprio `cd_ibge`, ou ≥ 9000000 para grupos de `amc.csv` |

## `votos_municipio.parquet`

- **Grão:** ano × turno × município TSE × número de voto. Inclui o exterior (`uf = ZZ`).
- **Origem:** etapa `painel` — soma da votação por seção do TSE.

| Coluna | Tipo | Descrição |
|---|---|---|
| `ano`, `turno` | Int16, Int8 | pleito |
| `uf`, `cd_tse`, `cd_ibge` | String, Int32, Int64 | município; `cd_ibge` nulo no exterior |
| `nr_votavel`, `nm_votavel` | Int32, String | número e nome na urna; 95 = branco, 96 = nulo |
| `votos` | Int32 | votos recebidos |
| `papel` | String | `pt`, `adversario`, `outro` (válidos); `anulado`, `branco`, `nulo` (não válidos) |

## `painel_municipio.parquet`

- **Grão:** município IBGE × ano × turno, sem o exterior.
- **Origem:** etapa `painel` — comparecimento do detalhe por zona + votos por papel.

| Coluna | Tipo | Descrição |
|---|---|---|
| `cd_ibge`, `ano`, `turno`, `uf` | | chave |
| `aptos` | Int32 | eleitores aptos = `comparecimento + abstencoes + eleitores_nao_instalados` |
| `comparecimento` | Int32 | = `validos + brancos + nulos` |
| `abstencoes` | Int32 | eleitores que não compareceram |
| `eleitores_nao_instalados` | Int32 | eleitores de seções não instaladas (raros; ex.: Manaus 2022, 84) |
| `validos` | Int32 | votos válidos = `votos_pt + votos_adv + votos_outros` |
| `brancos`, `nulos` | Int32 | `nulos` inclui votos anulados (candidatos indeferidos) |
| `votos_pt`, `votos_adv`, `votos_outros` | Int32 | votos do PT, do principal adversário e dos demais válidos |
| `pt_validos`, `adv_validos` | Float64 | proporção nos válidos |
| `pt_2p` | Float64 | PT / (PT + adversário) — métrica principal entre pleitos |
| `pt_2p_logit` | Float64 | logit de `pt_2p` |
| `pt_aptos` | Float64 | PT / aptos (inclui o efeito da abstenção) |
| `abstencao` | Float64 | abstenções / aptos |

## `painel_amc.parquet`

Mesmas colunas de `painel_municipio`, com `amc_id` no lugar de `cd_ibge`: contagens somadas
por área mínima comparável e proporções recalculadas a partir das somas. Usar este para
comparar pleitos; tem o mesmo número de linhas em todos os anos.
