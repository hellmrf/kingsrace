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

**Data:** 2026-10-09 · **Status:** em vigor; leitura do CNPJ e pipeline revistos em D9

- **Cache do DVC em hardlinks** (`dvc config --local cache.type hardlink,symlink`, só nesta
  máquina): cada bruto existe uma vez no disco, não duas. O DVC deixa os brutos só para
  leitura; o código nunca os altera.
- **CNPJ (Receita) fora do R2:** são ~7 GB por versão, além da cota gratuita. Os `.dvc` têm
  `push: false` e guardam URL + hash; os zips de Estabelecimentos são baixados, processados
  e apagados um por vez (`python -m kingsrace.ingest.receita todos`, retomável). Refazer do
  zero = baixar de novo da Receita (que mantém as versões mensais anteriores no
  compartilhamento público). A leitura direta do zip pela extensão `zipfs` foi trocada em D9.
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

## D8 — Resultados versionados: notebooks como etapas do DVC, com DVCLive

**Data:** 2026-10-09 · **Status:** em vigor

Até aqui os números de cada teste viviam só no kernel dos notebooks e eram copiados à mão
para `hipoteses.md`; o DVC não via nenhum resultado. Agora:

- **Cada notebook é uma etapa** (`nb_<nn>_<nome>` no `dvc.yaml`), executada pelo papermill.
  Ele registra pelo DVCLive (`kingsrace.resultados`) o que vai para o registro, com o ID da
  hipótese no nome: `A1/M3/beta`, `E2a/salto/p`, `B4/backtest_2022/G0/rmse_pp`; vereditos
  como `<ID>/sustenta` (0/1), pelo critério registrado.
- **O que fica onde:** `resultados/<nb>/metrics.json` e as tabelas de coeficientes
  (`plots/custom/`) no **git**, para comparar commits e branches sem baixar nada; o
  notebook executado (`reports/notebooks/`) e os PNGs dos gráficos (`plots/images/`) no
  **cache do DVC** (R2). O notebook no git continua sem saídas.
- **Tabelas de coeficientes** usam o template `.dvc/plots/coeficientes.json` (ponto e IC de
  95%, uma cor por revisão): `dvc plots diff main` põe lado a lado o mesmo teste em duas
  revisões.
- **Confirmatório é o que está comitado:** um resultado entra em `hipoteses.md` a partir do
  `metrics.json` de um commit, gerado por `just resultados` com `dvc status` limpo. Rodar o
  notebook à mão grava os mesmos arquivos, mas conta como rascunho.
- **Experimentos (`dvc exp run -S`) são exploração.** Só os parâmetros da seção
  `exploracao` do `params.yaml` servem para isso. `serie_e` (Holm) e `previsao_2t` vêm do
  registro e mudam só com nova entrada nele. Um experimento fica fora do git até um
  `dvc exp apply`/`dvc exp branch` explícito.
- **Limite:** o hash do notebook inclui as saídas; `just resultados` roda o `nbstripout`
  antes do `dvc repro` para que um notebook aberto e executado não pareça alterado.

---

## D9 — Pipeline completo para a série E e leitura do CNPJ em máquinas de 8 GB

**Data:** 2026-10-09 · **Status:** em vigor; revê em parte D7

- **Etapas novas no `dvc.yaml`:** `rais`, `sim`, `cnpj` e `mecanismos`, antes rodadas à
  mão (as saídas só existiam na máquina que as gerou).
- **`receita` é uma etapa congelada (`frozen`).** O `todos` chama `dvc import-url`, que não
  roda dentro do `dvc repro`. Para refazer: rodar o `todos` fora do DVC e `dvc commit
  receita`. As três parquets da Receita (pequenas) **vão para o R2**: uma máquina nova as
  recebe com `dvc pull`, sem baixar 7 GB. Os zips continuam fora (`push: false`), então o
  `dvc pull` ainda acusa a falta deles; isso é esperado.
- **Leitura do CNPJ:** cada CSV é extraído para o disco já em UTF-8, lido pelo DuckDB e
  apagado. A extensão `zipfs` descomprime o arquivo inteiro na memória (7 GB num zip de
  Estabelecimentos) e derrubava uma máquina de 8 GB; o latin-1 nativo do DuckDB recusa os
  bytes 0x80–0x9F que aparecem em alguns registros (0x8F em Estabelecimentos0 de 2026-09); o
  ISO_8859_1 da extensão `encodings` aceita, mas é ~15× mais lento. O DuckDB roda com
  memória limitada (`KINGSRACE_DUCKDB_MEMORIA`, 2 GB por padrão) e leitor sequencial (o
  paralelo recusa os CSVs da Receita com `strict_mode=false`). O escape é fixo em `"`: o
  detector escolheu `'` em Estabelecimentos4, e `"SABESP'"` engolia os campos seguintes.

---

## D10 — Série E: E2b, E4, E5, E7, E2d e E0b; duas correções nos homicídios

**Data:** 2026-10-10 · **Status:** em vigor

- **SIM de 2003 a 2005 com código de 7 dígitos.** Até 2005 o SIM grava o município de
  residência com o dígito verificador; a junção por 6 dígitos descartava todos os homicídios
  desses anos sem erro, e a E5 completava os anos ausentes com zero (placebo de 2006→2010
  falso). Agora o código é cortado para 6 dígitos na ingestão, e a E5 deixa de fora a
  transição que tiver algum ano do triênio ausente. O teste `test_dados` exige ≥ 96% dos
  homicídios de cada ano atribuídos a uma AMC (sobram 1–3% em "município ignorado").
- **População zero não é população.** Nazária (PI) não tem estimativa própria em 2004 (o
  SIDRA traz "-", que vira 0); a taxa de homicídios dava 0/0. Na E5, população 0 conta como
  ausente. O NaN que isso produzia derrubava o kernel dentro do `pyfixest`, sem mensagem: o
  `base_transicoes` agora descarta qualquer medida não finita.
- **Coligação presidencial do PT (E2d)** lida na própria etapa `religiosos`, do
  `consulta_cand_{ano}_BRASIL.csv` (candidatura a presidente do PT, 1º turno,
  `DS_COMPOSICAO_COLIGACAO`); as federações de 2022 entram pelos partidos que as compõem.
  O voto religioso é separado em: da coligação, do PRB/Republicanos e o total nominal da
  coligação (religiosos ou não), sempre sobre os válidos para deputado.
- **Duas famílias de Holm** (`params.yaml`, `serie_e`): a família 1 são os 11 testes ★; a
  família 2 (A5, E2d, E3b, E3c) foi registrada em 10/10. Com testes pendentes, cada um sai como
  "rejeita", "não rejeita" ou "pendente" pela regra de `models/event_study.holm`.
- **`event_study`** ganhou o painel empilhado genérico (`empilha`), combinações lineares com
  erro agrupado (`contraste`), medidas sem padronizar e várias medidas no mesmo modelo (E2d), e
  a persistência da E0b (`persistencia`). O `salto` é o mesmo de antes, escrito com as peças
  novas.
- **Intermediários do TSE** (`cache: false`) tinham sumido do disco desta máquina; a
  reconversão a partir dos zips mudou o hash dos parquets intermediários (a ordem das linhas
  do DuckDB não é fixa), mas não o de nenhum dado processado.

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
