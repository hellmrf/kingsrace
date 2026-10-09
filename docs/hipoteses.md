# Registro de hipóteses

Registrar aqui **antes** de rodar o modelo confirmatório: a hipótese, o teste e o que
contaria como evidência contra. Depois, anotar o resultado e o notebook. Análises
exploratórias não precisam de registro, mas o que sair delas e virar afirmação precisa.

Status: `aberta` → `registrada` (teste definido) → `testada` (resultado anotado).
Detalhamento de cada hipótese em [plano.md](plano.md), seção 4.

| ID | Hipótese | Status | Teste / critério | Resultado | Notebook |
|---|---|---|---|---|---|
| A1 | Lula cai mais (Δ dois maiores, 2022→2026 1T) quanto menor o município, mesmo dentro da UF | registrada | ver [A1](#a1) | | `02_tamanho.ipynb` |
| A2 | Queda maior onde o agro pesa mais e onde a soja avançou | aberta | | | |
| A3 | Participação evangélica (nível 2022 e Δ 2010–2022) prevê a queda | aberta | | | |
| A4 | Coeficiente da cobertura do Bolsa Família muda de sinal ou cresce entre 2022 e 2026 | aberta | | | |
| A5 | Prefeito do PL/centrão eleito em 2024 aumenta o afastamento de Lula (RDD) | aberta | | | |
| A6 | Parte relevante da perda de Lula é desmobilização (abstenção), não conversão | aberta | | | |
| A7 | Saldo de empregos formais 2022–2026 associado a queda menor | aberta | | | |
| A8 | Peso dos municípios pequenos na perda nacional de votos (contribuição) | aberta | | | |
| B1 | Transferências 1T→2T de 2026 favorecem Flávio, ao contrário de 2022 | aberta | | | |
| B2 | Variação da abstenção entre turnos e a quem beneficiou | aberta | | | |
| B3 | Transferências heterogêneas por região/perfil | aberta | | | |
| B4 | Previsão do 2T por município, congelada antes de 25/10/2026 | aberta | | | |
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
