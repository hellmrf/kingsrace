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
| A5 | Prefeito de direita eleito em 2024 aumenta o afastamento de Lula em 2022→2026 (RDD) | registrada (fundida com a E1b) | ver [módulo RDD](#módulo-rdd-a5--e1b) | | |
| A6 | Parte relevante da perda de Lula é desmobilização (abstenção), não conversão | **testada** | ver [A6](#a6) | **Não se sustenta.** Comparecimento + válidos = 5,9% da perda; o resto é fatia. A6b (abstenção maior nos redutos do PT) se sustenta, efeito pequeno | `04_decomposicao.ipynb` |
| A7 | Saldo de empregos formais 2022–2026 associado a queda menor | aberta | | | |
| A8 | Peso dos municípios pequenos na perda nacional de votos (contribuição) | **testada** | ver [A8](#a8) | **Sustentada.** AMCs < 20 mil eleitores: 21,6% do eleitorado, 28,9% da perda (1,34×); mas 71% da perda veio das maiores | `04_decomposicao.ipynb` |
| B1 | Transferências 1T→2T de 2026 favorecem Flávio, ao contrário de 2022 | aberta | | | |
| B2 | Variação da abstenção entre turnos e a quem beneficiou | aberta | | | |
| B3 | Transferências heterogêneas por região/perfil | aberta | | | |
| B4 | Previsão do 2T por município, congelada antes de 25/10/2026 | registrada | ver [B4](#b4) | | `03_previsao_2t.ipynb` |
| C1 | Clivagem do lulismo (renda, Nordeste, escolaridade, religião) ao longo de 2006–2026 | **testada** | ver [C](#série-histórica-c1-c2-c4-c5) | **(a), (b), (c) sustentadas.** Renda sempre negativa; efeito evangélico surge em 2018 | `06_serie.ipynb` |
| C2 | Nacionalização vs. regionalização do voto do PT (decomposição de variância) | **testada** | ver [C](#série-histórica-c1-c2-c4-c5) | **Não se sustenta.** Entre UFs caiu (70% → 62%); entre regiões imediatas da UF subiu (15% → 25%) | `06_serie.ipynb` |
| C3 | Tipologia de trajetórias municipais 2006–2026 | exploratória | ver [C](#série-histórica-c1-c2-c4-c5) | 4 tipos: redutos formados até 2018, subida e volta, afastamento gradual, antipetistas convergindo | `06_serie.ipynb` |
| C4 | Uniformidade da variação entre pleitos | **testada** | ver [C](#série-histórica-c1-c2-c4-c5) | **Sustentada.** dp 0,14 em 2022→2026 contra 0,40–0,49 antes | `06_serie.ipynb` |
| C5 | O gradiente de tamanho da A1 se repete nas transições anteriores | **testada** | ver [C](#série-histórica-c1-c2-c4-c5) | **Não se sustenta: inverteu.** Negativo em 2006→18 (até −0,133), positivo desde 2018→22 | `06_serie.ipynb` |
| D1 | Queda de 2026 concentrada nas periferias evangélicas das capitais | aberta | | | |
| E0 | Diagnóstico da virada de 2018 (regiões, 2º turno, acumulado, estados de origem, comparecimento, estabilidade do mapa) | exploratória | — | Nacional, presente no 2º turno, mudança de voto; **não é inversão completa** (desde 2014: −0,133 → −0,026); mapa congelado desde 2018 | `07_virada_2018.ipynb` |
| E1 | Máquinas locais: emendas por habitante e prefeitos de direita explicam o afastamento dos pequenos depois de 2018 | registrada | ver [E](#série-e-mecanismos-da-virada-de-2018) | | |
| E2 | Igrejas: presença evangélica (Censo 2010, CNPJ, candidatos religiosos) prevê o afastamento do PT em 2014→2018, e não antes | **testada** (E2a, E2b, E2c) | ver [E](#série-e-mecanismos-da-virada-de-2018) | **E2a, E2b e E2c se sustentam**, com Holm garantido. % evangélica 2010: −0,091, salto −0,098. Igrejas no CNPJ: −0,038, salto −0,038 (IC −0,054 a −0,021). Candidatos religiosos: −0,027, salto −0,027. Placebos nulos | `08_mecanismos.ipynb` |
| E3 | Internet móvel: chegada do 4G antes de 2018 prevê o afastamento do PT em 2014→2018 | registrada (condicional aos dados) | ver [E](#série-e-mecanismos-da-virada-de-2018) | | |
| E4 | Recessão e Lava Jato: perda de emprego formal e exposição a petróleo, naval e obras preveem o afastamento em 2014→2018 | **testada** | ver [E](#série-e-mecanismos-da-virada-de-2018) | **Não se sustenta.** E4a: −0,003 (IC −0,010 a +0,005), sinal contrário ao previsto. E4b: −0,002 (IC −0,009 a +0,005) | `08_mecanismos.ipynb` |
| E5 | Segurança: aumento dos homicídios prevê o afastamento em 2014→2018 | **testada**; aposta do autor: não se sustenta | ver [E](#série-e-mecanismos-da-virada-de-2018) | **Não se sustenta**, como apostado: +0,006 (IC −0,002 a +0,013), sinal contrário ao previsto | `08_mecanismos.ipynb` |
| E7 | Transformação do trabalho (pejotização, uberização): MEIs e trabalho por conta própria preveem o afastamento do PT a partir de 2014→2018 | **testada** | ver [E](#série-e-mecanismos-da-virada-de-2018) | **E7a não se sustenta** (−0,008, IC −0,024 a +0,007). **E7b: clivagem antiga, não choque de 2018** (−0,016 em 14→18, mas já −0,013 em 10→14; salto −0,004, IC −0,022 a +0,015; −0,030 em 18→22) | `08_mecanismos.ipynb` |
| E6 | Síntese: quanto do gradiente de tamanho de 2014→2018 e 2018→2022 cada mecanismo absorve | registrada (descritiva) | ver [E](#série-e-mecanismos-da-virada-de-2018) | | |
| E0b | Passageiro ou persistente: quanto do efeito de 2014→2018 de cada mecanismo ainda está lá em 2022 e 2026 | **testada** | ver [E0b](#e0b--choque-passageiro-ou-realinhamento) | **E2a, E2b e E2c persistentes**: retêm 112%, 113% e 103% em 2022 e 89%, 93% e 81% em 2026 (tamanho: 43% e 19%) | `08_mecanismos.ipynb` |
| E2d | A pegada religiosa de 2018 vem das organizações aliadas ao PT em 2014 (troca de lado), não da política religiosa em geral | **testada** | ver [E2d](#e2d--a-troca-de-lado-das-organizações-religiosas) | **Não se sustenta; sinal contrário.** Por pp: coligação −0,005 (IC −0,012 a +0,002), demais −0,015 (IC −0,023 a −0,006); diferença +0,010 (IC −0,001 a +0,021) | `08_mecanismos.ipynb` |
| E3b | Internet móvel depois de 2018 (acessos por município) prevê o afastamento dos pequenos em 2018→2022 e 2022→2026 | registrada (condicional aos dados) | ver [E3b e E3c](#e3b-e-e3c--duas-medidas-novas-para-o-ambiente-digital) | | |
| E3c | Celular e internet nos domicílios (Censo 2010) preveem o afastamento do PT em 2014→2018 | registrada (condicional aos dados) | ver [E3b e E3c](#e3b-e-e3c--duas-medidas-novas-para-o-ambiente-digital) | | |
| G1 | Aritmética do 2º turno de 2026: que combinações de transferência, comparecimento e conversão fecham a diferença | registrada (descritiva) | ver [G](#série-g-o-caminho-do-2º-turno-de-2026) | | `09_segundo_turno.ipynb` |
| G2 | Transferências do 1º para o 2º turno de 2022, por seção (inferência ecológica), e a faixa que elas dão para 2026 | registrada (descritiva; conferida pela B1) | ver [G](#série-g-o-caminho-do-2º-turno-de-2026) | | `09_segundo_turno.ipynb` |
| G3 | Reserva de comparecimento: abstencionistas e votantes perdidos onde Lula lidera, por município e local de votação | registrada (descritiva; conferida pela B2) | ver [G](#série-g-o-caminho-do-2º-turno-de-2026) | | `09_segundo_turno.ipynb` |
| G4 | Ex-eleitores: votos de Lula no 2º turno de 2022 que faltaram no 1º turno de 2026, por lugar | registrada (descritiva) | ver [G](#série-g-o-caminho-do-2º-turno-de-2026) | | `09_segundo_turno.ipynb` |
| G5 | Que tipo de lugar andou para o PT entre os turnos, de 2006 a 2022 | exploratória | ver [G](#série-g-o-caminho-do-2º-turno-de-2026) | | `09_segundo_turno.ipynb` |
| G6 | Pesquisas do 2º turno de 2026, com o erro do 1º turno descontado, e os cruzamentos por voto no 1º turno | exploratória | ver [G](#série-g-o-caminho-do-2º-turno-de-2026) | | `09_segundo_turno.ipynb` |
| G7 | O que está documentado sobre mobilização no dia da eleição e sobre o 2º turno de 2006 | documental | ver [G](#série-g-o-caminho-do-2º-turno-de-2026) | | `linha_do_tempo.csv` |

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

**Resultado da série (2026-10-09, `06_serie.ipynb`):**

- **C1:** renda padronizada −0,49 (2006), −0,35, −0,53, −0,62, −0,57 (2022), −0,62 (2026):
  (a) e (b) se sustentam, (b) por pouco. % evangélica +0,01 (2006) → −0,15 (2018) → −0,17
  (2022) → −0,13 (2026): (c) se sustenta. Exploratório: % urbana negativa de 2010 a 2018,
  positiva em 2022–2026.
- **C2:** fração entre UFs 69,8% (2006) → 61,8% (2022); entre regiões imediatas da UF
  14,9% → 25,1%. Não se sustenta como formulada: a diferença cresceu dentro dos estados.
- **C4:** desvio-padrão do Δ logit 0,40 / 0,49 / 0,48 / 0,43 nas transições anteriores e
  **0,14** em 2022→2026; correlação 0,987 (a maior). Sustenta-se.
- **C5:** efeito do tamanho −0,062, −0,046, −0,133, **+0,036**, **+0,025**. Positivo só em 2
  das 4 transições anteriores: não se sustenta. O gradiente inverteu por volta de 2018.

### Série E: mecanismos da virada de 2018

**Registrada em 2026-10-09, depois do diagnóstico exploratório E0 (`07_virada_2018.ipynb`) e
antes de baixar qualquer dado novo.** O E0 mostrou dois fenômenos: **(a)** o choque contra
o PT em 2014→2018, maior nas cidades grandes, que só voltou em parte; **(b)** desde 2018, o
afastamento dos municípios pequenos, que continua em 2026. A virada é nacional, então não
basta achar uma associação: cada mecanismo precisa mostrar uma **pegada no tempo**, ou seja,
aparecer na transição certa e **não** nas anteriores.

**Limite:** dados eleitorais por município não identificam interferência externa nem quem
financia um canal. Os testes dizem se a geografia da virada bate com a pegada de cada canal.

**Base comum (event study por transição):**

- **Unidade:** AMC (5.562), 1º turno. Transições: 2006→10, 2010→14, 2014→18, 2018→22,
  2022→26.
- **Desfecho:** Δ logit(`pt_2p`) em cada transição.
- **Modelo por transição:** Δ logit ~ X + log(aptos no pleito inicial) + logit(`pt_2p`
  inicial) + controles estruturais | região imediata, erros agrupados por região imediata,
  sem pesos. X é **padronizada** (z entre AMCs), para comparar mecanismos.
- **Controles estruturais** (Censo 2022, como na A1): log(renda mediana), alfabetização,
  % urbana, idade mediana, % preta ou parda. Robustez: sem controles; com pesos pelo
  eleitorado.
- **Teste da pegada:** painel empilhado das transições, X × transição, efeitos fixos de
  região imediata × transição, erros agrupados por região imediata. A diferença entre o
  coeficiente da transição-alvo e o da transição anterior é o teste de "salto".
- **Critério padrão (mecanismos do fenômeno a, alvo 2014→18):** sustenta-se se (i) β(14→18)
  tiver o sinal previsto com IC 95% excluindo zero **e** (ii) β(14→18) − β(10→14) tiver o
  mesmo sinal com IC 95% excluindo zero. Se (i) passar e (ii) não, o veredito é **"clivagem
  antiga, não choque de 2018"**.
- **Comparações múltiplas:** correção de Holm sobre os testes principais (marcados ★), em
  conjunto, com α = 0,05.
- Os coeficientes de 18→22 e 22→26 são sempre reportados (fenômeno b), sem critério,
  exceto na E1.

**E1 · Máquinas locais (alvo: fenômeno b, 18→22 e 22→26).**

- ★ **E1a:** X = valor pago de emendas parlamentares com município identificado como local
  do gasto, por habitante, nos quatro anos anteriores a cada eleição (Portal da
  Transparência, emendas individuais, de bancada, de relator e transferências especiais,
  onde houver município). Previsão: β < 0 em 18→22 **e** em 22→26 (mais emendas, mais
  afastamento do PT), e β(18→22) − β(14→18) < 0. Transições sem dado de emendas ficam de
  fora, e isso é registrado.
- ★ **E1b (RDD):** eleições para prefeito de 2016 e 2020 decididas por pouco entre um
  candidato da direita e um que não é da direita. Unidade: município. Desfecho: Δ logit
  (`pt_2p`) na transição presidencial seguinte (2016 → 14→18; 2020 → 18→22). `rdrobust`,
  banda ótima (MSE), IC robusto com correção de viés. Previsão: prefeito da direita → β < 0;
  o teste principal é o de **2020** (IC abaixo de zero). Mesmo desenho da A5 (2024 → 22→26).
- **Direita** = PSL, PL (ex-PR), PP, Republicanos (ex-PRB), DEM, União Brasil, PSC, PTB,
  Patriota (ex-PEN), PRTB, Novo. MDB e PSD ficam no grupo de comparação; robustez com eles
  na direita. A lista vale para todos os anos, mesmo que alguns desses partidos tenham
  apoiado o PT antes de 2016.
- Exploratório: E1a separada pelo bloco do autor da emenda.

**E2 · Igrejas (alvo: fenômeno a, 14→18).** Previsão: β < 0 (mais presença evangélica, mais
afastamento do PT), com o critério padrão.

- ★ **E2a:** X = % evangélica no Censo 2010 (anterior a 2014). Sugerida pela C1, que mostrou
  o efeito evangélico surgindo em 2018 no nível; aqui o teste é na variação e com o placebo.
- ★ **E2b:** X = igrejas evangélicas ativas por 10 mil habitantes em 2014 (estoque) e
  aberturas líquidas 2014→2017 por 10 mil habitantes (dois testes, só a primeira é ★). Fonte:
  CNPJ da Receita, CNAE 9491-0/00. "Ativa na data" = início antes da data e sem baixa,
  nulidade ou inaptidão anterior a ela. Evangélica = razão social bate com a lista de termos
  em `data/reference/denominacoes.csv`, commitada **antes** de cruzar com o voto.
  **Validação prévia:** a correlação entre igrejas evangélicas por habitante e a %
  evangélica do Censo (2010 com o estoque de 2010; 2022 com o de 2022) precisa ser ≥ 0,3;
  abaixo disso, a medida é declarada inválida e E2b não é testada.
- ★ **E2c:** X = % dos válidos para deputado federal em 2014 dados a candidatos religiosos.
  Religioso = ocupação declarada "sacerdote ou membro de ordem ou seita religiosa" **ou**
  nome de urna com título evangélico (Pastor, Pastora, Pr., Bispo, Bispa, Apóstolo,
  Apóstola, Missionário, Missionária, Presbítero). "Padre" e "Frei" ficam de fora. A mesma
  medida de 2006 e 2010 entra nas transições anteriores (exposição variável no tempo).
- **Lagoinha (exploratório, sem teste):** cronologia e mapa das unidades pela razão social
  no CNPJ; comparação descritiva de municípios que receberam unidade antes e depois de cada
  eleição. Sem teste, porque a igreja escolhe onde abrir.

**E3 · Internet móvel (alvo: fenômeno a, 14→18).** ★ X = anos com 4G no município até
outubro de 2018 (0 a 5), pelos dados da Anatel. Previsão: β < 0, com o critério padrão.
**Condicional aos dados:** sem série municipal do 4G anterior a 2018, a medida passa a ser a
variação de acessos de banda larga fixa por 100 habitantes de 2014 a 2017 (Anatel); sem
nenhuma das duas, E3 é registrada como **não testável**. A medida usada é anotada antes de
cruzar com o voto.

**Anotação (2026-10-09, antes de cruzar com o voto):** sem série municipal do 4G anterior a 2018 nos dados abertos da Anatel (detalhes em `decisoes.md`, D7), a E3 usa a medida alternativa: variação dos acessos de banda larga fixa por 100 habitantes entre o ano da eleição anterior e o ano anterior à eleição (2014→2017 para 14→18; 2010→2013 no placebo; 2007→2009 em 06→10, porque a série começa em 2007). É um indicador fraco do ambiente digital (não mede o celular nem o WhatsApp), e o resultado será lido assim.

**E4 · Recessão e Lava Jato (alvo: fenômeno a, 14→18).**

- ★ **E4a:** X = variação do log do emprego formal entre o ano da eleição anterior e o ano
  anterior à eleição (2014→2017 para a transição 14→18; equivalentes nas demais). Fonte: RAIS;
  se a RAIS municipal não estiver acessível, o pessoal assalariado do Cempre (IBGE), com a
  fonte anotada. Previsão: β > 0 (mais perda de emprego, mais afastamento do PT), com o
  critério padrão.
- ★ **E4b:** X = parcela do emprego formal de 2013 em extração de petróleo e gás e apoio
  (CNAE 06 e 09.1), derivados de petróleo (19), construção de embarcações (30.1) e obras de
  infraestrutura (42). Previsão: β < 0, com o critério padrão.

**E5 · Segurança (alvo: fenômeno a, 14→18).** ★ X = variação da taxa de homicídios por 100
mil habitantes entre os triênios anteriores a cada par de eleições (2011–13 → 2015–17 para
14→18). Homicídio = agressões (CID-10 X85–Y09) + intervenções legais (Y35–Y36), por
município de residência (SIM/DATASUS ou Atlas da Violência/Ipea). Previsão: β < 0, com o
critério padrão.

**E7 · Transformação do trabalho (registrada em 2026-10-09, a pedido, antes de abrir os dados
de MEI e de ocupação).** A ideia: a expansão do trabalho por conta própria (MEI desde 2009,
aplicativos de transporte e entrega a partir de 2014, reforma trabalhista de 2017) enfraquece
o vínculo com a identidade de trabalhador assalariado e com o PT, e aproxima do discurso
do "empreendedor". Alvo: fenômeno a (14→18), com os coeficientes de 18→22 e 22→26 sempre
reportados, porque a transformação continua depois de 2018.

- ★ **E7a · pejotização:** X = aberturas líquidas de MEI por 100 habitantes entre o ano da
  eleição anterior e o ano anterior à eleição (2014→2017 para 14→18; 2010→2013 para 10→14,
  que é o placebo; 2018→2021 e 2022→2025 depois). Fonte: CNPJ da Receita (tabela do Simples,
  com as datas de opção e de exclusão do MEI, ligada ao município do estabelecimento matriz),
  a mesma base da E2b. A transição 06→10 fica de fora (o MEI começou em julho de 2009).
  Previsão: β < 0, com o critério padrão.
- ★ **E7b · trabalho por conta própria:** X = % dos ocupados que trabalham por conta própria
  no Censo 2010 (anterior a 2014). Uma característica fixa cujo efeito passa a existir em
  2018 indicaria que o sentido político dessa posição mudou. Previsão: β < 0, com o critério
  padrão.
- **Uberização (exploratório, sem teste):** se houver uma lista confiável das datas de chegada
  da Uber e da 99 por município, comparação descritiva entre municípios com e sem aplicativo
  antes de 2018. Sem teste, porque as empresas escolhem onde entrar (cidades grandes e ricas
  primeiro) e o MEI de motorista de aplicativo só passou a existir depois.
- **Relação com a E4:** a E4a mede a perda de emprego formal; a E7 mede a troca de forma de
  trabalho. Na E6 as duas entram juntas, para separar o choque de emprego da mudança de
  forma.

**E6 · Síntese (descritiva, sem critério).** Nas transições 14→18 e 18→22, o modelo da C5
(tamanho + nível inicial | região imediata) mais cada X (E1–E5 e E7), uma de cada vez e depois todas
juntas. Reporta quanto o coeficiente do tamanho (−0,133 e +0,036) encolhe com cada uma,
como o M0→M3 da A1.

**Resultado E2a e E2c (2026-10-09, `08_mecanismos.ipynb`):**

| Teste | 2006→10 | 2010→14 | **2014→18** | 2018→22 | 2022→26 | Salto (IC 95%) | p (IU) |
|---|---|---|---|---|---|---|---|
| E2a · % evangélica 2010 | −0,006 | +0,007 | **−0,091** | −0,036 | +0,012 | −0,098 (−0,122 a −0,075) | < 10⁻¹⁴ |
| E2c · candidatos religiosos | +0,001 | −0,000 | **−0,027** | −0,006 | +0,000 | −0,027 (−0,044 a −0,010) | 0,002 |

- **Veredito: E2a e E2c se sustentam.** Placebos nulos e salto em 2014→2018 nas duas.
- **Holm:** o p de cada teste é o maior entre o do efeito em 2014→2018 e o do salto (teste de
  interseção-união: as duas condições precisam valer). Com 11 testes ★, p ≤ 0,05/11 ≈ 0,0045
  garante a rejeição em Holm quaisquer que sejam os outros, então os dois vereditos já são
  definitivos.
- **Robustez:** sem controles (−0,107; −0,034) e com pesos (−0,188; −0,039), mesmos sinais;
  placebos pequenos.
- **Exploratório:** as duas medidas quase não se correlacionam (0,18) e mantêm o efeito
  juntas (−0,090 e −0,019): a organização política das igrejas acrescenta algo à composição
  religiosa.
- **Limite:** pegada consistente com o canal "igreja", não prova causal. Não separa
  mobilização organizada pelas igrejas da pauta de Bolsonaro ou de campanhas digitais
  dirigidas a evangélicos (E3 e E6 ajudam), nem identifica quem organizou ou financiou.

### Registro de 2026-10-10: E0b, E2d, E3b, E3c, módulo RDD e a aposta da E5

**Registrado antes de cruzar qualquer medida nova com o voto.** As propostas vêm do ensaio e
do plano de ação sobre a virada de 2018 (branch `heliton/report1`), aprovadas em 10/10. Até
aqui, das medidas novas, só a distribuição dos homicídios por região foi olhada (sem o voto).

**Duas famílias de testes.** A família 1 é a dos 11 testes ★ já registrados (E1a, E1b, E2a,
E2b, E2c, E3, E4a, E4b, E5, E7a, E7b), com Holm a α = 0,05 sobre os 11. Os testes novos
formam a **família 2** (A5, E2d, E3b, E3c), com Holm a α = 0,05 sobre os 4. A E0b qualifica
os mecanismos e fica fora das duas.

**Holm com testes pendentes.** Enquanto faltarem testes numa família, o veredito de cada um
segue a regra de Holm nos dois extremos possíveis. É **rejeição garantida** se o teste for
rejeitado mesmo com todos os pendentes no fim da ordem (p = 1). É **não rejeição garantida**
se ele não for rejeitado nem com todos os pendentes no começo (p = 0). Fora desses casos, o
veredito fica **pendente**.

**Aposta do autor na E5 (prior; não muda o critério).** A E5 não se sustenta. A razão dada:
a alta dos homicídios de 2011–13 para 2015–17 se concentrou no Norte e no Nordeste, onde o
PT resistiu em 2018. Ressalva registrada junto: um nulo rejeita a exposição **local** à
violência, não a segurança como tema nacional de campanha, que o painel não vê.

#### E0b · choque passageiro ou realinhamento

- **Pergunta:** quanto do efeito de 2014→2018 de cada mecanismo ainda está lá depois. Separa
  o efeito de contexto e de candidato de 2018 (Lula impedido, Haddad, campo fragmentado) da
  mudança estrutural.
- **Modelo:** a base comum da série E com o desfecho **acumulado desde 2014** (Δ logit de
  2014→2018, 2014→2022 e 2014→2026), o nível e o tamanho de 2014 e a mesma X da transição
  2014→2018 (para as medidas que variam no tempo, a janela de 2014→2018).
- **Retenção:** R22 = β(14→22) / β(14→18) e R26 = β(14→26) / β(14→18).
- **Teste:** painel empilhado dos horizontes 2014→2018 e 2014→2022 (tudo interagido com o
  horizonte, efeitos fixos de região imediata × horizonte, erros agrupados por região
  imediata) e a combinação D = β(14→22) − 0,5 · β(14→18):
  - **persistente** se D tiver o sinal de β(14→18) com IC 95% excluindo zero (retém mais da
    metade);
  - **passageiro** se D tiver o sinal oposto com IC 95% excluindo zero (retém menos da
    metade);
  - **inconclusivo** se o IC de D contiver zero.
- **A quem se aplica:** aos mecanismos que se sustentam no critério padrão. R26 é descritiva.
- **Já conhecidos (descritivos, não confirmatórios):** tamanho (R22 ≈ 0,43, do E0), E2a
  (≈ 1,12) e E2c (≈ 1,03), calculados na exploração de 09/10 para o ensaio.

#### E2d · a troca de lado das organizações religiosas

- **Ideia:** a pegada da E2c está onde candidatos religiosos já tinham voto em 2014; a
  infraestrutura existia antes. A hipótese é que a pegada vem de organizações **aliadas ao
  PT em 2014** que passaram à oposição. O caso mais documentado é o PRB (Igreja Universal),
  que deixou a base em março de 2016.
- **Medida:** a mesma regra de religioso da E2c, separada pelo partido do candidato. X_al é
  a % dos válidos para deputado federal dados a candidatos religiosos de partidos da
  **coligação presidencial do PT** na eleição inicial da transição; X_out, a dos demais
  partidos. As medidas ficam em pp, sem padronizar, para que os dois coeficientes sejam
  comparáveis (efeito de 1 pp de voto para deputado).
- **Coligações** (cadastro de candidatos do TSE, candidatura presidencial do PT):
  - 2006: PT, PRB e PCdoB;
  - 2010: PT, PMDB, PR, PRB, PSB, PSC, PDT, PCdoB, PTC e PTN;
  - 2014: PT, PMDB, PSD, PP, PR, PROS, PDT, PCdoB e PRB;
  - 2018 e 2022: lidas do mesmo cadastro na execução.
- **Modelo por transição:** Δ logit ~ X_al + X_out + log(aptos) + nível inicial + controles
  estruturais | região imediata, erros agrupados por região imediata.
- **Critério (2014→2018):** sustenta-se se (i) β_al < 0 com IC 95% excluindo zero **e** (ii)
  β_al − β_out < 0 com IC 95% excluindo zero. O p do teste é o maior dos dois
  (interseção-união).
- **Evidência contra:** diferença ≥ 0 ou IC contendo zero. Nesse caso, a pegada é da
  política religiosa em geral, não da troca de lado.
- **Placebo reportado:** 2010→2014, com a coligação de 2010 (espera-se β_al e β_out ≈ 0).
- **Robustez:** controlar a fatia **total** dos partidos da coligação no voto para deputado
  (religiosos ou não). Se β_al sobrevive, a pegada é das organizações religiosas, não das
  máquinas desses partidos, que em boa parte também trocaram de lado em 2016.
- **Secundária, sem veredito:** o PRB sozinho contra os demais religiosos.

#### E3b e E3c · duas medidas novas para o ambiente digital

A E3 registrada (banda larga fixa) continua como está. As duas medidas novas separam os dois
fenômenos: TikTok, Kwai e vídeo curto não eram canais de massa em 2018, mas podem fazer parte
do afastamento dos pequenos depois.

- **E3c (fenômeno a, alvo 2014→2018):** X = % dos domicílios particulares permanentes com
  telefone celular no Censo 2010. Característica fixa, anterior a 2014, com o mesmo desenho e
  o mesmo critério padrão da E7b. Secundária, sem veredito: % com microcomputador com acesso
  à internet. Condicional aos dados: as tabelas do SIDRA serão anotadas antes de cruzar. Sem
  dado municipal, a E3c é **não testável**.
- **E3b (fenômeno b, alvo 2018→2022 e 2022→2026):** X = variação dos acessos de banda larga
  móvel por 100 habitantes no município entre 2019 e 2021 (para 2018→2022) e entre 2022 e
  2025 (para 2022→2026), pela Anatel, com a população do Censo 2022. Previsão: β < 0 nas duas
  transições.
  - **Critério:** β < 0 com IC 95% excluindo zero em 2018→2022 **e** em 2022→2026
    (interseção-união).
  - **Limite:** não há série municipal antes de 2019, então não há placebo nem teste de
    salto. É uma associação dentro da região imediata, mais fraca que o desenho padrão, e
    será lida assim.
  - **Robustez:** cobertura 4G por município em 2021.
  - **Condicional aos dados:** sem acessos móveis por município, a E3b é **não testável**.

#### Módulo RDD (A5 + E1b)

A A5 e a E1b passam a ser **um só desenho** aplicado a três ciclos municipais. A definição de
direita é a da E1b.

- **Ciclos e desfechos:** prefeito eleito em 2016 → Δ logit(`pt_2p`) em 2014→2018; em 2020 →
  2018→2022 (**E1b**, ★, família 1); em 2024 → 2022→2026 (**A5**, família 2).
- **Unidade:** município. Ficam de fora os municípios sem as duas eleições presidenciais da
  transição e os instalados no período.
- **Variável de corte:** margem, em % dos válidos, do candidato de direita sobre o candidato
  que não é de direita, na disputa decisiva (2º turno onde houver), só onde os dois
  primeiros colocados são um de cada grupo.
- **Estimação:** `rdrobust`, linear local, banda ótima (MSE), núcleo triangular, IC robusto
  com correção de viés; o nível inicial do PT como covariável (robustez sem ela).
- **Critério:** em cada teste principal (E1b em 2020, A5 em 2024), sustenta-se se o efeito de
  eleger o prefeito de direita for **negativo** com IC robusto abaixo de zero. O ciclo de 2016
  é reportado sem critério.
- **Validade:** densidade da variável de corte (`rddensity`); desfecho placebo (a transição
  presidencial **anterior** ao mandato não pode responder ao prefeito); balanço das
  covariáveis do Censo no corte.
- **Robustez:** MDB e PSD dentro da direita; metade e o dobro da banda.
- **Secundárias da A5, sem veredito:** PL contra não-PL e PT contra não-PT, em 2024.
- **Magnitude:** o efeito em pp perto de 50% e a fração dos municípios governados pela
  direita. Uma conta contrafactual nacional, com as hipóteses explícitas, fica para depois,
  como limite.

### Resultado E2b, E4, E5, E7, E2d e E0b (2026-10-10, `08_mecanismos.ipynb`)

Antes de rodar, duas correções nos dados de homicídios (código de município de 7 dígitos no
SIM de 2003–2005 e população zero de Nazária em 2004), que afetavam só o placebo de
2006→2010 da E5 (`decisoes.md`, D10). A validação prévia da E2b passou: correlação de 0,54
(2010) e 0,51 (2022) com a % evangélica do Censo.

| Teste | 2006→10 | 2010→14 | **2014→18** | 2018→22 | 2022→26 | Salto (IC 95%) | Veredito |
|---|---|---|---|---|---|---|---|
| E2b ★ · igrejas evangélicas (CNPJ, estoque) | −0,003 | −0,001 | **−0,038** | −0,017 | +0,005 | −0,038 (−0,054 a −0,021) | **sustenta-se** |
| E2b · aberturas (secundária) | −0,005 | +0,005 | −0,003 | −0,002 | +0,001 | −0,008 (−0,019 a +0,003) | — |
| E4a ★ · Δ log emprego formal (prev. β > 0) | +0,009 | +0,008 | −0,003 | −0,000 | +0,001 | −0,011 (−0,023 a +0,001) | não se sustenta |
| E4b ★ · emprego em petróleo, naval e obras | +0,002 | +0,001 | −0,002 | +0,000 | +0,000 | −0,004 (−0,013 a +0,006) | não se sustenta |
| E5 ★ · Δ taxa de homicídios | −0,005 | −0,001 | +0,006 | +0,001 | −0,004 | +0,007 (−0,004 a +0,017) | não se sustenta |
| E7a ★ · aberturas de MEI | — | +0,004 | −0,008 | +0,013 | −0,009 | −0,012 (−0,031 a +0,006) | não se sustenta |
| E7b ★ · % conta própria (Censo 2010) | +0,001 | −0,013 | **−0,016** | −0,030 | −0,010 | −0,004 (−0,022 a +0,015) | clivagem antiga, não choque de 2018 |

- **Holm, família 1 (8 de 11 calculados):** E2a, E2b e E2c têm rejeição garantida; os outros
  cinco, não rejeição garantida. Faltam E1a, E1b e E3.
- **E2d (família 2, 1 de 4):** não se sustenta (tabela acima, na linha da E2d). Robustez com a
  fatia total da coligação: igual (−0,005; diferença +0,010). Secundária, PRB contra os demais
  religiosos: −0,003 contra −0,014, diferença +0,011 (IC +0,000 a +0,021). A pegada não está na
  troca de lado da Universal; pesa mais nos religiosos de partidos fora da coligação de 2014
  (que inclui o PSC; separá-lo pede registro).
- **E0b:** E2a, E2b e E2c persistentes (D = −0,057, −0,024 e −0,014, todos com IC excluindo
  zero). Para E2a e E2c o resultado já era conhecido (exploração de 09/10); a E2b é a primeira
  confirmatória.
- **Exploratório:** com as três medidas religiosas juntas em 2014→2018, os templos (E2b) caem
  para −0,007 (IC −0,021 a +0,006), enquanto a composição (−0,086) e o voto em pastores
  (−0,018) mantêm o efeito. A E2b confirma a pegada por uma fonte independente, mas não é um
  canal próprio além da composição.
- **Limite:** os nulos de E4, E5 e E7a rejeitam a exposição **local**; recessão, Lava Jato e
  violência também agiram como fatos nacionais, que caem na variação média de cada transição.

### Série G: o caminho do 2º turno de 2026

**Registrado em 2026-10-10, antes de qualquer conta da série.** Até aqui, dos dados que ela
usa, só os totais nacionais por pleito e turno foram olhados: a diferença de 2,22 mi no 1º
turno de 2026 e os ganhos de cada lado entre os turnos de 2006 e de 2022. Plano completo em
[plano_segundo_turno.md](plano_segundo_turno.md).

**Para que serve.** Medir, antes de 25/10, quanto cada caminho pode render para Lula e onde
estão esses votos. A série é quase toda descritiva e não tem veredito. O que vale como teste
é a conferência depois de 25/10, quando a B1 e a B2 medirem o que de fato aconteceu. A B4
não muda: a previsão v2 continua em 24/10.

**Definições.**

- **D** = votos de Flávio − votos de Lula no 1º turno de 2026, com o exterior.
- **Grupos de origem k** do 1º turno:
  - eleitores de Lula, de Flávio e de cada eliminado;
  - brancos e nulos;
  - abstenção.
- **p_k^L e p_k^F:** as frações de cada grupo que votam em Lula e em Flávio no 2º turno.
- **Variação da margem entre os turnos:** ΔM = Σ_k N_k · (p_k^L − p_k^F). Lula vira se
  ΔM > D.
- **Três caminhos:**
  - transferência: eliminados e brancos/nulos;
  - comparecimento: abstencionistas do 1º turno que votam no 2º;
  - conversão: eleitores de Flávio que passam a Lula, e o inverso. Cada um vale 2 na margem.

#### G1 · aritmética

- **O que se calcula:** a identidade acima, no país e por UF. Para cada caminho, o tamanho
  do estoque N_k e a taxa líquida (p_k^L − p_k^F) que fecharia D sozinha.
- **Série histórica:** ganho de votos do PT e do adversário entre os turnos, e variação do
  comparecimento, de 2006 a 2022.
- **Na página:** uma calculadora que aplica a identidade às taxas escolhidas pelo leitor.

#### G2 · transferências de 2022, por seção

- **Unidade:** a seção. Ela é casada entre os turnos por UF, município, zona e seção; as
  sem par ficam de fora e são contadas.
- **Origens no 1º turno de 2022:**
  - Lula, Bolsonaro, Ciro, Tebet e os demais candidatos juntos;
  - brancos + nulos;
  - abstenção.
- **Destinos no 2º turno:** Lula, Bolsonaro, brancos + nulos e abstenção. As frações são
  sobre os aptos da seção (o cadastro é o mesmo nos dois turnos; a diferença é conferida).
- **Estimador:**
  - por UF, mínimos quadrados ponderados pelos aptos para a matriz B (origens × destinos),
    com B ≥ 0 e cada linha somando 1;
  - IC de 95% por bootstrap de municípios (200 réplicas);
  - o nacional é a média das UFs ponderada pelos votos de cada origem.
- **Validação:**
  - recuperar uma matriz conhecida em dados sintéticos;
  - informar a diferença entre os totais do 2º turno implicados por B e os oficiais;
  - a retenção dos finalistas (Lula→Lula, Bolsonaro→Bolsonaro) precisa passar de 0,9. Se
    não passar, o problema está no estimador, não no eleitor.
- **Robustez (exploratória):** estimar por UF × faixa de tamanho, porque a taxa constante
  dentro da UF é a principal fonte de viés.
- **Uso para 2026, que não é previsão:** a faixa de taxas plausíveis para Cury, Renan e
  Caiado vai das taxas dos eleitores de Tebet às dos demais candidatos (direita) de 2022,
  confrontada com os cruzamentos das pesquisas (G6).
- **Conferência depois de 25/10:** a B1, quando registrada, usa o mesmo estimador na
  transição de 2026. Anotar onde cada taxa caiu em relação à faixa da G2.
- **Expectativa do autor (prior, sem critério):** a maior parte do ganho de Bolsonaro entre os
  turnos de 2022 veio dos eleitores de Ciro, Tebet e dos demais, não da abstenção.

#### G3 · reserva de comparecimento

- **Reserva líquida por unidade u** (seção, local de votação, município, UF):
  R_u = A_u · (2p_u − 1).
  - A_u: abstenções no 1º turno de 2026.
  - p_u: Lula / (Lula + Flávio) no mesmo turno.
  - R_u é o saldo de votos se os abstencionistas votassem como os votantes do lugar.
- **Rendimento por ponto:** aptos_u · 0,01 · (2p_u − 1). São os votos líquidos de cada ponto
  de comparecimento a mais.
- **Votantes perdidos:** P_u = (t_u,2T-2022 − t_u,1T-2026) · aptos_u,2026, quando positivo
  (t é a taxa de comparecimento).
  - Por município pelo painel.
  - Por local de votação, casando os locais de 2022 e 2026 por município, zona e número do
    local, com o nome igual depois de normalizado. A taxa de casamento é informada.
- **Lição de 2022:** variação do comparecimento entre os turnos, por seção, contra p_u do
  1º turno, com efeito fixo de município e peso dos aptos. Junto, a linha "abstenção" da
  matriz da G2.
- **Ressalva:** (2p − 1) supõe que quem se absteve votaria como quem votou no mesmo lugar. Os
  abstencionistas têm outro perfil, e parte deles é cadastro inflado. A linha "abstenção"
  da G2 mostra quanto essa suposição errou em 2022.
- **Conferência depois de 25/10:** a B2 mede onde o comparecimento subiu no 2º turno de 2026 e
  a quem favoreceu.

#### G4 · ex-eleitores

- **Decomposição:** LMDI (`features/decomposicao.py`) dos votos de Lula do 2º turno de 2022
  para o 1º turno de 2026, por AMC, nos componentes eleitorado, comparecimento, válidos e
  fatia.
- **Alvo de persuasão:** a parcela "fatia" negativa, em votos. São lugares onde quem votou
  deixou de votar em Lula; no nível de pessoa é ecológico, já que troca de eleitores conta
  como fatia.
- **Tabelas:** por UF × faixa de tamanho (as faixas da A8), com a mesma conta do 1º turno de
  2022 ao 1º de 2026 (A8) para comparar.
- **Perfil (exploratório):** médias ponderadas das covariáveis nas AMCs que concentram 50% da
  fatia perdida, contra as demais.
- **Ressalva:** comparar o 2º turno de 2022 com o 1º de 2026 mistura a dinâmica entre turnos,
  e isso é dito junto do número.

#### G5 · quem se moveu entre os turnos (exploratória)

- **Modelo:** Δ logit(`pt_2p`) do 1º para o 2º turno, em cada eleição de 2006 a 2022, contra
  log(aptos), nível do 1º turno, % evangélica, renda, cobertura do Auxílio Brasil (só 2022) e
  efeito fixo de UF.
- **Estimação:** peso dos aptos e erros agrupados por região imediata.
- **Sem veredito:** serve para dizer que tipo de lugar se moveu no 2º turno.

#### G6 · pesquisas (exploratória)

- **Fonte:** pesquisas de 2º turno de 2026 desde 06/10, em votos válidos, em
  `pesquisas_2026.csv` com `turno=2`.
- **Correção:** a de `alvo_das_pesquisas` da B4 (λ × o viés de cada instituto no 1º turno),
  com a faixa de λ entre 0 e 1. É leitura do momento, não previsão.
- **Cruzamentos:** voto no 2º turno por voto no 1º, quando publicados, em
  `pesquisas_2t_cruzamentos.csv`.
- **Conferência:** ~20% das pesquisas conferidas na fonte, e todas as que entram nos
  cruzamentos.

#### G7 · documental

Itens em `linha_do_tempo.csv`, com o grau de evidência da série F (documentado, reportado,
alegado, refutado) e a fonte conferida:

- transporte gratuito no dia da eleição em 2022;
- operações da PRF no 2º turno de 2022;
- evidência experimental sobre mobilização porta a porta;
- a campanha do 2º turno de 2006.

#### Síntese

Uma tabela de alavancas. Cada linha traz o estoque, a faixa de taxas e de onde ela vem (G2,
G3 ou G6), o ganho líquido em votos, onde ele está e o que fazer. As recomendações levam selo
de inferência: os dados dizem onde e quanto, não qual mensagem.

**Premissa do plano e o que a derrubaria:** só transferência não fecha D. A premissa cai se,
com as taxas de 2022 (G2) ou com as dos cruzamentos (G6), o saldo líquido das transferências
for ≥ D.
