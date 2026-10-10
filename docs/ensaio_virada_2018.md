# A virada de 2018: o que os dados mostram, o que a história documenta e o que ainda é suspeita

*Ensaio de trabalho, 2026-10-09. Acompanha o [plano de ação](plano_virada_2018.md). Os números
vêm dos notebooks [06](../notebooks/06_serie.ipynb), [07](../notebooks/07_virada_2018.ipynb) e
[08](../notebooks/08_mecanismos.ipynb) e de duas contas exploratórias feitas para este texto
(seções 2.2 e 2.5), que ainda não passaram pelo registro de hipóteses.*

---

## Por que este texto

O projeto começou com uma pergunta modesta: por que Lula perdeu mais votos nos municípios
pequenos entre 2022 e 2026? Quando a série foi estendida até 2006, esse padrão se revelou a
ponta de algo maior. De 2006 a 2018, eram as **cidades grandes** que se afastavam do PT a cada
eleição. Em 2018 o sinal se inverte. No mesmo ponto nasce um efeito evangélico que antes não
existia, e o mapa eleitoral, que mudava bastante de uma eleição para outra, congela.

A coincidência convida a uma narrativa. Um processo nacional teria começado em Junho de 2013,
se aprofundado com o impeachment e a prisão de Lula e culminado na eleição de Bolsonaro,
talvez induzido de fora, num contexto de disputa entre os Estados Unidos e os BRICS. A
narrativa é coerente e tem apelo, e por isso mesmo pede cuidado. Este texto separa três tipos
de afirmação:

- **o que os nossos dados mostram**, com o número e o notebook;
- **o que a história documenta**, com data e fonte;
- **o que ainda é suspeita**, isto é, hipótese sem evidência pública que a sustente, seja ela
  plausível ou não.

O objetivo não é descartar a suspeita. É saber exatamente onde ela está e o que seria
preciso para testá-la.

---

## 1. O que um painel eleitoral consegue ver

Os dados são votos por município: 5.562 áreas comparáveis (AMCs) em seis eleições
presidenciais, de 2006 a 2026. Os testes comparam municípios da mesma região imediata, com
controles de renda, escolaridade, urbanização, idade e cor ou raça. Isso tem três
consequências.

1. **Uma causa que atinge o país inteiro do mesmo jeito não aparece nas comparações.** Uma
   campanha na TV aberta, o impedimento de Lula ou uma narrativa nacional nas redes movem
   todos os municípios juntos. Isso aparece na variação média do país, não na diferença entre
   municípios. Os testes só enxergam canais cuja **exposição varia de lugar para lugar**:
   igrejas, empregos, emendas, acesso à internet.
2. **Nenhum teste de voto identifica quem organizou ou financiou um canal.** "Onde a virada
   foi maior" é uma pergunta diferente de "quem causou a virada".
3. **As conclusões valem para lugares, não para pessoas.** "Municípios com mais evangélicos
   se afastaram mais do PT" não equivale a "os evangélicos se afastaram do PT", embora seja
   compatível com isso.

---

## 2. O que os dados mostram

### 2.1 Não é uma virada: são quatro movimentos

| Quando | Movimento | Medida | Resultado |
|---|---|---|---|
| 2014 | **auge da polarização regional** | peso do Nordeste no voto do PT, com o resto fixo (C1); fração da variância entre estados (C2) | 0,54 (2010) → **0,77** (2014) → 0,35 (2018); 62% → **72%** → 64% |
| 2014→2018 | **choque urbano** contra o PT | efeito do tamanho do município (C5) | −0,062 e −0,046 nas transições anteriores; **−0,133** |
| 2014→2018 | **realinhamento religioso** | % evangélica em 2010 (E2a); voto em candidatos religiosos para deputado em 2014 (E2c) | zero nas transições anteriores; **−0,091** e **−0,027** |
| desde 2018 | **afastamento dos pequenos** e **congelamento do mapa** | efeito do tamanho (C5); correlação do mapa com o pleito anterior (E0) | **+0,036** (2018→22) e **+0,025** (2022→26); 0,84–0,89 antes, **0,92–0,99** depois |

Os coeficientes estão em logit, a escala dos modelos. Para dar uma ideia de tamanho: o
**choque urbano** de 2014→2018 equivale a algo como 15 pontos percentuais de diferença entre
um município de 3 mil e um de 300 mil eleitores, contra uns 5 a 7 pontos nas transições
anteriores (conta aproximada, perto de 50%). O efeito evangélico de 2018 é de cerca de 2 pontos
por desvio-padrão da % evangélica.

**2014 é o auge de outra coisa.** A eleição de 2014 foi a mais regionalmente dividida da
série: o Nordeste pesou mais do que nunca no voto do PT, mesmo comparando municípios de
mesma renda e escolaridade. É o mapa do "nós contra eles". Mas nada da geografia de 2018
aparece ali: o gradiente de tamanho de 2010→2014 é o de sempre e o efeito evangélico é zero.

**O choque urbano de 2018 é nacional e é mudança de voto.** Aparece nas cinco regiões,
sobrevive quando se tiram São Paulo, Minas e Rio (os estados dos candidatos) e está todo na
fatia do PT, não no comparecimento. Parte dele vem da fragmentação: de 2010 a 2018 os outros
candidatos tinham 27–33% dos válidos nas cidades grandes; em 2022, 6–12%.

**O efeito religioso tem duas faces.** A composição (% evangélica do Censo) e a organização
política (voto em pastores, bispos e missionários para deputado) quase não se correlacionam
(0,18), e as duas mantêm o efeito quando entram juntas. Ou seja, não é só "onde há mais
evangélicos": é também "onde as igrejas já tinham máquina eleitoral em 2014".

**Desde 2018, o mapa congelou.** A correlação do voto do adversário com o pleito anterior
subiu de 0,85–0,89 para 0,975 em 2018→2022 e 0,986 em 2022→2026. No 2º turno, o congelamento
começa antes, e o molde é o Dilma × Aécio de 2014.

### 2.2 O choque urbano passou; o religioso ficou

A pergunta decisiva sobre 2018 é o que foi **momento** e o que foi **estrutura**. Uma forma
de separar os dois é medir quanto do efeito de 2014→2018 ainda está lá depois, comparando
sempre com 2014.

| Componente | 2014→2018 | acumulado até 2022 | acumulado até 2026 | retido em 2026 |
|---|---|---|---|---|
| Tamanho do município (choque urbano) | −0,133 | −0,057 | −0,026 | **19%** |
| % evangélica em 2010 | −0,091 | −0,102 | −0,081 | **89%** |
| Voto em candidatos religiosos em 2014 | −0,027 | −0,028 | −0,022 | **81%** |

*Tamanho: E0 (`07_virada_2018`). Religião: o mesmo modelo da E2 com as transições 2014→2018,
2014→2022 e 2014→2026 (exploratório, feito para este texto). Todos com IC 95% excluindo zero.*

O **choque urbano** se comporta como efeito de contexto e de candidato. Em 2018, Lula estava
preso e impedido, Haddad entrou na disputa a quatro semanas do 1º turno, o campo estava
fragmentado e a Lava Jato e a recessão estavam no auge. Quando Lula voltou à urna em 2022, as
cidades grandes voltaram em boa parte. Em 2026 resta um quinto do choque.

O **efeito religioso** se comporta como realinhamento. Ele **cresceu** em 2022, com Lula de
volta como candidato, e recuou pouco em 2026. O que se abriu em 2018 entre os municípios mais
e menos evangélicos continua aberto.

Essa é provavelmente a distinção mais importante deste texto. "O que aconteceu em 2018" tem
uma parte que passou e outra que ficou, e elas pedem explicações diferentes.

### 2.3 E Junho de 2013?

2013 não teve eleição. A janela mais próxima é a transição 2010→2014, e nela:

- o gradiente de tamanho é o habitual (−0,046, contra −0,062 em 2006→2010);
- os efeitos evangélico e de candidatos religiosos são zero (são os placebos da E2);
- o PT cai cerca de 4 pontos no país (59,0% → 55,4% entre os dois maiores);
- o que muda é a intensidade regional (seção 2.1).

Se Junho de 2013 deu início ao processo que culmina em 2018, ele não deixou no voto de 2014 a
geografia que o voto de 2018 teria. Essa geografia aparece de repente, em 2018. Isso **não**
exclui Junho de 2013 como causa: ele pode ter agido por canais nacionais, invisíveis no
painel, ou com atraso. Mas tira o apoio da ideia de um "pico de 2014" do mesmo processo. Nos
nossos dados, 2014 é o pico de um processo diferente: a polarização regional e de classe.

### 2.4 Leituras que precisam de ajuste

- **A3 e A8 não observam 2014–2018.** As duas comparam 2022 com 2026. O resultado nulo da A3
  (o crescimento evangélico entre os Censos não prevê a queda de 2026) é coerente com a E2:
  o efeito evangélico foi um evento de 2018, que persiste no nível mas não gera mais
  movimento. "As igrejas não têm o mesmo impacto em 2026" está certo quanto ao movimento e
  errado quanto ao nível. A diferença aberta em 2018 continua lá (C1: −0,15 em 2018, −0,17 em
  2022, −0,13 em 2026, contra +0,01 em 2006).
- **A C4 não diz que o voto ficou uniforme desde 2018.** A uniformidade é só de 2022→2026
  (desvio-padrão da variação de 0,14, contra 0,40–0,49 antes, inclusive 0,43 em 2018→2022).
  O que começa em 2018 é a **estabilidade** do mapa, que é outra coisa. A C2 mostra ainda que
  o voto ficou **mais** regional dentro dos estados (entre regiões imediatas da mesma UF: de
  15% para 25% da variância), não mais homogêneo. A uniformidade de 2022→2026 também tem uma
  explicação simples: é a única transição com o mesmo candidato do PT nas duas pontas, contra
  a mesma família política.
- **A dispersão geográfica não é recorde.** A variância do voto do PT entre municípios
  atingiu o máximo em 2018 (1,18, contra 0,61 em 2006) e em 2022–2026 é a **menor** da série
  (0,52 e 0,49). Isso não contradiz a percepção de polarização: mede o quanto os *lugares*
  diferem, não o quanto as *pessoas* se hostilizam. O que 2018 deixou é um mapa que não se
  mexe, não um mapa mais dividido.
- **A C5 não é bizarra na sua primeira parte.** O gradiente negativo de 2006 a 2014 é a
  continuação do realinhamento de 2006, bem documentado por Singer, Hunter e Power e Zucco: a
  base do PT migrou das cidades grandes para o interior pobre e o Nordeste. O que pede
  explicação é a **intensidade** de 2014→2018 (duas a três vezes a das anteriores) e a
  **troca de sinal** depois.

### 2.5 Os quatro tipos da C3, em valores absolutos

A C3 agrupa os municípios pela forma da trajetória **em relação à média nacional**, e isso pode
enganar: um município "sobe em relação à média" em 2018 se ficou parado enquanto o país caía.
Em valores absolutos (mediana da fatia do PT entre os dois maiores, em %):

| Tipo (nome atual) | AMCs | % do eleitorado | Perfil | 2006 | 2010 | 2014 | 2018 | 2022 | 2026 |
|---|---|---|---|---|---|---|---|---|---|
| Viraram redutos do PT | 1.192 | 9% | 69% no Nordeste; os mais pobres; menos evangélicos (16%) | 63 | 68 | 78 | 78 | 78 | 73 |
| Subiram até 2018 e voltaram | 1.924 | 16% | interior (36% NE, 27% Sul); os menores; mais agro | 58 | 66 | 68 | 58 | 60 | 52 |
| Afastamento gradual | 1.127 | 33% | 36% Sul, 25% Sudeste; renda alta; mais evangélicos (28%) | 53 | 60 | 53 | 30 | 42 | 35 |
| Antipetistas que se aproximaram | 1.319 | 42% | 72% Sudeste; os mais urbanos (87%) e ricos | 41 | 48 | 40 | 27 | 45 | 38 |
| *País (total de votos)* | | | | *54* | *59* | *55* | *39* | *53* | *49* |

- **Ninguém "subiu até 2018".** Os redutos do Nordeste ficaram estáveis em ~78% de 2014 a
  2022; o pico relativo de 2018 é o país caindo em volta deles. O tipo do interior caiu em
  2018, menos que o país, e caiu de novo em 2026: é ali que mora o afastamento dos pequenos.
- **O "afastamento gradual" não é gradual.** É um colapso em 2018 (53 → 30) com volta
  parcial. É também o tipo com mais evangélicos, o que combina com a parte persistente da
  seção 2.2.
- **Os "antipetistas que se aproximaram"** são as cidades grandes do Sudeste. Caíram em 2018
  como todos e em 2022 voltaram acima do nível de 2014. É o choque urbano com volta, em
  estado puro.
- **Por que quatro?** Os tipos são estáveis (os mesmos grupos com outras sementes do
  algoritmo), mas pouco separados: a silhueta é baixa (0,22). São uma partição de um contínuo,
  não grupos naturais. Dois eixos explicam 77% da variação de forma: o primeiro (53%) opõe
  2006–2010 a 2018 (o realinhamento até 2018); o segundo (25%) opõe 2014–2018 a 2022–2026 (o
  que veio depois). O primeiro eixo separa os redutos do Nordeste do tipo que colapsou em
  2018. O segundo separa as cidades grandes que voltaram depois de 2018 do interior, que
  seguiu caindo. Cada tipo ocupa uma região desse plano. A C3 redescreve os dois fenômenos
  do E0; não acrescenta um terceiro.

Nomes mais fiéis seriam: *redutos estáveis do Nordeste*, *interior que resistiu em 2018 e
cedeu depois*, *colapso de 2018 com volta parcial* e *cidades grandes antipetistas: queda e
volta*.

---

## 3. O que a história documenta, 2013–2018

Todos os itens desta seção estão documentados (fontes nas referências). A cronologia mostra
quanta coisa aconteceu ao mesmo tempo: qualquer uma delas é candidata a explicar parte da
virada, e é por isso que a coincidência no tempo, sozinha, não aponta para nenhuma.

| Data | Evento |
|---|---|
| jun/2013 | Jornadas de Junho. Apoio nacional aos protestos entre 75% e 84% nas pesquisas de junho e julho. A aprovação de Dilma cai de 57% para 30% em três semanas (Datafolha) |
| set/2013 | Revelado que a NSA monitorava as comunicações de Dilma e a Petrobras. Dilma adia a visita de Estado a Washington e denuncia a espionagem na ONU |
| mar/2014 | Começa a Lava Jato |
| jul/2014 | Cúpula de Fortaleza cria o Novo Banco de Desenvolvimento (NDB) e o arranjo de reservas dos BRICS |
| out/2014 | Dilma reeleita com 51,6% contra 48,4%. Quatro dias depois, o PSDB pede auditoria do resultado. A auditoria (nov/2015) não acha fraude, mas chama o sistema de "inauditável" |
| 2015–2016 | Recessão: PIB −3,5% (2015) e −3,3% (2016); o desemprego chega a 13,7% no início de 2017 |
| mar/2015 | Emendas parlamentares individuais viram obrigatórias (EC 86) |
| set/2015 | O STF proíbe doações de empresas a campanhas. A minirreforma corta a campanha de 90 para 45 dias. O voto impresso (emenda de Bolsonaro) entra na lei; o veto de Dilma é derrubado em novembro |
| dez/2015 | Eduardo Cunha aceita o pedido de impeachment |
| mar/2016 | O PRB (Igreja Universal) deixa a base do governo; depois, o PMDB |
| mai/2016 | Dilma é afastada. No mesmo dia, Bolsonaro é batizado no rio Jordão pelo Pastor Everaldo (PSC) |
| ago/2016 | Dilma é cassada |
| nov–dez/2016 | Lei 13.365 acaba com a operação obrigatória da Petrobras no pré-sal; teto de gastos (EC 95) |
| 2017 | Terceirização (mar), reforma trabalhista (jul) e fundo público de campanha, R$ 1,7 bi em 2018 (out). Moro condena Lula (jul) |
| jan–abr/2018 | TRF4 confirma a condenação (jan). Lula é preso (abr). O STF suspende o voto impresso (jun) |
| ago/2018 | Lula lidera as pesquisas (Datafolha: 39% contra 19% de Bolsonaro). Eduardo Bolsonaro se encontra com Steve Bannon |
| set/2018 | O TSE impede Lula (1º/set). Bolsonaro é esfaqueado (6/set). Haddad é registrado (11/set). Edir Macedo declara voto em Bolsonaro (28–29/set). Bolsonaro tem 8 segundos de TV por bloco |
| out/2018 | A Folha revela empresas comprando disparos em massa contra o PT no WhatsApp (18/out). Bolsonaro vence |
| 2019–2022 | Lula é solto (nov/2019); as condenações são anuladas e Moro é declarado parcial pelo STF (2021); o Comitê de Direitos Humanos da ONU conclui que os direitos de Lula foram violados (2022) |

Três observações sobre essa cronologia.

**Junho de 2013 não foi um bloco unido que depois se partiu.** Angela Alonso (*Treze*, 2023)
mostra três campos que conviveram nas ruas desde o início, sem coordenação: um socialista, um
autonomista e um patriota, à direita. O que tinham em comum era a oposição ao PT. O apoio era
amplo justamente porque as pautas eram muitas. Alonso rejeita a leitura de Junho como "ovo
da serpente" do bolsonarismo. Essa leitura historiográfica converge com o que os dados da
seção 2.3 sugerem: a geografia de 2018 não estava no voto de 2014. Sobre o "quase 90%": o
único número perto disso (89%, CNI-Ibope, julho) soma 50% "a favor" com 39% "a favor, se
sem violência". Nas outras pesquisas nacionais, o apoio fica entre 75% e 84%.

**A desconfiança das urnas tem genealogia doméstica.** Antes de Bolsonaro, o PSDB pediu
auditoria do resultado de 2014, e o voto impresso entrou na lei em 2015 por emenda do
próprio Bolsonaro, com o Congresso derrubando o veto de Dilma.

**As regras do jogo mudaram entre 2014 e 2018.** Sem dinheiro de empresas, com campanha
curta e com Bolsonaro tendo 8 segundos de TV, ganharam peso os canais que funcionam sem
dinheiro empresarial nem TV: igrejas, redes de mensagens, militância digital. É uma mudança
documentada que ajuda a explicar **por que** a pegada de 2018 aparece nas igrejas
(seção 5).

---

## 4. A hipótese da interferência externa

A hipótese, na forma mais forte: os Estados Unidos, ameaçados pela aproximação do Brasil com
os BRICS e o Sul Global, induziram a sequência que vai de Junho de 2013 à eleição de
Bolsonaro. Ela tem uma probabilidade prévia que não é desprezível, porque há precedentes
documentados. Mas ter precedente não é ter evidência sobre este caso. Esta seção separa as
duas coisas.

### 4.1 O que é documentado

- **Precedente histórico.** Em 1962, o IBAD financiou candidatos com dinheiro que incluía
  recursos de empresas estrangeiras (CPI de 1963; o IBAD foi dissolvido por ordem judicial).
  Em 1964, documentos americanos já liberados registram a Operação Brother Sam (navios e uma
  força-tarefa de porta-aviões para apoiar o golpe) e telegramas do embaixador Lincoln Gordon.
  Os arquivos operacionais da CIA sobre o Brasil continuam secretos.
- **Espionagem (2013).** A NSA monitorava as comunicações de Dilma e de assessores e espionou a
  Petrobras. Os documentos de Snowden mostram o monitoramento como alvo, não o conteúdo
  interceptado.
- **Petróleo (2009–2016).** Um telegrama do consulado americano no Rio (dez/2009, publicado
  em 2010) relata que uma executiva da Chevron ouviu de José Serra que, se a oposição
  vencesse, as regras do pré-sal seriam mudadas de volta. É um relato de segunda mão. Em
  2016, um projeto de Serra virou a Lei 13.365, que acabou com a operação obrigatória da
  Petrobras no pré-sal.
- **Formação de juízes e procuradores (2009).** Um telegrama da embaixada descreve um seminário
  sobre lavagem de dinheiro financiado pelo Departamento de Estado (o primeiro do "Projeto
  Pontes"), com juízes e procuradores de todo o país. Sergio Moro aparece como palestrante. A
  ideia de que o seminário "criou" a Lava Jato não está no documento.
- **Cooperação com a Lava Jato (2015–2017).** Em outubro de 2015, pelo menos 17 agentes
  americanos (Departamento de Justiça e FBI) trabalharam na força-tarefa em Curitiba sem
  pedido formal de cooperação, e o Ministério da Justiça soube pelo Itamaraty (Agência Pública
  e The Intercept Brasil, 2020). Em 2017, um alto funcionário do Departamento de Justiça
  elogiou publicamente a troca informal de informações com o Brasil.
- **Acordos de corrupção no exterior (FCPA).** Odebrecht e Braskem pagaram ao menos US$ 3,5 bi
  a EUA, Brasil e Suíça (2016). A Petrobras pagou US$ 853 milhões, 80% destinados ao Brasil,
  mais US$ 933 milhões à SEC (2018). Parte desse dinheiro iria para uma fundação privada da
  Lava Jato, suspensa pelo STF em 2019.
- **Rede libertária americana (2012–2017).** A Atlas Network e a Students for Liberty eram as
  principais financiadoras do Estudantes pela Liberdade (EPL), com orçamento de cerca de
  R$ 300 mil em 2015. Segundo o diretor do EPL, membros do grupo criaram a marca "MBL" para os
  protestos de 2013, porque as regras fiscais americanas impediam o EPL de agir
  politicamente. O MBL depois ganhou vida própria (Agência Pública, 2015; The Intercept,
  2017). A Atlas é uma rede privada, financiada por doadores privados.
- **Bannon (2018–2019).** Eduardo Bolsonaro se encontrou com Steve Bannon em agosto de 2018 e
  foi nomeado líder sul-americano do "The Movement" em 2019. A parceira brasileira da
  Cambridge Analytica suspendeu a parceria em março de 2018. Não há evidência de que a CA
  tenha trabalhado para Bolsonaro.
- **Interferência aberta (2025–2026).** A carta de julho de 2025 que impôs tarifas de 50% ao
  Brasil cita o julgamento de Bolsonaro como razão. Vieram depois as sanções Magnitsky a
  Alexandre de Moraes (retiradas em dezembro de 2025), a investigação comercial que cita o
  Pix (tarifa de 25% desde julho de 2026) e a classificação de PCC e CV como organizações
  terroristas (maio de 2026). Eduardo Bolsonaro, nos EUA desde 2025, fez campanha aberta por
  essas medidas e foi condenado pelo STF por coação em junho de 2026.

### 4.2 O que é alegado sem evidência pública

- **Que a CIA financiou o MBL ou os protestos de 2013 e 2015.** Não há documento público. O
  que está documentado é o laço do EPL com a rede privada Atlas, em escala modesta. Não se
  achou doação da NED, o braço público americano de apoio à sociedade civil, ao MBL ou ao Vem
  Pra Rua.
- **Que os EUA dirigiram a Lava Jato ou miraram Lula.** Está documentada a cooperação,
  inclusive informal e escondida do governo. Que ela tenha sido direção, não.
- **Que os EUA orquestraram Junho de 2013 ou o impeachment.** Não há evidência. A
  historiografia explica Junho por raízes domésticas que vêm desde 2003 (Alonso) e o
  impeachment pela ruptura da coalizão e pela oposição empresarial a Dilma (Singer, 2018).
- **A tese da "guerra híbrida".** O livro de Andrew Korybko (2015) saiu por uma universidade de
  Moscou, trata da Síria e da Ucrânia, e o autor escrevia para a Sputnik. A aplicação ao
  Brasil veio depois, em comentários e em veículos da esquerda brasileira. É um quadro
  interpretativo, com pouca recepção acadêmica, não evidência.

### 4.3 Correções ao brainstorming original

O brainstorming que motivou este texto misturava fatos, interpretações e alguns erros de data.
A tabela registra o que os registros mostram.

**Sobre 2013–2018:**

| Afirmação | O que os registros mostram |
|---|---|
| "quase 90% de apoio" a Junho de 2013 | 75% a 84% nas pesquisas nacionais. Os 89% somam "a favor" com "a favor, se sem violência" |
| em 2013, o "quarto governo de esquerda" | o terceiro (Lula 2003–06 e 2007–10, Dilma 2011–14) |
| impeachment no "pico de 2014" | Dilma foi reeleita em out/2014, afastada em mai/2016 e cassada em ago/2016 |
| o Brasil "liderava os BRICS+" | o BRICS+ só existe desde 2024. Em 2013 eram cinco países; o NDB foi criado em jul/2014 |
| o Sul Global "fundou o BRICS" em resposta a Trump | primeira cúpula em 2009. A resposta a Trump é a ampliação, não a fundação |
| o Pix tornou o Brasil independente do SWIFT e do dólar | o Pix é do Banco Central: começou sob Temer (2018) e foi lançado sob Bolsonaro (nov/2020). É doméstico, em reais, e nunca dependeu do SWIFT, que é para mensagens internacionais. O ponto real é a concorrência com as bandeiras de cartão |
| Vorcaro "comprou Brasília inteira com dinheiro público" | o Banco Master só cresce a partir de 2019, e não cabe na janela de 2013–2018. Documentado: o BRB (banco público do DF) comprou ~R$ 12 bi em carteiras que a PF suspeita serem falsas; 18 regimes próprios de previdência aplicaram R$ 1,9 bi. As ligações políticas são alegações sob investigação. O FGC, que cobriu ~R$ 41 bi, é bancado pelos bancos, não pelo Tesouro |

**Sobre 2022–2026:**

| Afirmação | O que os registros mostram |
|---|---|
| Trump bloqueou a Rússia do dólar e do SWIFT | foi em fev–mar/2022, sob Biden, junto com a UE |
| Trump declarou guerra comercial à China | começou em 2018, no primeiro mandato. Em 2025–26: escalada e tréguas sucessivas |
| ameaçou tarifas a quem se aliasse aos BRICS | ameaças confirmadas (nov/2024 e jul/2025); nenhuma executada |
| tarifas sobre o Brasil, com quem tem superávit | confirmado: 50% desde ago/2025, justificados pelo julgamento de Bolsonaro. Alimentos excluídos em nov/2025. A Suprema Corte derrubou a base legal em fev/2026. Desde jul/2026, 25% pela Seção 301 |
| Lei Magnitsky contra Moraes | confirmado (jul/2025; a esposa em set/2025). Retiradas em dez/2025 |
| acusou o Pix de prática desleal | confirmado (investigação aberta em jul/2025; decisão em jun/2026) |
| CV e PCC como organizações terroristas | confirmado (mai/2026) |
| "Doutrina Donroe"; o Brasil prioritário no documento de segurança | o "Corolário Trump" à Doutrina Monroe está na Estratégia de Segurança Nacional (dez/2025); "Donroe" é apelido da imprensa. **O Brasil não é citado** no documento |
| capturou Maduro e "colonizou" a Venezuela | captura confirmada (jan/2026); os EUA controlam a venda do petróleo venezuelano. "Colonizar" é interpretação |
| endureceu o bloqueio e ameaçou invadir Cuba | bloqueio endurecido (jan/2026); invasão só insinuada |
| tomou o controle da Groenlândia | **não**: ameaças, tarifas depois retiradas e um acordo de defesa que amplia bases (set/2026). A soberania segue dinamarquesa |
| tentou anexar o Canadá | só retórica ("51º estado") |
| declarou guerra ao Irã | não houve declaração formal. Houve ataques em jun/2025 e uma guerra de fato, com Israel, desde fev/2026 |
| o Irã fechou Hormuz, "bomba nos petrodólares" | o estreito foi declarado fechado em mar/2026, como resposta militar à guerra, e o Brent chegou a US$ 126. Não foi política monetária dos BRICS |
| Dilma preside o NDB e foi condecorada pela China | confirmado (presidente desde 2023, reconduzida em 2025; Medalha da Amizade em set/2024) |
| BRICS Pay, "The Unit", Drex | o BRICS Pay é projeto do conselho empresarial e não funciona. "The Unit" é proposta de círculos russos, não política oficial. O Drex foi reduzido em 2025 |

A lista de 2025–2026 mostra uma política externa americana agressiva e, no caso do Brasil,
uma interferência aberta e documentada. Mas ela é evidência sobre **2025–2026**. Usá-la para
explicar 2013–2018 é anacronismo: o governo americano era outro (Obama), e as relações foram
retomadas em plena Lava Jato, com a visita de Dilma a Washington em junho de 2015.

### 4.4 Armadilhas de raciocínio

- **"A quem interessa" não é causa.** Que os EUA se beneficiem de um resultado aumenta a
  plausibilidade de uma ação, não mostra que ela aconteceu.
- **Coincidência no tempo não escolhe uma causa.** Entre 2013 e 2018 aconteceu de tudo (seção
  3). Uma coincidência com a interferência é também uma coincidência com a recessão, a Lava
  Jato e o impedimento de Lula.
- **Uma quebra nacional é compatível com qualquer causa nacional.** É o limite dos nossos
  dados (seção 1): uniformidade não aponta para ninguém.
- **Coerência não é evidência.** Uma história em que tudo se encaixa é mais fácil de contar,
  não mais provável. Cada elo precisa de evidência própria, e a probabilidade da cadeia
  inteira é no máximo a do elo mais fraco.
- **Uma tese que explica qualquer resultado não explica nada.** Se a vitória da direita prova
  a interferência e a da esquerda prova que ela falhou, a tese não pode ser testada.

### 4.5 O que contaria como evidência

- **Dinheiro:** fluxos do governo ou de fundações americanas para as organizações que lideraram
  2015–2016, com datas, em registros públicos (NED, USAID, formulários fiscais das
  fundações). Por exemplo, um aumento em 2013–2016 dirigido a esses grupos.
- **Documentos:** telegramas, papéis desclassificados ou autos judiciais mostrando
  coordenação em decisões específicas, além da cooperação já conhecida.
- **Nos nossos dados:** um canal com exposição ligada aos EUA que varie entre municípios (por
  exemplo, presença de organizações da rede Atlas) e mostre a pegada de 2014→2018. Depende
  de existir o dado.

O fio com mais documentos passa pelo **petróleo**: a NSA na Petrobras, o telegrama de 2009, a
lei de 2016 e, depois, a abertura do pré-sal a operadoras estrangeiras. Não passa pelos BRICS,
cuja disputa com o dólar se intensifica sobretudo depois das sanções à Rússia, em 2022. Isso faz do petróleo o melhor
candidato a investigação (série F do plano), não uma conclusão.

### 4.6 Explicações domésticas que competem

Cada uma é documentada e várias têm teste no painel: recessão (E4a); colapso local de
petróleo, indústria naval e obras (E4b); violência (E5); transformação do trabalho (E7);
projeto político das igrejas e a troca de lado da Universal (E2, E2d); máquinas locais e
emendas (E1); WhatsApp e redes (E3); impedimento de Lula e efeito de candidato (E0b); novas
regras de financiamento (série F). Elas não excluem influência externa, e várias podem ter
agido juntas. A diferença é que estas têm evidência e teste; a interferência externa em
2013–2018, por enquanto, não tem nenhum dos dois.

---

## 5. As perguntas, uma a uma

### "O que, quem e com que dinheiro, entre 2013 e 2018?"

**O quê** os dados respondem em parte (seção 2): um choque urbano passageiro, um
realinhamento religioso persistente e, depois, o afastamento dos pequenos e o congelamento
do mapa. **Quem** e **com que dinheiro** estão fora do alcance de um painel de votos (seção 1)
e pedem a trilha documental do plano (série F).

Há, porém, um fato institucional que muda o sentido de "dinheiro" nessa história: **2018 foi a
primeira eleição geral sem doação de empresas** (proibida pelo STF em 2015) e com o fundo
público de campanha, numa campanha mais curta. Bolsonaro tinha segundos de TV e venceu. Quando
o dinheiro empresarial e o tempo de TV perdem peso, ganham peso os canais que funcionam sem
eles: organizações com capilaridade própria (igrejas), redes de mensagens e militância
digital. São justamente os canais com pegada em 2018 (igrejas) ou sob suspeita (WhatsApp).
Investigar quem financiou 2018 passa, portanto, por esses canais, e não só pelas contas
oficiais de campanha.

### "Quem financiou a virada das igrejas? EUA? As próprias igrejas? Vorcaro?"

O painel não diz quem financiou. O que ele diz, e a história completa, é o seguinte:

- **A infraestrutura já existia em 2014.** O efeito da E2c é maior onde candidatos religiosos
  já tinham voto em 2014. A capacidade eleitoral das igrejas não foi criada em 2018: ela
  **mudou de lado** em 2018.
- **A troca de lado mais documentada é a da Igreja Universal.** O partido ligado a ela (PRB,
  hoje Republicanos) foi o partido do vice-presidente José Alencar, teve um ministério com
  Dilma e esteve na coligação dela em 2014. Deixou a base em março de 2016, um mês antes da
  votação do impeachment na Câmara, e o líder da igreja declarou voto em Bolsonaro em 2018
  (seção 3). A hipótese nova **E2d** testa exatamente isso: se o salto de 2018 se
  concentra onde eram fortes os candidatos religiosos de partidos aliados do PT em 2014.
- **O financiamento das igrejas é, em grande parte, doméstico e conhecido:** dízimo, redes
  de rádio e TV próprias e imunidade tributária. Não há evidência pública de dinheiro
  americano na mobilização das igrejas em 2018.
- **Vorcaro está fora da janela.** O Banco Master só cresce a partir de 2019 (seção 4.3);
  não pode explicar 2014–2018.

### "O que explica os quatro tipos da C3?"

A seção 2.5 responde: dois eixos (o realinhamento até 2018 e o que veio depois) e a geografia
que os acompanha (Nordeste pobre, interior agro, Sul e Sudeste de renda alta e mais
evangélico, grandes cidades do Sudeste). Lidos em valores absolutos, os tipos contam a mesma
história das seções 2.1 e 2.2.

### "Que fatia do resultado é decidida pela máquina, que fatia pelo povo e que fatia pelos EUA?"

A pergunta, nessa forma, não tem resposta. Prefeitos, deputados e emendas agem **por meio**
dos eleitores, não em paralelo a eles, e efeitos que interagem não se somam em fatias. O que
dá para estimar:

- **o efeito local de eleger um prefeito de direita** num município de disputa apertada
  (RDD, hipóteses A5 e E1b, que o plano propõe fundir para 2016, 2020 e 2024);
- **quanto do gradiente de tamanho cada canal absorve** (E6), como a A1 fez com a
  composição;
- **um contrafactual nacional com hipóteses explícitas**, como limite superior.

A fatia "dos EUA" não é estimável com votos. Mesmo uma interferência real agiria por algum
canal (dinheiro para organizações, conteúdo nas redes, cooperação judicial), e o que se pode
medir é o canal, nunca a origem.

Há uma pista forte para a máquina pública: o **afastamento dos pequenos começa junto com uma
mudança no orçamento**. As emendas parlamentares individuais viraram obrigatórias em 2015, as
de bancada em 2019, as transferências diretas aos municípios ("emendas Pix") passaram a
existir em 2019 e o "orçamento secreto" funcionou de 2020 a 2022. Os municípios pequenos são
os que mais dependem desse dinheiro. Isso faz da E1a (emendas por habitante) a melhor
candidata a explicar o fenômeno pós-2018.

### "As redes sociais e o TikTok" (E3)

É uma hipótese plausível, com literatura sobre o WhatsApp em 2018. Mas o calendário importa.
Em 2018 os canais eram WhatsApp, Facebook e YouTube. TikTok e Kwai viram canais de massa no
Brasil a partir de 2019–2020. Eles não podem explicar o choque de 2018, mas podem fazer parte
do afastamento dos pequenos desde então. Para esse fenômeno a Anatel tem dados por município
(acessos móveis desde 2019; cobertura 4G e 5G desde 2021). A medida registrada hoje para a
E3 (banda larga fixa) é fraca; o plano propõe duas medidas novas.

Há também uma versão mais sólida da intuição sobre o digital. Quando o ambiente de informação
se nacionaliza (os mesmos vídeos e mensagens em toda parte, o noticiário local
enfraquecido), as variações ficam uniformes, porque o que move o voto é o mesmo em todo
lugar. Hopkins documentou isso nos EUA. A uniformidade de 2022→2026 (C4) é compatível com
essa leitura, embora a explicação mais simples (mesmos candidatos) ainda não tenha sido
descartada.

### "E4 e E7 se ligam ao cenário global"

Em parte. A **E4b** mede o custo eleitoral local do colapso de petróleo, indústria naval e
obras: os setores mais atingidos pela Lava Jato e mais ligados à estratégia de
desenvolvimento dos governos do PT. Se houver pegada, ela mostra **onde** esse colapso pesou
no voto. Não diz quem conduziu a Lava Jato, nem por quê. A **E7** mede a passagem do emprego
assalariado para o trabalho por conta própria, que é ao mesmo tempo tendência global (as
plataformas) e escolha doméstica (o MEI em 2009, a reforma trabalhista em 2017).

### "A E5 vai ser rejeitada"

É uma boa aposta, e vale registrá-la em `hipoteses.md` antes de rodar. Há uma razão nos
próprios dados: o aumento dos homicídios entre 2011–13 e 2015–17 se concentrou no Norte
(+10,7 por 100 mil) e no Nordeste (+8,0), onde o PT resistiu; no Sudeste, onde o choque urbano
foi forte, a taxa ficou estável (−0,5). (SIM, com a população de 2022 como aproximação.)
Uma ressalva para a leitura do resultado: um nulo rejeita a **exposição local** à violência,
não a segurança como tema nacional de campanha, que age igual em todo o país e o painel não
vê.

---

## 6. O que dá para afirmar hoje

1. **[dado]** A virada de 2018 combina um choque urbano que já reverteu ~80% e um
   realinhamento religioso que persiste. Desde 2018, os pequenos se afastam do PT e o mapa
   congelou.
2. **[dado]** Nada disso aparece em 2014. A eleição de 2014 foi o auge da polarização
   regional, que é outro fenômeno.
3. **[documentado]** Entre 2013 e 2018 houve uma sequência de choques domésticos (Lava Jato,
   recessão, ruptura da coalizão, impeachment, impedimento de Lula, novas regras de
   financiamento), e cada um é candidato a explicar parte da virada.
4. **[documentado]** Houve ação americana relevante no período: a espionagem da NSA, a
   cooperação informal com a Lava Jato e os acordos bilionários de FCPA. Em 2025–2026 houve
   interferência aberta.
5. **[suspeita]** Que a ação americana tenha causado Junho de 2013, o impeachment ou a eleição
   de 2018 não tem evidência pública, e os nossos dados não podem testá-lo.
6. **[pergunta aberta]** Quem organizou e financiou os canais com pegada em 2018 (as igrejas
   e, possivelmente, as redes) é a pergunta certa, e tem caminho documental (série F do
   plano).

---

## Referências

### Historiografia e ciência política

- Alonso, Angela. *Treze: a política de rua de Lula a Dilma*. Companhia das Letras, 2023.
- Hopkins, Daniel J. *The Increasingly United States*. University of Chicago Press, 2018.
- Hunter, Wendy; Power, Timothy. "Rewarding Lula: Executive Power, Social Policy, and the
  Brazilian Elections of 2006". *Latin American Politics and Society* 49(1), 2007.
- Korybko, Andrew. *Guerras híbridas: das revoluções coloridas aos golpes*. Expressão
  Popular, 2018 (original de 2015).
- Nobre, Marcos. *Imobilismo em movimento*. Companhia das Letras, 2013.
- Pinheiro-Machado, Rosana. *Amanhã vai ser maior*. Planeta, 2019.
- Samuels, David; Zucco, Cesar. *Partisans, Antipartisans, and Nonpartisans: Voting Behavior
  in Brazil*. Cambridge University Press, 2018.
- Singer, André. "Raízes sociais e ideológicas do lulismo". *Novos Estudos CEBRAP* 85, 2009.
- Singer, André. *Os sentidos do lulismo*. Companhia das Letras, 2012.
- Singer, André. *O lulismo em crise*. Companhia das Letras, 2018.
- Zucco, Cesar. "The President's 'New' Constituency: Lula and the Pragmatic Vote in Brazil's
  2006 Presidential Elections". *Journal of Latin American Studies* 40(1), 2008.

### Documentos e reportagens, 2009–2018

- Telegrama 09RIODEJANEIRO369 (pré-sal): <https://wikileaks.org/plusd/cables/09RIODEJANEIRO369_a.html>
- Telegrama 09BRASILIA1282 (Projeto Pontes): <https://wikileaks.org/plusd/cables/09BRASILIA1282_a.html>
- NSA e Petrobras (Bloomberg, set/2013): <https://www.bloomberg.com/news/articles/2013-09-09/snowden-documents-show-u-s-spied-on-petrobras-globo-tv-reports>
- Lei 13.365 no Senado (Congresso em Foco): <https://www.congressoemfoco.com.br/noticia/46855/senado-desobriga-petrobras-de-investir-no-pre-sal>
- FBI e procuradores americanos em Curitiba (Agência Pública, 2020): <https://apublica.org/2020/03/como-a-lava-jato-escondeu-do-governo-federal-visita-do-fbi-e-procuradores-americanos/>
- Kenneth Blanco no Atlantic Council (DOJ, 2017): <https://justice.gov/opa/speech/acting-assistant-attorney-general-kenneth-blanco-speaks-atlantic-council-inter-american-1>
- FCPA, Odebrecht e Braskem (Stanford): <https://fcpa.stanford.edu/enforcement-action.html?id=635>
- Fundação da Lava Jato suspensa (Poder360): <https://www.poder360.com.br/justica/alexandre-de-moraes-suspende-acordo-que-previa-fundacao-da-lava-jato/>
- EPL, Atlas e a criação do MBL (Agência Pública, 2015): <https://apublica.org/2015/06/a-nova-roupa-da-direita/>
- "Sphere of Influence" (The Intercept, 2017): <https://theintercept.com/2017/08/09/atlas-network-alejandro-chafuen-libertarian-think-tank-latin-america-brazil/>
- Cambridge Analytica no Brasil (BuzzFeed News): <https://www.buzzfeednews.com/article/mauroalbano/cambridge-analytica-brazil-suspend-partnership>
- Disparos no WhatsApp e julgamento do TSE (Agência Brasil, 2021): <https://agenciabrasil.ebc.com.br/justica/noticia/2021-10/tse-rejeita-pedido-para-cassar-chapa-bolsonaro-mourao>
- Auditoria do PSDB (Exame): <https://exame.com/brasil/auditoria-do-psdb-conclui-que-nao-houve-fraude-na-eleicao/>
- Veto ao voto impresso derrubado (Agência Senado, 2015): <https://www12.senado.leg.br/noticias/materias/2015/11/18/congresso-derruba-veto-de-dilma-e-votos-deverao-ser-impressos>
- PRB deixa a base (Congresso em Foco, 2016): <https://www.congressoemfoco.com.br/noticias/prb-anuncia-que-deixara-a-base-aliada>
- Orçamento secreto no STF (Conjur, 2022): <https://www.conjur.com.br/2022-dez-19/maioria-stf-declara-inconstitucionalidade-orcamento-secreto/>
- Suspeição de Moro (STF): <https://noticias.stf.jus.br/postsnoticias/stf-confirma-suspeicao-de-sergio-moro-na-acao-do-triplex-do-guaruja/>
- Apoio às manifestações de 2013 (CNI-Ibope, via Ipea): <https://www.ipea.gov.br/participacao/noticiasmidia/participacao-institucional/769-manifestacoes-nas-ruas-sao-aprovadas-por-89-dos-brasileiros>
- Aprovação de Dilma em junho de 2013 (Congresso em Foco): <https://congressoemfoco.com.br/noticias/jornais-aprovacao-a-dilma-despenca-de-57-a-30-em-3-semanas>
- Brother Sam (National Security Archive): <https://nsarchive2.gwu.edu/NSAEBB/NSAEBB118/index.htm>
- Brother Sam (FRUS 1964–68): <https://history.state.gov/historicaldocuments/frus1964-68v31/ch5>
- PIB de 2016 (IBGE): <https://agenciadenoticias.ibge.gov.br/agencia-noticias/22966-revisao-do-pib-de-2016-mostra-queda-de-3-3-em-relacao-ao-ano-anterior.html>

### Documentos e reportagens, 2022–2026

- Carta de Trump sobre as tarifas (jul/2025): <https://static.poder360.com.br/2025/07/Carta-Trump-Brasil-ingles.pdf>
- Seção 301 contra o Brasil (USTR, jul/2026): <https://ustr.gov/about/policy-offices/press-office/press-releases/2026/july/ustr-section-301-action-brazils-unreasonable-acts-policies-and-practices>
- Magnitsky retirada (OFAC, dez/2025): <https://ofac.treasury.gov/recent-actions/20251212>
- PCC e CV como organizações terroristas (Federal Register): <https://public-inspection.federalregister.gov/2026-11323.pdf>
- Estratégia de Segurança Nacional (Casa Branca, dez/2025): <https://www.whitehouse.gov/wp-content/uploads/2025/12/2025-National-Security-Strategy.pdf>
- SWIFT e Rússia, 2022 (Tesouro americano): <https://home.treasury.gov/news/press-releases/jy0612>
- Condenação de Eduardo Bolsonaro (STF): <https://noticias.stf.jus.br/postsnoticias/stf-condena-eduardo-bolsonaro-por-coacao-no-curso-do-processo-sobre-tentativa-de-golpe/>
- Liquidação do Banco Master (Poder360): <https://www.poder360.com.br/poder-economia/banco-central-decreta-liquidacao-extrajudicial-do-banco-master/>
- Regimes de previdência no Master (Poder360): <https://www.poder360.com.br/poder-economia/18-regimes-de-previdencia-tem-r-19-bi-aplicado-no-banco-master/>
- Recondução de Dilma ao NDB: <https://www.ndb.int/news/board-of-governors-re-elects-h-e-mrs-dilma-rousseff-as-ndb-president/>
- Origem do Pix (Aos Fatos): <https://www.aosfatos.org/noticias/bolsonaro-criou-pix-saiba-origem-sistema-pagamentos/>
- Hormuz em out/2026 (Al Jazeera): <https://www.aljazeera.com/news/2026/10/6/hormuz-ship-attacks-surge-are-increased-oil-exports-sustainable>
- Groenlândia (Al Jazeera, jan/2026): <https://www.aljazeera.com/news/2026/1/22/trumps-greenland-framework-deal-what-we-know-about-it-what-we-dont>
