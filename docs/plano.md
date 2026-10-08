# kingsrace: plano de pesquisa sobre comportamento eleitoral presidencial no Brasil (2006–2026)

## Contexto

O objetivo é entender as nuances do voto presidencial brasileiro com análise exploratória, modelagem e visualização, em dois eixos:
**(a)** 2022 → 2026, mais a dinâmica entre o 1º e o 2º turno de 2026;
**(b)** a série histórica 2006–2026.

Ponto de partida: a observação de que Lula perdeu mais votos entre 2022 e 2026 quanto menor o município.

Situação hoje (08/10/2026), a confirmar com os arquivos do TSE:

- **1º turno (04/10):** Flávio Bolsonaro (PL) 47,03% (56,1 mi), Lula (PT) 45,16% (53,9 mi), Augusto Cury 2,89%, Renan Santos 2,24%, Caiado 2,18%, Zema 0,27%.
- **Abstenção:** 21,1%, a maior desde 1998.
- **Pesquisas:** erraram a direção. O Datafolha de 1º/10 dava Lula 45% contra Flávio 40% nos válidos.
- **2º turno:** 25/10/2026. Os dados de 2T só existirão depois disso, por isso o roteiro tem etapas.
- **Referência 2022, 1º turno:** Lula 48,43% (57.259.504), Bolsonaro 43,20% (51.072.345).
- **Referência 2022, 2º turno:** Lula 50,90% (60.345.999), Bolsonaro 49,10% (58.206.354).

Decisões tomadas:

- Série de 2006 a 2026.
- Unidade principal é o **município**, com zoom em **local de votação/seção** para análises dentro das cidades.
- **Python**.
- Primeiro marco: **notebooks + relatório Quarto**. Um portal público fica para um marco futuro, então convém manter o processamento já pensado para ser republicável.

Versionamento de dados: DVC com remoto no Cloudflare R2 (ver `docs/decisoes.md`, D1).

---

## 1. Fontes de dados

### Núcleo (necessárias para o 1º marco)

| Fonte | O que traz | Granularidade | Acesso |
|---|---|---|---|
| **TSE: `votacao_candidato_munzona_{ano}`** | votos por candidato/turno | município × zona | `cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/` |
| **TSE: `detalhe_votacao_munzona_{ano}`** | aptos, comparecimento, abstenção, brancos, nulos | município × zona | idem, `detalhe_votacao_munzona/` |
| **TSE: `votacao_secao_{ano}_BR`** (presidente) | votos por seção | seção | idem, `votacao_secao/`; 2026 já publicado e atualizado ao fim de cada turno |
| **TSE: `detalhe_votacao_secao_{ano}`** | comparecimento/abstenção por seção | seção | idem |
| **TSE: `eleitorado_local_votacao_{ano}`** | locais de votação com endereço e **lat/long** (anos recentes) | local de votação | portal de dados abertos do TSE, "Eleitorado" |
| **TSE: perfil do eleitorado** | idade, sexo, escolaridade dos eleitores aptos | município/zona (seção nos anos recentes) | portal de dados abertos do TSE |
| **TSE: resultados municipais 2016/2020/2024** | partido do prefeito eleito e margem de vitória | município | `votacao_candidato_munzona` dos anos municipais |
| **Base dos Dados: diretórios** | tabela de correspondência código TSE ↔ código IBGE de município, região imediata, UF | município | `basedosdados` (BigQuery; o plano gratuito basta) |
| **IBGE: Censo 2022 + Censo 2010** | população, urbanização, raça/cor, idade, alfabetização, **religião** (resultados preliminares da amostra de 2022, divulgados em jun/2025), renda (se já divulgada para 2022) | município (setor censitário para o zoom) | SIDRA (`sidrapy`), FTP do IBGE |
| **IBGE: estimativas populacionais, PIB dos Municípios** | população por ano; PIB per capita; **valor adicionado por setor** (peso do agro, da administração pública) | município × ano | SIDRA |
| **IBGE: REGIC + tipologia rural-urbana** | hierarquia urbana e centralidade, uma medida de "tamanho" melhor que só a população | município | site do IBGE |
| **MDS / Portal da Transparência: Bolsa Família / Auxílio Brasil** | famílias beneficiárias e valores | município × mês | VIS DATA (MDS), Portal da Transparência |
| **geobr** | malhas de município, setor, região imediata, UF | geometrias | pacote `geobr` (Python) |

### Complementares (entram se uma hipótese pedir)

- **MapBiomas / PAM-IBGE / Censo Agro 2017**: área de soja e pasto, expansão da fronteira agrícola.
- **RAIS/CAGED**: saldo de empregos formais entre 2022 e 2026 por município, para testar voto econômico local.
- **CNPJ da Receita Federal (CNAE 9491-0/00, organizações religiosas)**: indicador anual de presença de igrejas por município. Complementa o Censo, que mede religião só a cada 12 anos.
- **Siconfi/FINBRA**: dependência de transferências (FPM) e peso do emprego público.
- **Anatel**: acesso à banda larga, como indicador do ambiente informacional.
- **Pesquisas eleitorais** (agregadores e registros do TSE): para o erro das pesquisas de 2026, só em nível UF/nacional.

> Prioridade: TSE direto para tudo de 2026, porque a Base dos Dados deve demorar a incorporar 2026. A Base dos Dados entra pelos diretórios e pela correspondência de códigos.

---

## 2. Harmonização e processamento (a parte mais trabalhosa)

1. **Correspondência TSE ↔ IBGE.** O código de município do TSE (5 dígitos) não é o do IBGE (7 dígitos). Usar o diretório da Base dos Dados e falhar o pipeline se sobrar código sem correspondência.
2. **Área Mínima Comparável (AMC).** Municípios instalados depois de 2006 (os 5 de 2013 e possíveis criações recentes, a verificar) são somados ao município de origem em uma chave `amc_id`, usada nas análises longitudinais.
3. **Votos no exterior (UF = ZZ)**: guardados à parte, fora dos modelos municipais.
4. **Tabela de candidatos por pleito.** Uma tabela `candidatos.csv` mapeia o candidato do PT e o principal adversário em cada pleito:
   - 2006: Lula × Alckmin
   - 2010: Dilma × Serra
   - 2014: Dilma × Aécio
   - 2018: Haddad × Bolsonaro
   - 2022: Lula × Bolsonaro
   - 2026: Lula × Flávio
5. **Métricas padronizadas** (por unidade × ano × turno):
   - participação nos votos válidos;
   - **participação nos dois maiores (PT / (PT + adversário))**, a métrica principal entre anos, porque os candidatos menores mudam a cada pleito;
   - participação sobre os eleitores aptos (soma o efeito da abstenção);
   - logit da participação; Δ em pontos percentuais e Δ em logit.
6. **Painel em parquet:** `painel_municipio.parquet` com uma linha por `amc_id × ano × turno`, juntando votos, comparecimento e covariáveis. As covariáveis anuais vêm interpoladas ou do ano mais próximo, com a defasagem registrada.
7. **Zoom em seção.** Agregar seções por **local de votação**: as seções são remanejadas entre pleitos, os locais são mais estáveis. A geocodificação pelas coordenadas do TSE só é confiável nos anos recentes, então o zoom fica em **2018/2022/2026** e em algumas capitais. Os locais são ligados aos setores censitários de 2022 por junção espacial (raio ou Voronoi).
8. **Entre turnos de 2026.** Mesma seção e mesmo eleitorado nos dois turnos, então dá para casar 1T e 2T por seção, 1:1.

---

## 3. Workspace e stack

```
kingsrace/
├── pyproject.toml            # uv; Python 3.12
├── justfile                  # receitas do dia a dia (setup, test, lint, repro, push/pull)
├── dvc.yaml                  # pipeline: ingest → harmonize → features (a partir do M0b)
├── data/
│   ├── raw/{tse,ibge,mds,...}/   # imutável; versionado pelo DVC (git guarda só os .dvc)
│   ├── interim/              # descartável
│   ├── processed/            # parquet: painel_municipio, painel_local (saídas do dvc.yaml)
│   └── reference/            # tabelas pequenas feitas à mão, no git (candidatos.csv, previsão 2T)
├── src/kingsrace/
│   ├── ingest/               # um módulo por fonte, idempotente
│   ├── harmonize/            # correspondência, AMC, mapeamento de candidatos
│   ├── features/             # covariáveis e métricas
│   ├── models/
│   └── viz/                  # tema e paleta únicos, funções de mapa
├── notebooks/                # numerados: 01_sanidade, 10_eda_2022_2026, 20_..., etc.
├── reports/                  # projeto Quarto (relatório do 1º marco)
├── docs/
│   ├── hipoteses.md          # hipóteses registradas ANTES dos modelos confirmatórios
│   ├── dicionario_dados.md
│   └── decisoes.md
└── tests/                    # pandera + pytest para esquemas e reconciliação
```

**Bibliotecas:**

| Área | Pacotes |
|---|---|
| Dados | `polars`, `duckdb`, `pyarrow` |
| Geo | `geopandas`, `geobr`, `libpysal` / `esda` / `spreg` / `mgwr` (PySAL) |
| Estatística | `pyfixest` (efeitos fixos), `statsmodels`, `pymc` + `bambi` + `arviz`, `rdrobust`, `pyei` (inferência ecológica) |
| ML | `lightgbm`, `shap`, `scikit-learn` |
| Visualização | `altair`/`plotly` (interativo), `matplotlib` (estático) |
| Relatório | Quarto |
| Acesso a dados | `sidrapy`, `basedosdados`, `httpx` |
| Versionamento de dados | DVC com remoto no Cloudflare R2; `nbstripout` para notebooks (ver `decisoes.md`, D1) |

As bibliotecas de análise entram no `pyproject.toml` no marco em que forem usadas.

---

## 4. Questões e hipóteses

### A. A geografia da queda de Lula, 2022 → 2026 (1º turno contra 1º turno)

- **A1, tamanho do município.** A queda de Lula (Δ dois maiores) cresce conforme o município diminui.
  - **Testar se é tamanho ou composição.** Pequeno costuma significar Nordeste, rural, agro, envelhecido.
  - Comparar dentro da mesma UF e da mesma região imediata (efeitos fixos) e somar controles aos poucos.
  - Conferir que o padrão sobrevive em Δ logit, não só em Δ pp, por causa de efeitos de teto e regressão à média nos redutos com mais de 80% em 2022.
  - Conferir que se olha o **Δ com sinal**, não a magnitude: ruído amostral infla |Δ| nos municípios pequenos.
- **A2, agro e fronteira agrícola.** A queda é maior onde o agro pesa mais no valor adicionado e onde a soja avançou (Centro-Oeste, MATOPIBA).
- **A3, religião.** A participação evangélica em 2022, e o crescimento dela entre 2010 e 2022, preveem a queda.
- **A4, Bolsa Família.** Em 2022, o Auxílio Brasil de R$ 600 era de Bolsonaro; em 2026, o Bolsa Família é de Lula. A hipótese é que o coeficiente da cobertura do programa muda de sinal ou cresce entre 2022 e 2026.
- **A5, máquinas locais.** Municípios com prefeito do PL ou do centrão eleito em 2024 se afastaram mais de Lula.
  - **Desenho causal:** RDD em eleições municipais de 2024 decididas por pouco (PL contra não-PL, PT contra não-PT), com o voto presidencial de 2026 como resultado.
- **A6, desmobilização ou conversão.** Separar a perda de votos de Lula em duas partes: queda de comparecimento (a abstenção recorde) e eleitores que mudaram de voto.
  - Pergunta: a abstenção subiu mais nos redutos de Lula?
  - Cuidado com cadastro eleitoral inflado (mortos, quem se mudou) nos municípios pequenos que perdem população.
- **A7, voto econômico local.** O saldo de empregos formais (CAGED) entre 2022 e 2026 está associado a uma queda menor.
- **A8, contribuição.** Mesmo que os pequenos tenham variado mais, de onde vieram os ~3,4 milhões de votos a menos? Decompor a perda nacional por faixa de tamanho × região. Isso calibra a importância prática do achado A1.

### B. Entre o 1º e o 2º turno de 2026 (depois de 25/10)

- **B1, transferências.** Matriz de transição 1T → 2T: votos de Cury, Renan, Caiado, brancos/nulos e abstenção para Flávio, Lula, branco/nulo e abstenção.
  - Inferência ecológica em nível de seção, que é crível aqui porque o eleitorado é idêntico nos dois turnos.
  - Comparar com 2022, quando os votos de Ciro e Tebet foram para Lula.
- **B2, comparecimento.** A abstenção caiu no 2T? Onde caiu, e a quem beneficiou?
- **B3, heterogeneidade.** As transferências variam por região e por perfil do município?
- **B4, previsão congelada.** Antes de 25/10, prever o resultado do 2T por município a partir do 1T e das covariáveis. Commitar a previsão com data e avaliar depois: é um teste fora da amostra genuíno.

### C. Série histórica 2006–2026

- **C1, realinhamento do lulismo.** Acompanhar, eleição a eleição, os coeficientes de renda, Nordeste, escolaridade e religião no voto do PT. Mostra quando a clivagem se formou (2006), se estabilizou e se agora se desfaz.
- **C2, nacionalização ou regionalização.** Decompor a variância do voto do PT em três níveis: entre UFs, entre municípios dentro da UF, e entre locais dentro do município. Medir também o I de Moran ao longo do tempo e a fração de municípios com vitória acima de 70%.
- **C3, estabilidade e "viradas".** Correlação do voto municipal entre pleitos. Agrupar trajetórias de 2006 a 2026 em tipos, como reduto estável, migrou para o bolsonarismo, voltou ao PT.
- **C4, uniformidade da variação.** A variação de um pleito para o outro é uniforme (uma onda nacional) ou heterogênea? Comparar o desvio-padrão da variação em cada par de pleitos.

### D. Zoom intraurbano (capitais selecionadas, 2018/2022/2026)

- **D1.** Gradiente centro-periferia da variação 2022 → 2026, cruzado com renda, raça e religião do setor censitário. Hipótese: a queda de 2026 se concentra nas periferias evangélicas.

---

## 5. Modelagem: do mais simples ao mais sofisticado

1. **Descritiva:** binscatter e LOWESS de Δ contra log(eleitorado), por região; funnel plot de Δ contra tamanho para separar sinal de ruído.
2. **Regressão ponderada com efeitos fixos** (`pyfixest`):
   - resultado: Δ dois maiores (pp e logit);
   - pesos: eleitorado;
   - efeitos fixos: UF ou região imediata;
   - erros-padrão agrupados por região imediata.
3. **Diagnóstico espacial:** I de Moran dos resíduos; modelos de defasagem e de erro espacial (`spreg`); MGWR para ver onde o efeito do tamanho muda de sinal ou de intensidade.
4. **Modelo hierárquico bayesiano** (`bambi`/PyMC):
   - votos do PT sobre válidos com verossimilhança beta-binomial;
   - intercepto e inclinação de log(tamanho) variando por região/UF;
   - encolhe os municípios minúsculos para a média, o que resolve o ruído.
5. **ML para heterogeneidade:** LightGBM + SHAP prevendo Δ a partir de ~50 covariáveis, com **validação cruzada espacial** (blocos por UF ou região), para encontrar não linearidades e interações. É ferramenta de descoberta, não de inferência causal.
6. **Desenhos causais:** RDD nas eleições municipais de 2024 decididas por pouco (A5, com `rdrobust`).
7. **Inferência ecológica:** `pyei`, com a variante R×C multinomial-Dirichlet (B1), aplicada aos pares de seções 1T/2T.
8. **Trajetórias:** agrupamento (k-means/GMM) sobre os vetores de participação do PT de 2006 a 2026 (C3).
9. **Previsão do 2T** (B4): modelo de variação sobre o 1T com covariáveis, validado retroativamente em 2022 (prever o 2T de 2022 a partir do 1T de 2022) antes de aplicar a 2026.

---

## 6. Visualizações

- **Coroplético da variação de Lula 2022 → 2026**, com escala divergente centrada em zero.
  - Mapas por área exageram os municípios grandes da Amazônia, então acompanhar sempre de um **cartograma** (Dorling ou hexágonos, proporcional ao eleitorado) ou de um mapa de pontos.
- **Mapa de setas de variação** (estilo NYT): seta por município, inclinação = variação, comprimento ∝ votos.
- **Binscatter** de Δ contra log(eleitorado), por região, mais o **funnel plot**.
- **Cascata (waterfall)** da contribuição de cada faixa de tamanho × região para a perda nacional (A8).
- **Coeficientes ao longo do tempo**, 2006–2026 (C1).
- **Pequenos múltiplos** das trajetórias agrupadas (C3).
- **Sankey 1T → 2T** com intervalos de incerteza (B1).
- **Diagrama ternário** Lula/Flávio/outros por município.
- **Mapas intraurbanos** de locais de votação nas capitais (D1).

Carregar a skill `dataviz` antes de escrever o código dos gráficos, para paleta e tema consistentes, que o portal futuro herda.

---

## 7. Armadilhas metodológicas (vão para `docs/decisoes.md`)

- **Falácia ecológica:** correlação entre municípios não é comportamento individual. Escrever as conclusões em nível de lugar ("municípios com X"), não de pessoa.
- **Ruído dos municípios pequenos:** municípios com menos de 2 mil eleitores dominam as caudas. Usar pesos, encolhimento bayesiano ou funnel plot.
- **Teto e regressão à média:** sempre condicionar ao valor de 2022 e mostrar Δ logit junto com Δ pp.
- **Autocorrelação espacial:** infla a significância. Usar validação cruzada espacial, erros agrupados e I de Moran.
- **Denominador:** válidos, dois maiores ou aptos contam histórias diferentes, porque a abstenção foi de 21%. O cadastro eleitoral é inflado onde há emigração.
- **Caminhos múltiplos de análise:** registrar as hipóteses em `docs/hipoteses.md` antes dos modelos confirmatórios e separar notebooks exploratórios de confirmatórios. O 2T de 2026 é o conjunto de teste natural.
- **MAUP (problema da unidade de área modificável):** conferir se os achados sobrevivem quando se agrega por região imediata.

---

## 8. Roteiro

| Marco | Quando | Entregas |
|---|---|---|
| **M0a: fundação** | ✅ 08/10 | Mover este plano para `docs/plano.md`; `git init` + `.gitignore`; `uv` com o esqueleto da seção 3; DVC inicializado (remoto R2 a configurar com as credenciais); `nbstripout`; docs de decisões, hipóteses e dicionário.  |
| **M0b: ingestão e painel** | ✅ 08/10 | Escopo reduzido a **2022 e 2026** (baixar só o que se usa agora). Votação por seção + detalhe por zona (presidente), correspondência TSE↔IBGE própria, AMC, `candidatos.csv`, `painel_municipio`/`painel_amc`, testes de reconciliação. Ver `decisoes.md` (D4). |
| **M1a: 2022 → 2026** | até ~24/10 | Covariáveis do núcleo (Censo, PIB, Bolsa Família, prefeitos 2024). EDA da seção A. Replicar o achado A1 com controles. **Previsão do 2T congelada e commitada antes de 25/10** (B4). |
| **M1b: entre turnos** | depois de 25/10, quando o TSE atualizar os arquivos | Ingestão do 2T de 2026; inferência ecológica (B1); B2/B3; avaliação da previsão. |
| **M1c: série histórica** | novembro | Ingestão de 2006–2018 (incluir os anos em `params.yaml` e revisar `candidatos.csv`, overrides e AMC). Seção C: coeficientes ao longo do tempo, decomposição de variância, trajetórias. |
| **M1d: intraurbano** | depois de M1c | Seção D em 2 ou 3 capitais (por exemplo SP, Salvador, Recife). |
| **M1e: relatório** | ao fim | Quarto consolidando os achados, com mapas e gráficos interativos. |
| **M2: portal público** | futuro | Fora do escopo agora. O painel em parquet + `viz/` já ficam reaproveitáveis. |

---

## 9. Verificação

- **Reconciliação com totais oficiais:** a soma do painel por candidato, turno e ano bate exatamente com o total nacional do TSE. Exemplos: 2022 1T Lula 57.259.504; 2026 1T Flávio 56.104.503 e Lula 53.879.538, confirmar no relatório de totalização.
- **Consistência entre níveis:** soma das seções = soma de munzona = total da UF, para cada pleito.
- **Correspondência completa:** zero códigos sem par entre TSE e IBGE; número de AMC estável entre os anos.
- **Esquemas:** `pandera` em cada parquet do `processed/`, rodando no `pytest`.
- **Reprodutibilidade:** `dvc repro` refaz tudo de `raw/` até `processed/`; cada arquivo bruto tem um `.dvc` com URL e hash, e `dvc pull` em outra máquina reproduz o mesmo estado.
- **Sanidade da modelagem:** replicar um fato conhecido antes de buscar coisas novas. Por exemplo, a correlação negativa entre IDH e voto em Lula em 2022 e a inversão regional de 2006 descrita por Singer.
