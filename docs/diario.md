# Diário do projeto

Registro do que foi feito e do que se descobriu, do mais recente para o mais antigo.
Achados aqui são exploratórios até passarem pelo registro em [hipoteses.md](hipoteses.md).

---

## 2026-10-10 · síntese para o grupo: "O que os votos mostram"

[`reports/conjuntura/`](../reports/conjuntura/) · página publicada como artifact privado

Uma página visual, sem jargão, para debater os achados com os colegas antes do 2º turno
(versão 1, para a militância e a direção; a versão acadêmica fica para depois de 25/10).
Cada afirmação leva um selo de evidência (dado testado, exploratório, documentado,
reportado, alegado), e os números vêm todos de `dados.js`, gerado por `just conjuntura` a
partir das métricas dos notebooks e do painel, com os totais conferidos contra os oficiais.

**Contas descritivas novas** (exploratórias, sem registro; feitas para a página):

- **A distribuição da variação municipal em cada transição** (pp, 1º turno): em 2022→2026, o
  PT caiu em 99,1% das AMCs, com desvio-padrão de 3,1 pp, contra 8,4 a 9,7 pp nas quatro
  transições anteriores. É a C4 em pontos percentuais.
- **Pesquisas da véspera do 1º turno:** 7 dos 11 institutos davam Lula à frente; o viés médio
  na fatia entre os dois foi de +1,6 pp a favor de Lula.
- **Bolsa Família no nível (A4) em pp:** por desvio-padrão de cobertura (7,6 famílias por 100
  habitantes), +1,1 pp para o PT em 2022 e +2,2 pp em 2026.

**Fontes novas:** `data/reference/linha_do_tempo.csv` (eventos de 2006 a 2026 com grau de
evidência e fonte conferida, o produto previsto na série F) e as séries de pesquisas de
2025–2026 (2º turno simulado Lula × Flávio e aprovação do governo), que alimentam um gráfico
**exploratório** de pesquisas com as ações dos EUA marcadas no tempo. O gráfico não testa
nada: serve para escolher o que testar.

**Para o grupo decidir** (votação na própria página): tarifas por município (Comex Stat),
pesquisas × eventos por segmento, segurança (PCC/CV), módulo RDD de prefeitos e emendas,
E3b, trilha documental e igrejas em 2026.

---

## 2026-10-10 · só a religião marca 2018; economia, violência e trabalho, não (série E)

[`notebooks/08_mecanismos.ipynb`](../notebooks/08_mecanismos.ipynb) · registro de 10/10 em
[hipoteses.md](hipoteses.md)

**Registrado antes dos dados:** E0b (passageiro ou persistente), E2d (a troca de lado das
organizações religiosas), E3b e E3c (duas medidas novas para o ambiente digital), a fusão de
A5 com E1b num só desenho de RDD e a aposta do autor de que a E5 cairia. Os testes novos
formam uma segunda família de Holm.

**Resultados:**

- **Igrejas no CNPJ (E2b) se sustentam:** nada antes de 2014, −0,038 em 2014→2018, salto
  significativo. Com a % evangélica no mesmo modelo, porém, os templos perdem o efeito
  (exploratório): confirmam a pegada religiosa por outra fonte, mas não são um canal à parte.
- **Economia, Lava Jato e violência não deixaram pegada local (E4a, E4b, E5).** Onde se perdeu
  mais emprego formal, onde petróleo, estaleiros e obras pesavam mais e onde os homicídios
  subiram mais, o PT não perdeu mais em 2018. A aposta na E5 se confirmou.
- **Trabalho:** o MEI (E7a) não tem efeito com os controles. A conta própria (E7b) tem, mas já
  aparecia em 2010→2014 e é maior em 2018→2022: clivagem que se aprofunda, não choque de 2018.
- **A troca de lado da Universal não explica a pegada religiosa (E2d).** O efeito por ponto de
  voto em pastores é menor nos partidos da coligação de Dilma (−0,005) que nos demais
  (−0,015); onde o pastor era do PRB, o PT perdeu menos. A pegada está na política religiosa
  em geral, e mais fora da base de 2014 (onde está o PSC de Bolsonaro e do Pastor Everaldo).
- **Persistência (E0b):** as três medidas religiosas retêm 81% a 93% do efeito em 2026; o
  choque urbano, 19%.

**Correções no caminho:** o SIM de 2003–2005 grava o município com 7 dígitos, e esses anos
sumiam na junção; a população zero de Nazária (PI) em 2004 gerava 0/0, e o NaN derrubava o
kernel sem mensagem. As duas afetavam só o placebo de 2006→2010 da E5 e foram corrigidas antes
dos resultados (D10). Os intermediários do TSE foram reconvertidos; nenhum dado processado
mudou.

**Próximo:** emendas e prefeitos (E1a, módulo RDD com A5 e E1b), Anatel e Censo 2010 (E3, E3b,
E3c). Candidatos a registro: o PSC na E2d e a conta própria no afastamento dos pequenos.

---

## 2026-10-09 · igrejas: a pegada aparece exatamente em 2018 (E2a, E2c)

[`notebooks/08_mecanismos.ipynb`](../notebooks/08_mecanismos.ipynb)

**Dados novos:** candidatos e votos para deputado federal de 2006 a 2022 (TSE). A medida E2c
é a fatia dos válidos para deputado que foi para candidatos religiosos: ocupação religiosa
declarada ou título evangélico no nome de urna (Pastor, Bispo, Missionário…). Os votos
nominais válidos batem com o detalhe do TSE em todas as UFs nos cinco anos. Particularidades
em [decisoes.md](decisoes.md) (D6).

**Ferramenta nova:** `models/event_study.py`, o teste comum da série E. Calcula o efeito da
medida em cada transição e o "salto" em relação à transição anterior, num painel empilhado.

**Resultados (os dois vereditos são definitivos, mesmo antes da correção de Holm completa):**

- **% evangélica no Censo 2010 (E2a):** nenhum efeito em 2006→2010 e 2010→2014; em 2014→2018,
  −0,091 por desvio-padrão (~2,3 pp numa AMC dividida ao meio). O efeito segue menor em
  2018→2022 e se inverte levemente em 2022→2026.
- **Voto em candidatos religiosos (E2c):** também nulo antes e −0,027 em 2014→2018, e quase
  some depois. A pegada da organização política das igrejas está concentrada em 2018.
- **Composição e organização são coisas diferentes:** as duas medidas quase não se
  correlacionam (0,18) e mantêm o efeito quando entram juntas (exploratório).

**O que isso não diz:** não é prova causal, e não separa a mobilização organizada pelas
igrejas da pauta de costumes de Bolsonaro ou de campanhas no WhatsApp dirigidas a
evangélicos. Também não diz quem organizou ou financiou. Próximo: o CNPJ (igrejas por ano,
Lagoinha e MEIs da E7).

---

## 2026-10-09 · o que exatamente virou em 2018 (série E, etapa 0)

[`notebooks/07_virada_2018.ipynb`](../notebooks/07_virada_2018.ipynb) (exploratório)

Antes de procurar causas para a virada, um diagnóstico do que mudou, só com os dados que já
tínhamos. Abre a **série E** (mecanismos da virada), cujo roteiro está em
[hipoteses.md](hipoteses.md).

- **A virada é nacional.** O efeito do tamanho muda de sinal nas cinco regiões.
- **Sobrevive no 2º turno**, mais fraca (2018→2022: +0,013 contra +0,036 no 1º). Parte do
  gradiente do 1º turno vinha da fragmentação: de 2010 a 2018 os outros candidatos tinham
  27–33% dos válidos nas cidades grandes; em 2022, 6–12%.
- **Não é efeito "filhos da terra":** sem SP, MG e RJ, os coeficientes quase não mudam.
- **É mudança de voto, não comparecimento:** o gradiente está todo na fatia do PT.
- **Não é uma inversão completa.** Desde 2014, o efeito acumulado do tamanho é −0,133 em
  2018, −0,057 em 2022 e −0,026 em 2026: as cidades grandes voltaram ao PT só em parte. São
  dois fenômenos: o choque urbano de 2014→2018 e, desde 2018, o afastamento dos pequenos.
- **Bolsonaro herdou o mapa do PSDB** (correlação do adversário Aécio→Bolsonaro 0,874, como
  nas trocas anteriores), e **o mapa congelou** a partir de 2018 (0,975 e 0,986). No 2º turno
  o congelamento começa antes: o molde é o Dilma × Aécio de 2014.

**Consequência para o desenho:** uma quebra igual no país todo é o que qualquer causa nacional
produz, então a uniformidade não aponta para nenhuma. As hipóteses E1–E5 e E7 (máquinas
locais e emendas, igrejas, internet móvel, recessão e Lava Jato, violência, transformação do
trabalho: MEI e conta própria) vão ser testadas pela **pegada geográfica e temporal** de cada
canal, com placebo nas transições anteriores a 2018.

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
