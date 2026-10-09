# Dicionário de dados

Tabelas de `data/processed/`, geradas por `just repro` (etapas em `dvc.yaml`). O esquema
executável está em `src/kingsrace/esquemas.py`; este arquivo explica o significado.
Pleitos disponíveis: os de `params.yaml` (2006–2022, 1º e 2º turnos, e 2026 1º turno).

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
| `aptos` | Int64 | eleitores aptos = `comparecimento + abstencoes + eleitores_nao_instalados` |
| `comparecimento` | Int64 | = `validos + brancos + nulos` |
| `abstencoes` | Int64 | eleitores que não compareceram |
| `eleitores_nao_instalados` | Int64 | resíduo aptos − comparecimento − abstenções: eleitores de seções não instaladas (ex.: Manaus 2022, 84) e pequenas diferenças do TSE em 2006–2014 |
| `validos` | Int64 | votos válidos = `votos_pt + votos_adv + votos_outros` |
| `brancos`, `nulos` | Int64 | `nulos` é o resíduo comparecimento − válidos − brancos: nulos, votos de candidatos indeferidos e anulados apurados em separado |
| `votos_pt`, `votos_adv`, `votos_outros` | Int64 | votos do PT, do principal adversário e dos demais válidos |
| `pt_validos`, `adv_validos` | Float64 | proporção nos válidos |
| `pt_2p` | Float64 | PT / (PT + adversário) — métrica principal entre pleitos |
| `pt_2p_logit` | Float64 | logit de `pt_2p` |
| `pt_aptos` | Float64 | PT / aptos (inclui o efeito da abstenção) |
| `abstencao` | Float64 | abstenções / aptos |

## `painel_amc.parquet`

Mesmas colunas de `painel_municipio`, com `amc_id` no lugar de `cd_ibge`: contagens somadas
por área mínima comparável e proporções recalculadas a partir das somas. Usar este para
comparar pleitos; tem o mesmo número de linhas em todos os anos.

## `covariaveis_municipio.parquet`

- **Grão:** uma linha por município (5.571). Boa Esperança do Norte (5101837) fica sem
  dados: o Censo 2022 e o PIB de 2023 são anteriores à sua instalação (2025).
- **Origem:** etapa `covariaveis` — API do SIDRA/IBGE, consultas em
  `src/kingsrace/ingest/ibge.py` (arquivos brutos em `data/raw/ibge/sidra/`).

| Coluna | Fonte (tabela SIDRA) | Descrição |
|---|---|---|
| `populacao`, `area_km2`, `densidade` | 4714 | população residente (Censo 2022), área, hab/km² |
| `pct_urbana` | 9923 | % da população em situação urbana |
| `idade_mediana`, `indice_envelhecimento` | 9515 | idade mediana; idosos por 100 jovens |
| `pct_branca`, `pct_preta`, `pct_parda`, `pct_preta_parda` | 9605 | cor ou raça, % da população |
| `taxa_alfabetizacao` | 9543 | % alfabetizados entre 15+ anos |
| `pct_catolica`, `pct_evangelica`, `pct_sem_religiao` | 9537 | religião, % da população de 10+ anos (resultados preliminares da amostra) |
| `renda_pc_media`, `renda_pc_mediana` | 10295 | rendimento domiciliar per capita mensal (R$ de 2022) |
| `pct_renda_outras_fontes` | 10297 | % do rendimento domiciliar que não vem do trabalho (aposentadorias, programas sociais, aluguéis…) |
| `pib_2021`, `pib_2023`, `pib_pc_2021`, `pib_pc_2023` | 5938 | PIB (mil R$) e PIB per capita (R$, sobre a população de 2022) |
| `va_2021`, `va_agro_2021`, `va_adm_2021` | 5938 | valor adicionado total, da agropecuária e da administração pública (mil R$) |
| `pct_va_agro_2021`, `pct_va_adm_2021` | 5938 | participação no VA (%); nula se o VA total ≤ 0 (Cachoeira Dourada/GO) |

| `pct_evangelica_2010`, `delta_evangelica` | 137 | % evangélica no Censo 2010 (sobre a população **total**; em 2022 é sobre 10+ anos) e crescimento 2010→2022 em pp. Ausente nos municípios criados depois de 2010 |
| `area_soja_2021_ha`, `area_soja_2025_ha` | 5457 (PAM) | área plantada de soja (ha). "…" (município sem lavoura) vira 0; área maior que o território vira ausente (Mariópolis/PR, 2025) |
| `soja_2021_pct_territorio`, `exp_soja_pct_territorio` | 5457 | soja em % do território em 2021 e sua expansão 2021→2025, em pp do território |
| `familias_ab_2022`, `valor_ab_2022` | MDS (MiSocial, set/2022) | famílias no Auxílio Brasil e valor pago no mês |
| `familias_bf_2026`, `pessoas_bf_2026`, `valor_bf_2026` | MDS (MiSocial, set/2026) | famílias e pessoas no Bolsa Família e valor repassado no mês |
| `familias_ab_100hab_2022`, `familias_bf_100hab_2026` | MDS + Censo | famílias beneficiárias por 100 habitantes (população de 2022) |

O VA por setor de 2023 ainda não foi publicado por município; por isso os setores usam 2021.
Símbolos do IBGE: "-" é zero absoluto; "..", "..." e "X" são ausentes.

## `covariaveis_amc.parquet`

As mesmas colunas por `amc_id`. Colunas extensivas (população, área, PIB, VA, soja, famílias,
valores) são **somadas**; as taxas do Censo são ponderadas pela população; as derivadas
(per capita, participações, por 100 habitantes, densidade) são **recalculadas a partir das
somas**. Município sem população no Censo (Boa Esperança do Norte) entra nas somas, não nos
pesos.
