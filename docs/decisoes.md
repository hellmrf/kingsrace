# Decisões

Registro curto de decisões de projeto e metodológicas. Uma entrada nova por decisão;
quando uma for revista, marcar como **substituída** e apontar para a nova.

---

## D1 — Versionamento de dados: DVC + Cloudflare R2

**Data:** 2026-10-08 · **Status:** em vigor

- **git:** código, docs, notebooks (sem saídas, via `nbstripout`) e tabelas pequenas em
  `data/reference/`.
- **DVC:** arquivos brutos em `data/raw/` (o git guarda só os `.dvc` com URL + hash) e
  as saídas do pipeline declaradas no `dvc.yaml`.
- **Remoto:** bucket no Cloudflare R2 (API S3; 10 GB grátis, sem custo de download).
  Credenciais só em `.dvc/config.local`, que não vai para o git.

**Por quê:** o TSE substitui arquivos no mesmo endereço (os de 2026 são atualizados ao
fim de cada turno), então só uma cópia fixa identificada por hash garante
reprodutibilidade. O `dvc repro` refaz apenas as etapas cujas entradas mudaram. O mesmo
bucket pode servir os parquet do portal público (M2) via DuckDB-WASM.

**Descartado:** Git LFS (cota gratuita pequena para alguns GB de dados por seção);
manifest + rclone (sem cache de etapas).

---

## D2 — Stack

**Data:** 2026-10-08 · **Status:** em vigor

Python 3.12 com `uv`; `polars` + `duckdb` sobre parquet; `pandera` para esquemas;
`just` para receitas do dia a dia. Bibliotecas de análise (geo, estatística, ML)
entram no `pyproject.toml` no marco em que forem usadas.

---

## D3 — Unidade de análise e comparabilidade

**Data:** 2026-10-08 · **Status:** em vigor

- Unidade principal: município, agregado em **área mínima comparável** (`amc_id`)
  para que a série 2006–2026 tenha as mesmas fronteiras em todos os anos.
- Zoom intraurbano: **local de votação** (mais estável que seção), só 2018/2022/2026.
- Métrica principal entre pleitos: participação do PT entre os dois maiores.
  Válidos e aptos são métricas secundárias, sempre reportadas junto.

---

## D4 — Correspondência de municípios e contabilidade do TSE

**Data:** 2026-10-08 · **Status:** em vigor

- **Correspondência TSE↔IBGE construída por nós**, por UF + nome normalizado contra a API
  de localidades do IBGE, com 11 overrides documentados. O CSV comunitário
  `betafcc/Municipios-Brasileiros-TSE` foi descartado: tem 5 municípios da BA com códigos
  rodados entre si (Laje, Lagoa Real, Lajedão, Lajedinho, Lajedo do Tabocal), 2 de SC
  trocados (Santiago do Sul ↔ Santa Terezinha do Progresso) e não tem Boa Esperança do Norte.
- **Fonte dos votos:** `votacao_secao_{ano}_BR` (só presidente), agregada; não usamos
  `votacao_candidato_munzona` (~1 GB/ano com todos os cargos).
- **Votos anulados:** o nº 28 em 2026 (Leonardo Alves de Araujo, 5.246 votos) não entra
  nos válidos; o TSE o soma aos nulos. Marcado como `anulado` em `candidatos.csv`. O
  pipeline falha se pt + adversário + outros ≠ válidos, o que denuncia casos novos.
- **Seções não instaladas:** seus eleitores contam em `aptos` mas não em comparecimento
  nem em abstenções; viram a coluna `eleitores_nao_instalados`.
- **AMC 2022–2026:** Boa Esperança do Norte (MT), instalado em 2025, foi desmembrado de
  Nova Ubiratã (~80%) e Sorriso (~20%); os três formam a AMC 9000001.

---

## D5 — Série histórica 2006–2026: particularidades do TSE

**Data:** 2026-10-09 · **Status:** em vigor

- **Totais conferidos:** PT e adversário batem exatamente com os totais oficiais nos 11
  turnos (2006–2026).
- **Votos anulados de candidato:** além do nº 28 em 2026, o nº 29 em 2006 (Rui Costa
  Pimenta, candidatura indeferida, 25.769 votos) vai como `anulado` em `candidatos.csv`.
- **Código 97, "voto anulado e apurado em separado":** votos de seções anuladas pela
  Justiça Eleitoral (272 em 2010 2T, 746 em 2018 1T). Tratado como `anulado` em todos os anos.
- **Nulos e eleitores não instalados por resíduo:** o significado das colunas de nulos do
  TSE muda entre anos (em 2006, `QT_VOTOS_NULOS` e `QT_TOTAL_VOTOS_NULOS` diferem em 3 por
  linha; em 2026 só o "total" inclui os anulados do nº 28). Por isso `nulos` = comparecimento
  − válidos − brancos e `eleitores_nao_instalados` = aptos − comparecimento − abstenções. A
  checagem independente continua: válidos (detalhe) = pt + adversário + outros (seções).
- **Voto em trânsito de 2010:** veio numa pseudo-UF "VT" (códigos 999xx, ~80 mil eleitores);
  atribuído à capital correspondente (`voto_transito_2010.csv`), como o TSE faz desde 2018.
- **AMCs da série:** os 5 municípios instalados em 2013 (Mojuí dos Campos, Paraíso das Águas,
  Pinto Bandeira, Pescaria Brava, Balneário Rincão) formam AMC com os de origem: 5.562 AMCs,
  iguais em todos os 11 turnos. Curiosidade: Mojuí dos Campos e Paraíso das Águas já aparecem
  nos dados de 2010 do TSE.
- **AMC em mais de uma região imediata** (Paraíso das Águas + Costa Rica + Água Clara +
  Chapadão do Sul): fica com a região mais frequente entre os membros.
- **Efeito nas análises 2022→2026:** desprezível (A1 M3: +0,0244 → +0,0243; A4a idêntico).

---

## D6 — Deputado federal e candidatos religiosos (medida E2c)

**Data:** 2026-10-09 · **Status:** em vigor

- **Fontes:** `consulta_cand_{ano}` (ocupação), `votacao_candidato_munzona_{ano}` (votos por
  candidato, município e zona) e `detalhe_votacao_munzona_{ano}_BRASIL.csv` (válidos). O
  `_BR.csv` do detalhe só tem presidente.
- **Votos nominais válidos:** até 2014 o `QT_VOTOS_NOMINAIS` já vem sem os anulados; a partir
  de 2018 o TSE separa `QT_VOTOS_NOMINAIS_VALIDOS` (em 2022, ~1 milhão de votos de
  candidatos indeferidos ficam de fora). A soma bate com o detalhe em todas as UFs nos cinco
  anos (teste em `test_dados.py`).
- **Denominador:** `QT_TOTAL_VOTOS_VALIDOS` do detalhe (nominais + legenda).
- **Chave do candidato:** (ano, UF, `SQ_CANDIDATO`); em 2006 o sequencial se repete entre UFs.
- **Candidatos com voto e sem cadastro:** 1 em 2006 (GO, 51.839 votos) e 3 em 2014. O nome de
  urna vem do arquivo de votação; sem ocupação conhecida, contam só pelo título.
- **A regra registrada é seguida à risca**, com dois efeitos conhecidos: entra quem declara
  ocupação religiosa sem título católico no nome (ex.: o padre Luiz Couto, PT-PB, em 2022) e
  fica de fora quem é evangélico mas não usa título nem declara a ocupação (muitos deputados
  da bancada evangélica). A medida é um **limite inferior** da presença religiosa explícita.

---

## D7 — Fontes grandes com pouco disco: CNPJ, RAIS, SIM e Anatel

**Data:** 2026-10-09 · **Status:** em vigor

- **Cache do DVC em hardlinks** (`dvc config --local cache.type hardlink,symlink`, só nesta
  máquina): cada bruto existe uma vez no disco, não duas. O DVC deixa os brutos só para
  leitura; o código nunca os altera.
- **CNPJ (Receita) fora do R2:** são ~7 GB por versão, além da cota gratuita. Os `.dvc` têm
  `push: false` e guardam URL + hash; os zips de Estabelecimentos são baixados, processados
  e apagados um por vez (`python -m kingsrace.ingest.receita todos`, retomável), lidos
  direto do zip pela extensão `zipfs` do DuckDB. Refazer do zero = baixar de novo da Receita
  (que mantém as versões mensais anteriores no compartilhamento público).
- **RAIS e SIM vêm por FTP**, que o `dvc import-url` não suporta: baixados com `curl`,
  versionados com `dvc add` e com a URL de origem em `data/reference/fontes_ftp.csv`.
- **SIM 2025 é preliminar** (pasta PRELIM do DATASUS); entra no último triênio da E5
  (2023–2025). **RAIS:** a partir de 2018 o layout muda (vírgula, aspas, colunas
  "… - Código"); o leitor acha as colunas pelo prefixo. Totais conferidos com os oficiais
  (2006: 35.155.249 vínculos; 2013: 48.948.433). SIM 2012: 57.045 homicídios, igual ao Atlas
  da Violência.
- **E3 cai para a medida alternativa registrada (banda larga fixa).** Não há série municipal
  do 4G anterior a 2018 nos dados abertos da Anatel: os acessos móveis só vêm por DDD até
  2018 (por município só a partir de 2019), a cobertura por município começa em 2021 e as
  estações rádio-base do SMP não estão no arquivo público de estações licenciadas (só os
  radioenlaces). A banda larga fixa tem acessos por município desde 2007. Decidido antes de
  cruzar qualquer dado da Anatel com o voto.
- **Por habitante:** igrejas e MEIs usam a população do Censo 2022 em todos os anos; as taxas
  de homicídio usam as estimativas do IBGE no ano do meio de cada triênio (SIDRA 6579).

---

## Armadilhas metodológicas (valem para todas as análises)

- **Falácia ecológica:** escrever conclusões em nível de lugar ("municípios com X"),
  não de pessoa.
- **Ruído dos municípios pequenos:** pesar por eleitorado, usar encolhimento bayesiano
  ou funnel plot.
- **Teto e regressão à média:** condicionar ao valor do pleito anterior; mostrar Δ logit
  junto com Δ pp.
- **Autocorrelação espacial:** validação cruzada espacial, erros agrupados, I de Moran
  nos resíduos.
- **Denominador:** válidos, dois maiores e aptos contam histórias diferentes; o cadastro
  eleitoral é inflado onde há emigração.
- **Caminhos múltiplos de análise:** registrar hipóteses em `hipoteses.md` antes dos
  modelos confirmatórios.
- **MAUP:** conferir se os achados sobrevivem agregando por região imediata.
