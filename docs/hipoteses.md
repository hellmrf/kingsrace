# Registro de hipóteses

Registrar aqui **antes** de rodar o modelo confirmatório: a hipótese, o teste e o que
contaria como evidência contra. Depois, anotar o resultado e o notebook. Análises
exploratórias não precisam de registro, mas o que sair delas e virar afirmação precisa.

Status: `aberta` → `registrada` (teste definido) → `testada` (resultado anotado).
Detalhamento de cada hipótese em [plano.md](plano.md), seção 4.

| ID | Hipótese | Status | Teste / critério | Resultado | Notebook |
|---|---|---|---|---|---|
| A1 | Lula cai mais (Δ dois maiores, 2022→2026 1T) quanto menor o município, mesmo dentro da UF | **testada** | ver [A1](#a1) | **Sustentada.** M3: β = +0,024 (IC 95% +0,021 a +0,028); metade do gradiente bruto é composição | `02_tamanho.ipynb` |
| A2 | Queda maior onde o agro pesa mais e onde a soja avançou | aberta | | | |
| A3 | Participação evangélica (nível 2022 e Δ 2010–2022) prevê a queda | aberta | | | |
| A4 | Coeficiente da cobertura do Bolsa Família muda de sinal ou cresce entre 2022 e 2026 | aberta | | | |
| A5 | Prefeito do PL/centrão eleito em 2024 aumenta o afastamento de Lula (RDD) | aberta | | | |
| A6 | Parte relevante da perda de Lula é desmobilização (abstenção), não conversão | registrada | ver [A6](#a6) | | `04_decomposicao.ipynb` |
| A7 | Saldo de empregos formais 2022–2026 associado a queda menor | aberta | | | |
| A8 | Peso dos municípios pequenos na perda nacional de votos (contribuição) | registrada | ver [A8](#a8) | | `04_decomposicao.ipynb` |
| B1 | Transferências 1T→2T de 2026 favorecem Flávio, ao contrário de 2022 | aberta | | | |
| B2 | Variação da abstenção entre turnos e a quem beneficiou | aberta | | | |
| B3 | Transferências heterogêneas por região/perfil | aberta | | | |
| B4 | Previsão do 2T por município, congelada antes de 25/10/2026 | registrada | ver [B4](#b4) | | `03_previsao_2t.ipynb` |
| C1 | Clivagem do lulismo (renda, Nordeste, escolaridade, religião) ao longo de 2006–2026 | aberta | | | |
| C2 | Nacionalização vs. regionalização do voto do PT (decomposição de variância) | aberta | | | |
| C3 | Tipologia de trajetórias municipais 2006–2026 | aberta | | | |
| C4 | Uniformidade da variação entre pleitos | aberta | | | |
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
