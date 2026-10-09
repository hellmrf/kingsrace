# Diário do projeto

Registro do que foi feito e do que se descobriu, do mais recente para o mais antigo.
Achados aqui são exploratórios até passarem pelo registro em [hipoteses.md](hipoteses.md).

---

## 2026-10-09 · a série histórica 2006–2026

[`notebooks/06_serie.ipynb`](../notebooks/06_serie.ipynb)

**Dados:** 2006, 2010, 2014 e 2018 incorporados; 11 turnos, 5.562 AMCs comparáveis, todos
os totais de PT e adversário batendo com os oficiais. No caminho: votos de candidato anulado
em 2006 (Rui Costa Pimenta), o código 97 ("anulado e apurado em separado"), nulos definidos
por resíduo (o sentido das colunas do TSE muda entre anos), voto em trânsito de 2010 numa
pseudo-UF e AMCs para os municípios de 2013 (detalhes em [decisoes.md](decisoes.md), D5).

**O achado principal: o gradiente de tamanho inverteu em 2018.** De 2006 a 2018, os
municípios **grandes** se afastaram mais do PT a cada eleição (o pico foi 2014→2018, o
desmoronamento urbano do PT). Desde 2018→2022 é o contrário: as cidades grandes voltaram e
os municípios pequenos é que se afastam. O padrão de 2022→2026 que motivou o projeto é a
continuação dessa virada, não uma regra antiga. A mesma virada aparece na clivagem: com o
resto fixo, ser urbano era desvantagem para o PT até 2018 e passou a ser vantagem.

**Outros resultados:**
- **A clivagem de renda é a constante da série:** municípios mais pobres votam mais no PT em
  todos os pleitos, com qualquer candidato. O **efeito evangélico nasceu em 2018**.
- **O voto ficou mais regional dentro dos estados**, não entre eles (o interior se separou dos
  centros urbanos da mesma UF).
- **2022→2026 foi a transição mais uniforme da série**: o país se moveu quase em bloco (é a
  única com o mesmo candidato do PT nos dois lados).
- **Quatro tipos de trajetória** (exploratório): redutos do PT formados até 2018 (Nordeste),
  subida e volta, afastamento gradual (mais no Sul) e antipetistas convergindo para o meio.

**Pergunta que fica:** o que mudou por volta de 2018? Candidatos (Haddad, Bolsonaro), o
antipetismo urbano pós-Lava Jato e a volta dele em 2022, ou uma reorganização do interior?

---

## 2026-10-09 · agro, religião e Bolsa Família (A2, A3, A4)

[`notebooks/05_composicao.ipynb`](../notebooks/05_composicao.ipynb)

As três pistas que apareceram nos controles da A1 foram testadas com **medidas novas**
(soja da PAM, Censo 2010, dados do MDS), mantendo as medidas antigas como controles.

- **Agro (A2) e religião (A3) não se confirmam.** Nem a expansão recente da soja nem o
  crescimento evangélico entre os Censos explicam a queda além do que já estava no modelo.
- **Bolsa Família (A4) se confirma, e com força.** Em 2022 (Auxílio Brasil, governo
  Bolsonaro), onde o programa alcançava mais famílias o PT já ia melhor; em 2026 (Bolsa
  Família, governo Lula), essa associação **praticamente dobrou**. E onde a cobertura é maior,
  o PT perdeu menos entre 2022 e 2026: o efeito de 1 desvio-padrão é maior que o do tamanho
  do município.
- **Dados novos e correções no caminho:** o "-" do IBGE é zero (não ausente); a agregação por
  AMC passou a somar contagens; um erro na PAM (Mariópolis/PR com soja maior que o território)
  foi anulado; e um efeito colateral dessa correção, que zerava a soja de Boa Esperança do
  Norte, foi pego antes de rodar os modelos.

---

## 2026-10-09 · para onde foram os votos de Lula (A6, A8)

[`notebooks/04_decomposicao.ipynb`](../notebooks/04_decomposicao.ipynb)

- **Não foi abstenção (A6 rejeitada).** Dos 3,4 milhões de votos que Lula perdeu, quase tudo
  é queda da fatia dele entre os válidos (−4,1 mi); o comparecimento ficou igual e o
  eleitorado cresceu (+0,9 mi), compensando parte. Com a ressalva ecológica: troca de
  eleitores dentro do mesmo município aparece como "fatia".
- **Os pequenos pesaram mais que o tamanho (A8 sustentada):** municípios com menos de 20 mil
  eleitores têm 22% do eleitorado e 29% da perda. Mas 71% dos votos perdidos vieram dos
  maiores.
- **Achado exploratório, o mais interessante do dia:** a queda tem naturezas diferentes por
  região. No **Nordeste e no Norte, Lula manteve os votos** e a fatia caiu porque o
  adversário cresceu (+1,6 mi no Nordeste, absorvendo eleitores novos e ex-eleitores de
  outros). No **Sudeste e no Sul, Lula perdeu votos** de fato (−1,8 e −1,0 mi). Candidata a
  hipótese própria.

---

## 2026-10-08 (madrugada) · previsão do 2º turno, versão 1

[`notebooks/03_previsao_2t.ipynb`](../notebooks/03_previsao_2t.ipynb) · especificação e
critérios de avaliação em [hipoteses.md](hipoteses.md#b4).

- **Congelada:** `data/reference/previsoes/previsao_2t_2026_v1.csv`, tag
  `previsao-2t-2026-v1`, sha256 `fc6e30ce87ba34913f22490038338e0adb45447487bd6719efbedbd132192d2d`.
- **Nível central: Lula 46,9%** entre os dois finalistas (faixa 45,8%–48,0%). Vem da única
  pesquisa de 2º turno até agora (Datafolha 6–8/10: Lula 48% dos válidos), corrigida pela
  metade do viés do instituto no 1º turno (+2,2 pp a favor de Lula).
- **Achado do backtest de 2022:** distribuir os votos dos eliminados por perfil de
  candidato (Tebet e Ciro → Lula) **piora** a previsão por município em relação a um
  deslocamento uniforme (1,16 contra 0,95 pp). O desvio de 2022 não segue onde os outros
  candidatos eram fortes; segue um padrão de **compressão** (os redutos andam para o centro).
  Por isso o central é o uniforme, e as alternativas (transferências, compressão) vão
  congeladas junto para o resultado decidir.
- **Bug pego antes de congelar:** o `join` do polars não preserva a ordem das linhas, e a
  variante de transferências recebia valores de outros municípios. Corrigido com teste de
  regressão; a previsão agora é determinística (mesmo hash a cada execução).
- **Próximo:** versão 2 em 24/10 com as pesquisas finais (`just previsao v2 2026-10-24`,
  depois de acrescentar as pesquisas em `data/reference/pesquisas_2026.csv`).

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
