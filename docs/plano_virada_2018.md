# Plano de ação: investigar a virada de 2014–2018

**Proposta de 2026-10-09, para decisão.** Acompanha o ensaio
[ensaio_virada_2018.md](ensaio_virada_2018.md), que traz os números e o contexto histórico.
Nada aqui está registrado. O que for aprovado entra em [hipoteses.md](hipoteses.md) antes de
cruzar qualquer dado com o voto, como sempre.

---

## 1. Onde estamos

- **A "virada de 2018" são três processos, com destinos diferentes** (ensaio, seção 2):
  1. um **choque urbano** em 2014→2018, que já reverteu ~80% até 2026;
  2. um **realinhamento religioso** em 2014→2018, que não reverteu (aprofundou em 2022);
  3. o **afastamento dos municípios pequenos** desde 2018, ainda em curso em 2026.

  Antes deles, 2014 foi o auge da polarização **regional**, que não tem a pegada de 2018.
- **A E2 explicou parte do processo 2.** O resto da série E (E1, E3–E5, E7) ainda não rodou.
- **Limite dos dados:** uma causa nacional produz uma quebra uniforme, que o painel absorve
  no efeito de cada transição. O painel só vê canais com **exposição desigual entre
  municípios**. E nenhum teste do painel diz quem organizou ou financiou um canal.
- **Consequência:** a pergunta sobre interferência externa precisa de uma **trilha
  documental** própria (série F, seção 3), com outro tipo de evidência.

---

## 2. Hipóteses: priorizar, criar, fundir, arquivar

### Priorizar (dados já ingeridos, custo baixo)

| ID | O quê | Situação dos dados | Observação |
|---|---|---|---|
| E2b | Igrejas no CNPJ (estoque 2014, aberturas 2014→17) | `cnpj_amc` pronto | Falta a validação prévia (correlação ≥ 0,3 com o Censo) |
| E4a, E4b | Recessão e exposição à Lava Jato (petróleo, naval, obras) | `emprego_amc` pronto (RAIS) | É o teste mais próximo da tese geopolítica que o painel permite (ver nota abaixo) |
| E5 | Homicídios | `homicidios_amc` pronto (SIM) | Registrar antes a sua **aposta** (E5 rejeitada) como prior em `hipoteses.md` |
| E7a, E7b | MEI e trabalho por conta própria | `cnpj_amc` pronto; E7b precisa do Censo 2010 (SIDRA) | |

Nota sobre a E4: se a E4b mostrar pegada, ela mede o **custo eleitoral local** do colapso
de petróleo, naval e obras. Isso vale qualquer que seja a origem da Lava Jato, e não diz nada
sobre envolvimento americano.

### Criar (registrar antes de rodar)

- **E0b · choque passageiro ou realinhamento.** Para cada mecanismo, o efeito **acumulado**
  desde 2014, medido em 2022 e em 2026, comparado ao efeito de 2014→2018. Proposta de
  critério: o efeito é *persistente* se o acumulado em 2022 mantiver ≥ 50% do efeito de
  2014→2018, com IC 95% excluindo zero. Separa o efeito de candidato e de contexto de 2018
  (Lula impedido, Haddad, campo fragmentado) da mudança estrutural.
  **Cuidado:** para o tamanho, a E2a e a E2c o resultado já é conhecido (ensaio, seção 2.2:
  43%, 112% e 103% retidos em 2022). Nesses três casos a E0b é descritiva; ela só é
  confirmatória para os mecanismos ainda não testados.
- **E2d · a virada das lideranças.** Separar a medida E2c pelo partido do candidato
  religioso em 2014: partidos da coligação de Dilma em 2014 contra os demais. A composição da
  coligação sai do próprio `consulta_cand` de 2014 (candidatura presidencial).
  - **Ideia:** o PRB (Igreja Universal) era aliado do PT até 2016 e a cúpula da Universal
    apoiou Bolsonaro em 2018. Se o salto de 2014→2018 se concentra onde eram fortes os
    candidatos religiosos de partidos **aliados** do PT, o mecanismo é a troca de lado das
    organizações, e não a política religiosa em geral.
  - **Previsão:** salto mais negativo no grupo da coligação.
  - **Evidência contra:** salto igual ou maior nos partidos de oposição.
  - **Custo:** baixo (dados já baixados, só a regra de partido no `religiao.py`).
- **E3 em duas partes.** A E3 registrada (banda larga fixa) fica como está, mas é fraca. Duas
  medidas novas:
  - **E3c (fenômeno 2, 2014→18):** % de domicílios com celular e com computador conectado à
    internet no **Censo 2010** (disponibilidade por município a conferir no SIDRA).
    Característica fixa, mesmo desenho da E7b.
  - **E3b (fenômeno 3, 2018→22 e 2022→26):** crescimento de acessos de banda larga móvel
    por município (Anatel, com série municipal desde 2019) e cobertura 4G/5G (desde 2021).
    É aqui que TikTok, Kwai e vídeo curto podem aparecer, porque eles não existiam como
    canal de massa em 2018.
- **E9 · a rua (condicional aos dados).** Geografia dos protestos pró-impeachment de
  2015–2016, e de Junho de 2013 como precursor. Só entra se houver base de eventos de
  protesto por município (ver seção 3, F3). Vai ser colinear com o tamanho, porque protesto
  é urbano. O teste interessante é a E6: quanto do choque urbano a rua absorve.

### Fundir

- **A5 + E1b → um módulo de RDD** para 2016, 2020 e 2024 (mesmo desenho, três ciclos). É a
  resposta mais limpa à pergunta "quanto pesa a máquina". O RDD estima o efeito de eleger um
  prefeito de direita nos municípios de disputa apertada. Uma conta contrafactual nacional
  (o que mudaria sem esses prefeitos) pode vir depois, como limite, com as hipóteses dela
  explícitas.
- **E4 + E7** seguem como testes separados, mas sempre lidos juntos na E6 (já previsto),
  como o bloco "economia e trabalho".

### Revisar (exploratório, custo baixo)

- **C3.** Acrescentar ao `06_serie` as trajetórias **absolutas** de cada tipo, a análise de
  componentes principais e a silhueta. Renomear os tipos (proposta no ensaio, seção 2.5):
  "subiram até 2018" é um artefato da medida relativa.

### Arquivar ou reformular

- **Banco Master / Vorcaro como causa da virada:** anacronismo. O banco cresce depois de
  2019 e não pode explicar 2014–2018 (ensaio, seção 4.3). Se interessar, é uma pergunta
  sobre 2026, fora deste desenho.
- **"Que fatia do resultado foi decidida pelos EUA":** o painel eleitoral não estima isso.
  A pergunta vira a série F.
- **"Que fatia é da máquina e que fatia é do povo":** a pergunta não tem resposta aditiva.
  Prefeitos e emendas agem *por meio* de eleitores, não em paralelo a eles. A pergunta que
  tem resposta é a do RDD (efeito local) e a da E6 (quanto do gradiente cada canal absorve).

---

## 3. Série F: influência externa e financiamento (trilha documental)

**Por quê:** é a única forma de investigar "quem" e "com que dinheiro". **O que muda:** a
evidência é documento, não regressão. **Regra de ouro:** antes de abrir cada fonte, escrever
que padrão **enfraqueceria** a tese, para não ler qualquer resultado como confirmação.

**Escala de evidência** (vale para tudo o que entrar na linha do tempo):

| Grau | Critério | Pode ir para o texto como fato? |
|---|---|---|
| **documentado** | documento primário ou decisão oficial (lei, sentença, sanção, relatório de órgão, registro público de doação) | sim |
| **reportado** | jornalismo investigativo com documentos citados | sim, atribuído ao veículo |
| **alegado** | afirmação sem documento público | não; só como alegação, com quem alega |
| **refutado** | desmentido por documento ou decisão | só para registrar |

**Frentes:**

| ID | Pergunta | Fontes | O que enfraqueceria a tese |
|---|---|---|---|
| F1 | O dinheiro público americano para a sociedade civil brasileira cresceu em 2013–2016? Para quem? | relatórios anuais e base de doações da NED (por país); ForeignAssistance.gov (USAID e Departamento de Estado, por ano e executor) | volume estável ou queda em 2013–16; destinatários sem relação com os movimentos de 2015–16 |
| F2 | Quanto dinheiro privado americano chegou a think tanks e movimentos brasileiros? | formulários 990 das fundações (anexo de doações ao exterior), via ProPublica Nonprofit Explorer e Candid; relatórios da Atlas Network | valores pequenos perto do financiamento doméstico (doações, empresários brasileiros) |
| F3 | Quem são, quando nasceram e com quem se ligam as organizações de 2013–2018? | CNPJ (data de abertura; a tabela de **Sócios**, ainda não ingerida, está no mesmo arquivo da Receita); candidaturas ligadas a movimentos no TSE (2016, 2018); bases de eventos de protesto (CEBRAP/Alonso, se acessíveis) | organizações anteriores a 2013, ou com sócios e financiadores só domésticos |
| F4 | Como foi a cooperação internacional da Lava Jato? | acordos de FCPA (justice.gov, sec.gov); pedidos de cooperação; arquivos da Vaza Jato (The Intercept Brasil, Agência Pública); decisões do STF | cooperação só pelos canais formais, nos padrões de outros países |
| F5 | O que está documentado da ação americana em 2025–2026? | Casa Branca (carta das tarifas), OFAC (Magnitsky), USTR (Seção 301), registros FARA (efile.fara.gov), processos no STF/PGR | (é a frente mais documentada; serve para 2026, não para 2018) |
| F6 | Quem financiou a campanha de 2018? | prestação de contas do TSE de 2018; distribuição do FEFC; julgamento das ações sobre disparos em massa (TSE, 2021) | (descritiva) |

**Produto:** uma linha do tempo 2009–2026 em `data/reference/linha_do_tempo.csv` (data,
evento, ator, grau, fonte), que alimenta o relatório e pode virar visualização.

---

## 4. Ordem proposta

Restrição fixa: a previsão v2 do 2º turno sai em **24/10** e o 2º turno é em **25/10**. A
M1b (B1–B4) tem prioridade logo depois.

| Quando | Painel (série E) | Documental (série F) |
|---|---|---|
| **até 16/10** | registrar E0b, E2d, E3c e a aposta da E5; rodar E2b, E4, E5, E7, E2d; revisar a C3 | F5 e F1 (fontes públicas e rápidas) |
| **até 24/10** | ingerir emendas (Portal da Transparência) e prefeitos 2016/2020/2024; módulo de RDD (A5 + E1b); **previsão v2 do 2T** | F2 |
| **depois de 25/10** | **M1b** (B1–B4); depois E1a, E3b, E6 | F3, F4, F6; linha do tempo consolidada |
| **novembro** | relatório: série E + ensaio revisto com os resultados | |

---

## 5. Decisões que dependem de você

1. **Série F:** criar a trilha documental, com a escala de evidência acima?
2. **Registros novos:** E0b, E2d, E3c, E3b (e E9, se houver dados)?
3. **Fusão:** A5 e E1b num só módulo de RDD?
4. **Prioridade:** fenômeno 3 primeiro (está em curso e conversa com o 2º turno) ou
   fenômenos 1 e 2 primeiro (a história de 2018)? A ordem acima intercala os dois.
5. **C3:** renomear os tipos com base nas trajetórias absolutas?
6. **Ensaio:** fica interno até a série E fechar, ou entra no relatório Quarto já agora?
