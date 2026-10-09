# Diário do projeto

Registro do que foi feito e do que se descobriu, do mais recente para o mais antigo.
Achados aqui são exploratórios até passarem pelo registro em [hipoteses.md](hipoteses.md).

---

## 2026-10-08 (noite)

### A1 testada: o tamanho importa, mas metade era composição

[`notebooks/02_tamanho.ipynb`](../notebooks/02_tamanho.ipynb) roda a especificação
registrada em [hipoteses.md](hipoteses.md#a1).

- **A1 se sustenta.** Mesmo comparando municípios da mesma região imediata e com a mesma
  composição (renda, religião, idade, agro, escolaridade, cor ou raça, transferências e o
  voto do PT em 2022), os menores perderam mais. O coeficiente cai pela metade com os
  controles (0,049 → 0,024 em logit), mas fica longe de zero, e todas as checagens de
  robustez concordam.
- **Em pp:** entre 3 mil e 300 mil eleitores, ~2,5 pp a mais de queda na menor (5,0 pp sem
  controles).
- **O Nordeste não é diferente** (A1b): o "Nordeste plano" do panorama era composição.
- **Pistas exploratórias** (cada uma precisa de registro próprio antes de virar afirmação):
  com o resto fixo, o PT caiu **mais** onde era mais forte em 2022, onde a renda é maior e
  onde o agro pesa mais; caiu **menos** onde há mais renda de transferências/aposentadorias e,
  contra a intuição, onde há mais evangélicos (condicional ao voto de 2022).

### Incidente: repositório git corrompido por queda do WSL

Um commit ficou com objetos vazios. Reparado sem perda (o conteúdo estava nos arquivos de
trabalho); `core.fsync committed` ligado para evitar repetição.

---

## 2026-10-08

### Notebook 01 · Panorama — gráficos interativos

[`notebooks/01_panorama.ipynb`](../notebooks/01_panorama.ipynb) reorganizado com
explicações de "como ler" e "o que observar" em cada gráfico. Os gráficos são exibidos
como widgets (`JupyterChart`) em modo offline, sem depender de CDN, e cada um recebe só
os dados que usa.

### Primeiros achados (exploratórios)

- O PT perdeu **3,9 pp** entre os dois maiores no país (52,9% → 49,0%, 1º turno, sem
  exterior). O município **mediano** perdeu **6,0 pp**, e o PT subiu em apenas 50 dos
  5.569 municípios (AMC).
- A perda é maior quanto menor o município, **dentro de todas as regiões**. No Sul:
  −9,5 pp abaixo de 5 mil eleitores contra −2,0 pp acima de 500 mil. No Centro-Oeste:
  −8,4 contra −0,8.
- O Nordeste é a exceção parcial: perda quase constante (~−5 pp) até 50 mil eleitores.
- Na distribuição dos municípios, o pico dos redutos do PT desceu de ~80% para ~70%.

Ainda falta separar tamanho de composição (região, renda, agro, religião) e checar o
efeito de teto com o logit. Esse é o próximo passo (M1a).

### Bug corrigido: overflow nas contagens

As contagens eram Int32, e `100 * votos` estourava sem erro (Lula aparecia com 12,1% dos
válidos). Agora são Int64 desde a conversão.

### M0b concluído: dados de 2022 e 2026

- Painel por município e por AMC, conferido contra os totais oficiais do TSE (exatos).
- O CSV comunitário de correspondência TSE↔IBGE tinha 7 municípios com códigos trocados;
  a correspondência agora é própria (detalhes em [decisoes.md](decisoes.md), D4).
- 5.246 votos do nº 28 em 2026 foram anulados pelo TSE e não contam como válidos.
- Boa Esperança do Norte (MT), instalado em 2025, forma uma AMC com Sorriso e Nova Ubiratã.
