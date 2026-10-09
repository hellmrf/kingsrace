# Registro de hipóteses

Registrar aqui **antes** de rodar o modelo confirmatório: a hipótese, o teste e o que
contaria como evidência contra. Depois, anotar o resultado e o notebook. Análises
exploratórias não precisam de registro, mas o que sair delas e virar afirmação precisa.

Status: `aberta` → `registrada` (teste definido) → `testada` (resultado anotado).
Detalhamento de cada hipótese em [plano.md](plano.md), seção 4.

| ID | Hipótese | Status | Teste / critério | Resultado | Notebook |
|---|---|---|---|---|---|
| A1 | Lula cai mais (Δ dois maiores, 2022→2026 1T) quanto menor o município, mesmo dentro da UF | **testada** | ver [A1](#a1) | **Sustentada.** M3: β = +0,024 (IC 95% +0,021 a +0,028); metade do gradiente bruto é composição | `02_tamanho.ipynb` |
| A2 | Queda maior onde o agro pesa mais e onde a soja avançou | **testada** | ver [A2–A4](#a2-a3-e-a4) | **Não se sustenta.** Expansão da soja: −0,0007 (IC −0,0017 a +0,0003) | `05_composicao.ipynb` |
| A3 | Participação evangélica (nível 2022 e Δ 2010–2022) prevê a queda | **testada** | ver [A2–A4](#a2-a3-e-a4) | **Não se sustenta.** Crescimento 2010→22: +0,0002 (IC −0,0009 a +0,0012) | `05_composicao.ipynb` |
| A4 | Coeficiente da cobertura do Bolsa Família muda de sinal ou cresce entre 2022 e 2026 | **testada** | ver [A2–A4](#a2-a3-e-a4) | **Sustentada.** Associação dobrou: +0,0058 (2022) → +0,0115 (2026); interação IC +0,0036 a +0,0077. A4a também | `05_composicao.ipynb` |
| A5 | Prefeito do PL/centrão eleito em 2024 aumenta o afastamento de Lula (RDD) | aberta | | | |
| A6 | Parte relevante da perda de Lula é desmobilização (abstenção), não conversão | **testada** | ver [A6](#a6) | **Não se sustenta.** Comparecimento + válidos = 5,9% da perda; o resto é fatia. A6b (abstenção maior nos redutos do PT) se sustenta, efeito pequeno | `04_decomposicao.ipynb` |
| A7 | Saldo de empregos formais 2022–2026 associado a queda menor | aberta | | | |
| A8 | Peso dos municípios pequenos na perda nacional de votos (contribuição) | **testada** | ver [A8](#a8) | **Sustentada.** AMCs < 20 mil eleitores: 21,6% do eleitorado, 28,9% da perda (1,34×); mas 71% da perda veio das maiores | `04_decomposicao.ipynb` |
| B1 | Transferências 1T→2T de 2026 favorecem Flávio, ao contrário de 2022 | aberta | | | |
| B2 | Variação da abstenção entre turnos e a quem beneficiou | aberta | | | |
| B3 | Transferências heterogêneas por região/perfil | aberta | | | |
| B4 | Previsão do 2T por município, congelada antes de 25/10/2026 | registrada | ver [B4](#b4) | | `03_previsao_2t.ipynb` |
| C1 | Clivagem do lulismo (renda, Nordeste, escolaridade, religião) ao longo de 2006–2026 | registrada | ver [C](#série-histórica-c1-c2-c4-c5) | | `06_serie.ipynb` |
| C2 | Nacionalização vs. regionalização do voto do PT (decomposição de variância) | registrada | ver [C](#série-histórica-c1-c2-c4-c5) | | `06_serie.ipynb` |
| C3 | Tipologia de trajetórias municipais 2006–2026 | exploratória | ver [C](#série-histórica-c1-c2-c4-c5) | | `06_serie.ipynb` |
| C4 | Uniformidade da variação entre pleitos | registrada | ver [C](#série-histórica-c1-c2-c4-c5) | | `06_serie.ipynb` |
| C5 | O gradiente de tamanho da A1 se repete nas transições anteriores | registrada | ver [C](#série-histórica-c1-c2-c4-c5) | | `06_serie.ipynb` |
| D1 | Queda de 2026 concentrada nas periferias evangélicas das capitais | aberta | | | |

---

## Especificações registradas

### A1

**Registrada em 2026-10-08, antes de qualquer regressão.** A exploração do
`01_panorama.ipynb` (gráficos descritivos por região e faixa de tamanho) já mostrou o
padrão bruto; o que se testa aqui é se ele sobrevive à composição dos municípios.

- **Unidade:** AMC (5.569), 1º turno.
- **Desfecho principal:** Δ logit(`pt_2p`) entre 2022 e 2026. Secundário: Δ em pp.
- **Regressor de interesse:** log(eleitores aptos em 2022), medido antes do tratamento.
  Como Δ é negativo, a hipótese prevê **coeficiente positivo** (maior → perde menos).
- **Especificação principal (M3):** MQO sem pesos, efeitos fixos de **região geográfica
  imediata** (509), erros-padrão agrupados por região imediata. Controles:
  logit(`pt_2p`) em 2022 (teto e regressão à média), `pct_urbana`, `idade_mediana`,
  `pct_evangelica`, log(`renda_pc_mediana`), `taxa_alfabetizacao`, `pct_preta_parda`,
  `pct_va_agro_2021`, `pct_renda_outras_fontes`.
- **Sequência reportada:** M0 sem controles nem efeitos fixos → M1 + efeitos fixos de UF →
  M2 + efeitos fixos de região imediata → M3 + controles. A queda do coeficiente de M0
  para M3 mede quanto do gradiente a composição explica.
- **Critério:** A1 se sustenta se, em M3, o coeficiente de log(aptos) for positivo com
  IC 95% acima de zero. Evidência contra: IC contendo zero ou coeficiente negativo, ou
  seja, o gradiente bruto se explica por composição.
- **Robustez (não muda o veredito, só o qualifica):** desfecho em pp; pesos pelo
  eleitorado; efeitos fixos de UF no lugar de região imediata; tamanho pela população do
  Censo; excluir AMCs com menos de 2 mil eleitores (ruído).
- **Secundária, sugerida pela exploração (não confirmatória):** A1b, o gradiente é mais
  fraco no Nordeste (interação log(aptos) × Nordeste em M3).

**Resultado (2026-10-08, `02_tamanho.ipynb`):**

| Modelo | β de log(eleitorado) | IC 95% |
|---|---|---|
| M0 bruto | +0,049 | +0,045 a +0,054 |
| M1 + EF de UF | +0,040 | +0,036 a +0,044 |
| M2 + EF de região imediata | +0,036 | +0,033 a +0,038 |
| **M3 + controles** | **+0,024** | **+0,021 a +0,028** |

- **Veredito: A1 se sustenta.** As quatro checagens de robustez ficam entre +0,023 e
  +0,027; em pp, +0,54 pp por unidade de log (IC +0,47 a +0,62).
- Ordem de grandeza: entre duas AMCs comparáveis da mesma região imediata, uma com 3 mil e
  outra com 300 mil eleitores, a menor perdeu ~2,5 pp a mais (5,0 pp sem controles).
- **A1b não se confirma:** interação com Nordeste = +0,001 (IC −0,006 a +0,008).
- Observações: todos os modelos usam a mesma amostra (5.569 AMCs, todas completas); o
  `pyfixest` descarta grupos de efeito fixo unitários (n = 5.567–5.568). São 510 regiões
  imediatas, não 509 como escrito acima (a definição não muda).

### B4

**Registrada em 2026-10-08, antes do 2º turno (25/10).** Método em
`src/kingsrace/models/previsao_2t.py`; previsões congeladas em
`data/reference/previsoes/` (v1 em 08/10, só com o Datafolha de 6–8/10; v2 em 24/10, com as
pesquisas finais). Cada versão tem commit e tag `previsao-2t-2026-<versão>`.

- **O que se prevê:** a fatia de Lula entre os dois finalistas, por município (5.571).
- **Nível nacional:** média das pesquisas de 2º turno, corrigida por λ × o viés de cada
  instituto no 1º turno. Central λ = 0,5; faixa de λ = 1 (viés repetido inteiro) a λ = 0.
- **Geografia (três variantes no mesmo nível):** G0 deslocamento uniforme em logit
  (central); G1 transferências por perfil de candidato; G2 uniforme + compressão de 2022.

**Como será avaliada** (com os dados do 2º turno do TSE):

1. **Nível:** erro nacional do cenário central, em pp; o resultado cai dentro da faixa?
2. **Geografia:** cada variante é recalibrada no nível real e medida pelo RMSE municipal
   (pp, sem pesos; com pesos pelo eleitorado como complemento). Vence a de menor RMSE.
3. **Erro total:** RMSE municipal das colunas exatamente como congeladas.
4. **Referência ingênua:** repetir a fatia do 1º turno (`pt_2p_1t`). O modelo só agrega
   valor se bater essa referência.
5. **Por UF:** erro do total de cada UF.

**Expectativas registradas (o que contaria como surpresa):** G0 ≤ G1 em RMSE, ou seja,
as transferências por perfil não ajudam, como no backtest de 2022 (0,95 contra 1,16 pp);
e G2 ≤ G0, ou seja, a compressão de 2022 se repete.

### A6

**Registrada em 2026-10-09, antes do cálculo.** No panorama já se viu que a abstenção
nacional (sem exterior) ficou praticamente igual entre 2022 e 2026 (20,8% e 20,8%); a
pergunta é se, mesmo assim, a mobilização diferencial explica parte da perda.

- **Unidade:** AMC, 1º turno de 2022 e de 2026, sem o exterior.
- **Decomposição (LMDI, exata e aditiva):** votos de Lula V = A · t · v · s, com A = aptos,
  t = comparecimento/aptos, v = válidos/comparecimento, s = Lula/válidos. Em cada AMC,
  ΔV = L(V₂₆, V₂₂) · [Δln A + Δln t + Δln v + Δln s], com L a média logarítmica; os quatro
  termos somados no país dão as contribuições de **eleitorado**, **comparecimento**,
  **votos válidos** (brancos e nulos) e **fatia de Lula**.
- **Critério:** A6 se sustenta se comparecimento + válidos responderem por **≥ 25%** da
  perda nacional de votos de Lula. Abaixo disso, a perda é sobretudo mudança de fatia.
- **Secundária A6b:** dentro da mesma região imediata, o comparecimento caiu mais onde o PT
  era mais forte? MQO de Δlogit(t) em logit(`pt_2p` 2022), efeitos fixos e erros agrupados
  por região imediata; sustenta-se se o coeficiente for negativo com IC 95% abaixo de zero.
- **Limite:** decomposição ecológica. Se eleitores de Lula ficaram em casa e foram
  substituídos por novos eleitores de Flávio no mesmo município, isso aparece como "fatia".

### A8

**Registrada em 2026-10-09, antes do cálculo.**

- **Medida:** a perda nacional de votos de Lula (1º turno, 2022 → 2026, sem exterior),
  somada por grupo de AMCs (faixa de eleitorado de 2022 × região), com a mesma
  decomposição LMDI da A6.
- **Hipótese:** as AMCs com **menos de 20 mil eleitores** em 2022 respondem por uma fração
  da perda nacional **maior** que a sua fração do eleitorado de 2022.
- **Critério:** sustenta-se se fração da perda > fração do eleitorado. Também se reporta a
  razão entre as duas (quantas vezes o peso eleitoral) e a tabela completa por grupo.

**Resultado A6 e A8 (2026-10-09, `04_decomposicao.ipynb`):** Lula perdeu 3,40 milhões de
votos (1º turno, sem exterior). Contribuições: eleitorado +0,88 mi; comparecimento +0,07 mi;
brancos e nulos −0,27 mi; fatia de Lula −4,07 mi. **A6 não se sustenta** (5,9% < 25%).
A6b: −0,014 (IC 95% −0,026 a −0,003), sustentada com efeito pequeno (~−0,25 pp de
comparecimento por +1 logit de PT em 2022). **A8 se sustenta:** razão 1,34.

### A2, A3 e A4

**Registradas em 2026-10-09, antes de qualquer regressão com as medidas novas.** As três
pistas vieram dos controles do M3 da A1 (`02_tamanho.ipynb`): agro (`pct_va_agro_2021`),
religião (`pct_evangelica`) e transferências (`pct_renda_outras_fontes`). Para não testar
com os dados que as sugeriram, cada uma usa uma **medida nova**, e a medida antiga fica
como controle.

**Base comum (= M3 da A1):** AMC, Δ logit(`pt_2p`) 1º turno 2022 → 2026; MQO sem pesos;
efeitos fixos e erros agrupados por região imediata; controles log(aptos 2022),
logit(`pt_2p` 2022), `pct_urbana`, `idade_mediana`, `pct_evangelica`, log(renda mediana),
`taxa_alfabetizacao`, `pct_preta_parda`, `pct_va_agro_2021`, `pct_renda_outras_fontes`.

- **A2 · soja:** acrescenta `exp_soja_pct_territorio` (expansão da área de soja 2021→2025,
  em pp do território) e `soja_2021_pct_territorio` como controle de nível. Hipótese:
  coeficiente da expansão **negativo**. Sustenta-se se o IC 95% estiver abaixo de zero.
- **A3 · religião:** acrescenta `delta_evangelica` (crescimento 2010→2022, pp), com o nível
  de 2022 já entre os controles. Hipótese: coeficiente **negativo** (onde os evangélicos
  cresceram mais, o PT perdeu mais). Sustenta-se se o IC 95% estiver abaixo de zero.
  Amostra: AMCs com dado de 2010.
- **A4 · transferências (principal, a formulação original):** o PT passou a ganhar mais
  onde o programa é maior, quando o programa virou "dele"? Painel empilhado 2022 e 2026 com
  logit(`pt_2p`) no nível como desfecho; cobertura = famílias no programa por 100
  habitantes (Auxílio Brasil em set/2022; Bolsa Família em set/2026); todos os controles
  da base (menos o logit de 2022) interagidos com o ano; efeitos fixos região imediata ×
  ano. Hipótese: interação cobertura × 2026 **positiva**. Sustenta-se se o IC 95% estiver
  acima de zero.
- **A4a · complementar:** no modelo de Δ da base, acrescenta `familias_bf_100hab_2026`.
  Hipótese: coeficiente **positivo** (mais Bolsa Família, queda menor).

São quatro testes. Sem correção formal para comparações múltiplas, mas os p-valores são
reportados e um resultado com p entre 0,01 e 0,05 é tratado como fraco.

**Resultado A2–A4 (2026-10-09, `05_composicao.ipynb`):**

| Teste | Coeficiente | IC 95% | p | Veredito |
|---|---|---|---|---|
| A2 · expansão da soja (por pp do território) | −0,0007 | −0,0017 a +0,0003 | 0,19 | não se sustenta |
| A3 · crescimento evangélico (por pp) | +0,0002 | −0,0009 a +0,0012 | 0,74 | não se sustenta |
| A4 · cobertura × 2026 (painel, nível) | +0,0057 | +0,0036 a +0,0077 | < 0,001 | **sustenta-se** |
| A4a · Bolsa Família 2026 (modelo de Δ) | +0,0044 | +0,0032 a +0,0056 | < 0,001 | **sustenta-se** |

Na A4a, 1 desvio-padrão de cobertura (~7,6 famílias por 100 habitantes) equivale a +0,034
em Δ logit, mais que 1 desvio-padrão do tamanho do município (+0,027).

### Série histórica (C1, C2, C4, C5)

**Registradas em 2026-10-09, antes de qualquer análise da série** (até aqui só foram
conferidos totais e consistência dos dados de 2006–2018).

**Comum:** AMC (5.562, as mesmas em todos os pleitos); fatia do PT entre os dois maiores
(`pt_2p`), em logit. Pleitos: 1º turno de 2006, 2010, 2014, 2018, 2022 e 2026 (o 2º turno
como complemento). Candidatos do PT: Lula (2006, 2022, 2026), Dilma (2010, 2014), Haddad
(2018). **Limite:** as covariáveis são do Censo 2022 (e 2010 para religião); para os pleitos
antigos elas medem a estrutura dos municípios, não o retrato da época.

- **C1 · a clivagem do lulismo.** Por pleito, MQO do logit de `pt_2p` em variáveis
  padronizadas (log da renda mediana, alfabetização, % evangélica, % urbana, idade mediana)
  e Nordeste, sem efeitos fixos, erros agrupados por região imediata. Hipóteses:
  (a) renda com coeficiente **negativo em todos os pleitos**; (b) |renda| **maior em 2022 que
  em 2006** (a clivagem de classe se aprofundou); (c) % evangélica **mais negativa em 2022 e
  2026 que em 2006**.
- **C2 · regionalização.** Decomposição da variância do logit de `pt_2p` (ponderada pelo
  eleitorado) em entre UFs, entre regiões imediatas dentro da UF e dentro da região
  imediata. Hipótese: a fração **entre UFs é maior em 2022 que em 2006** (o voto ficou mais
  regional).
- **C4 · uniformidade.** Para cada par de 1ºs turnos consecutivos, o desvio-padrão do
  Δ logit entre AMCs (heterogeneidade) e a correlação entre os dois pleitos (estabilidade).
  Hipótese: 2022→2026 é **mais uniforme** (menor desvio-padrão) que a média das quatro
  transições anteriores.
- **C5 · o gradiente de tamanho na série.** Para cada par de 1ºs turnos consecutivos,
  Δ logit ~ log(aptos no pleito inicial) + logit(`pt_2p` inicial), efeitos fixos e erros
  agrupados por região imediata (sem as covariáveis do Censo, que são posteriores aos
  pleitos antigos). Hipótese: o coeficiente do tamanho é **positivo com IC 95% acima de zero
  em pelo menos 3 das 4 transições anteriores** a 2022→2026. Senão, o gradiente é
  específico do período recente.
- **C3 · trajetórias (exploratória, sem teste):** agrupamento das AMCs pela trajetória do
  logit de `pt_2p` nos seis 1ºs turnos.
