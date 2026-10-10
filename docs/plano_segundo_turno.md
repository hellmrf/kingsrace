# Plano de ação: o caminho do 2º turno (série G), a página "Como virar" e o site

**Aprovado em 2026-10-10.** As hipóteses da série G estão registradas em
[hipoteses.md](hipoteses.md#série-g-o-caminho-do-2º-turno-de-2026); este documento traz o
porquê, a ordem do trabalho e a estrutura do site.

## Contexto

Em 10/10 faltam 15 dias para o 2º turno (dom 25/10). A pergunta é, com os dados, **o que
mais pesa e o que a militância, a direção e as campanhas podem fazer para virar**. O produto
é um documento público já, em camadas para o público, a militância e a direção, servido
pelo **GitHub Pages** e não pelos artifacts do claude.ai. O código precisa ficar organizado
para crescer sem virar macarrão. A pergunta acadêmica (o
mecanismo de 2018 e 2026) fica para depois de 25/10.

Ponto de partida, com o painel atual (1º turno de 2026):

- Flávio tem 56,10 mi de votos e Lula 53,88 mi: **2,22 mi de diferença**.
- Os eliminados somam 9,3 mi, quase todos à direita (Cury 3,45, Renan 2,68, Caiado ~2,6,
  Zema ~0,3). Os nulos são 3,67 mi e a abstenção, 32,9 mi.
- **Em 2022, do 1º para o 2º turno, Bolsonaro ganhou 7,1 mi e Lula 3,1 mi**, e o comparecimento
  quase não mudou (+0,56 mi). Em 2006 foi o contrário: Lula +11,6 mi e Alckmin −2,4 mi.
- Só com transferências, Lula precisaria de ~64/36 dos válidos dos eliminados, o que é
  improvável. A virada depende da soma de três caminhos: transferência, comparecimento e
  conversão (quem troca Flávio por Lula vale 2 na margem). O trabalho é **medir quanto cada
  caminho pode render e onde estão esses votos**.

Decisões tomadas:

- uma página nova, em camadas;
- mapa por local de votação nas cidades grandes (a v1 sai por município);
- GitHub Pro, com o Pages saindo do próprio repo (privado) pelo Actions;
- build em Python + Jinja, sem Node.

## Como trabalhar

- Branch `feat/segundo-turno` a partir da `main`. Da `heliton/checkpoint-1` entram só as
  tabelas de referência que a página usa: `pesquisas_serie_2025_2026.csv`,
  `aprovacao_lula_2025_2026.csv`, `linha_do_tempo.csv` e as linhas delas no README. O
  conteúdo é idêntico, então o merge futuro da checkpoint não dá conflito.
- O site publica a cada merge na `main`, então cada versão da página entra por PR.
- **Registrar a série G em `docs/hipoteses.md` antes de rodar G2–G5.** Ela é quase toda
  descritiva. O registro diz o que se calcula, por qual método, e como cada faixa será
  conferida depois de 25/10 pela B1/B2. Não mexe na B4: a previsão v2 continua em 24/10.
- Ambiente: `~/.local/bin/uv`. Tudo o que for pesado roda em
  `systemd-run --user --scope -q -p MemoryMax=4G -p MemorySwapMax=0`, um trabalho de cada vez.
  Usar `dvc exp run --temp`.

## Análises (série G)

Cada uma responde "quantos votos, onde e com que evidência".

| ID | Pergunta | Dados | Método |
|---|---|---|---|
| **G1** Aritmética | Que combinações de caminhos fecham 2,22 mi (mais uma margem para o erro das pesquisas)? O que aconteceu entre os turnos em 2006–2022? | `painel_amc`, `votos_municipio` (prontos) | Contas nacionais e por UF; a página traz uma calculadora em JS |
| **G2** Transferências | Para onde foram, do 1º para o 2º turno de 2022, os votos de Ciro, Tebet, outros, brancos/nulos e abstenção? Que faixa isso dá para Cury, Renan e Caiado? | seção 2022 (votos prontos; aptos/comparecimento a ingerir) + cruzamentos das pesquisas de 2T de 2026 (voto no 2T por voto no 1T) | Inferência ecológica por seção (mesmo eleitorado nos dois turnos): mínimos quadrados com restrição (linhas somam 1, valores entre 0 e 1) por UF, IC por bootstrap de municípios. 2006 e 2014 se der tempo |
| **G3** Comparecimento | Onde estão os abstencionistas em lugares de Lula, e quantos votos líquidos rende cada ponto de comparecimento? Onde estão os que votaram no 2T de 2022 e não voltaram? Onde subiu o comparecimento no 2T de 2022, e a quem favoreceu? | detalhe por seção 2022/2026, locais 2026 | Reserva líquida = abstencionistas × (2p − 1), por seção, local, município e UF. Votantes perdidos = comparecimento 2T 2022 − 1T 2026, por município e por local (casando município + zona + nº do local, conferindo o nome) |
| **G4** Conversão | Onde estão, em votos absolutos, os eleitores que Lula teve no 2T de 2022 e não teve no 1T de 2026? Que perfil têm esses lugares? | `painel_amc`, covariáveis (prontos) | LMDI 2T 2022 → 1T 2026 (`features/decomposicao.decompoe_votos`). A parcela "fatia" é o alvo de persuasão, por UF × tamanho |
| **G5** Quem se moveu no 2T | Que tipo de lugar andou para Lula entre os turnos de 2022 (e de 2006)? | painel + covariáveis (prontos) | Δ logit 1T→2T com efeito fixo de UF (pyfixest), exploratório |
| **G6** Pesquisas | Onde está a corrida agora, com o erro do 1º turno descontado? O que dizem os cruzamentos por voto no 1T? | pesquisas de 2T desde 6/10, com fonte e `conferido` | Tendência + faixa de erro. Não é previsão nova; alimenta a v2 da B4 |
| **G7** O que funciona | O que está documentado sobre mobilização no dia (transporte gratuito em 2022, bloqueios da PRF, porta a porta) e sobre o 2T de 2006? | pesquisa documental | Selo de evidência (documentado, reportado, alegado) e fonte conferida |

**Síntese, que responde "o que mais pesa":** uma tabela de alavancas, em que cada linha traz
o tamanho do estoque, a taxa plausível (faixa e de onde vem), o ganho líquido em votos
(faixa), onde está e o que fazer. As recomendações levam selo de inferência: os dados dizem
onde e quanto, não qual mensagem.

## O site: estrutura contra o macarrão

**Três camadas, cada uma com uma só responsabilidade (vira a decisão D12 em
`docs/decisoes.md`):**

1. **Análise** (`notebooks/`, `models/`, `features/`): produz `data/processed/` e
   `resultados/`. Nunca escreve no site.
2. **Dados do site** (`src/kingsrace/publica/<página>.py`):
   - só lê saídas do DVC (`processed/`, `resultados/`) e `reference/`, sem fazer conta
     nova, nem "descritiva": **todo número e todo gráfico da página é antes uma saída
     declarada no `dvc.yaml`** (métrica, gráfico ou tabela de uma etapa), com o mesmo nome;
   - a ordem é pipeline (o centro) → notebook (análise) → público;
   - grava JSON e CSV determinísticos em `site/dados/<página>/`;
   - confere os totais contra `totais_oficiais.csv`.
   - É uma etapa do DVC, e as saídas vão ao R2.
3. **Apresentação** (`site/`):
   - templates Jinja com `StrictUndefined`: um número que falta derruba o build, em vez de
     sair "—";
   - nenhum número digitado no HTML; o texto mora só nos templates;
   - os números entram no HTML na hora do build (a página funciona sem JS e gera prévia com
     Open Graph no WhatsApp);
   - os gráficos são módulos JS puros, `desenha(el, dados, opções)`, sem variáveis globais e
     com as cores tiradas dos tokens CSS.

```text
site/
  modelos/base.html.j2            # head (OG, tema claro/escuro), cabeçalho, rodapé (commit + data dos dados)
  modelos/macros.html.j2          # selo de evidência, figura com fonte, número, alavanca
  paginas/index.html.j2           # capa
  paginas/segundo-turno/index.html.j2
  estatico/css/{tema,componentes}.css     # tokens extraídos da página conjuntura
  estatico/js/formato.js                  # número BR, pp, mi
  estatico/js/graficos/{barras,linhas,mapa,pontos}.js
  estatico/js/componentes/{calculadora,busca,tabela}.js
  estatico/vendor/                        # d3 e topojson-client com versão fixa, servidos do próprio site
  dados/                                  # gerado pelo DVC; fora do git
src/kingsrace/publica/
  comum.py          # metricas(nb), br(), pp(), mi(), confere_totais(), grava_json()
  segundo_turno.py  # dados da página: funções puras + executa()
  geo.py            # malha municipal simplificada (API de malhas do IBGE → TopoJSON)
  build.py          # Jinja → _site/; copia estatico/ e dados/
  __main__.py       # python -m kingsrace.publica {dados <página> | build | serve}
.github/workflows/pages.yml
tests/test_publica.py
```

- `reports/conjuntura/` segue como artifact privado do grupo (votação e comentários
  dependem do runtime do claude.ai). O gerador dele migra para
  `publica/conjuntura.py` depois de 25/10, e daí a página reaproveita o mesmo `estatico/`.
- Os locais de votação vão em listas com endereço e um link "abrir no mapa" (lat/long), por
  UF, em CSV para baixar. O mapa de pontos sai só nas cidades grandes, sem camada de mapa
  externa.

**Deploy (`.github/workflows/pages.yml`):**

- Disparo: push na `main` que toque `site/`, `src/kingsrace/publica/` ou `dvc.lock`; também
  `workflow_dispatch`.
- Passos:
  1. checkout;
  2. `astral-sh/setup-uv` com versão fixa;
  3. `uv sync --frozen`;
  4. credenciais do R2 via `dvc remote modify --local`, a partir dos secrets;
  5. `uv run dvc pull site_segundo_turno site_geo` (só os dados do site);
  6. `uv run python -m kingsrace.publica build`;
  7. `actions/upload-pages-artifact` + `actions/deploy-pages`.
- URL: `hellmrf.github.io/kingsrace`.
- **Configuração manual, uma vez só** (nada é feito no GitHub ou no Cloudflare sem
  confirmação):
  - criar no R2 um token **só de leitura** do bucket;
  - gravar os secrets `R2_ACCESS_KEY_ID` e `R2_SECRET_ACCESS_KEY`;
  - em Settings → Pages, pôr Source = GitHub Actions.
- Local:
  - `just site` = `dvc repro site_segundo_turno` + build;
  - `just site-serve` = prévia em `localhost`;
  - entram no `pyproject.toml`: `jinja2` e um grupo `site`.

## Arquivos da análise

**Ingestão (DVC):**

- `dvc import-url` de três arquivos do TSE, já conferidos no ar em 10/10:
  - `detalhe_votacao_secao_2022.zip` (244 MB)
  - `detalhe_votacao_secao_2026.zip` (177 MB)
  - `eleitorado_local_votacao_2026.zip` (176 MB, com nome, endereço e lat/long)
- A malha municipal do IBGE também entra, para a etapa `site_geo`.
- `ingest/tse.py`: esquemas `DETALHE_SECAO` e `LOCAL_VOTACAO`, reusando
  `csv_zip_para_parquet`.
- `features/secao.py` (novo): monta `painel_secao.parquet` e `painel_local.parquet` (o
  `painel_local` que o `plano.md` já previa). Reusa `classifica_votos` e `adiciona_metricas`
  de `features/painel.py`.
- `dvc.yaml`: etapas `converte_secao` (foreach 2022, 2026), `locais`, `painel_secao`,
  `nb_09_segundo_turno`, `site_geo` e `site_segundo_turno`.

**Modelos e notebook:**

- `models/inferencia_ecologica.py` (novo): matriz de transição com restrição, mais o
  bootstrap. Depois de 25/10 serve direto para a B1.
- `notebooks/09_segundo_turno.ipynb`: G1–G6, com métricas `G*/...` pelo DVCLive (funções de
  `resultados.py`). Reusa `features/base.base_variacao` e `models/event_study.ajusta`.

**Referência e docs:**

- `pesquisas_2026.csv`: novas linhas `turno=2`, o formato que a v2 da B4 lê.
- `pesquisas_2t_cruzamentos.csv` (novo): voto no 2T por voto no 1T, por instituto.
- `linha_do_tempo.csv`: os itens da G7.
- `README.md` da raiz: seção "Site".
- `docs/hipoteses.md`: série G.
- `docs/decisoes.md`:
  - D12, as camadas do site;
  - o método da IE;
  - o casamento de locais entre 2022 e 2026.
- `docs/diario.md`.

## Roteiro

| Quando | Entrega |
|---|---|
| **sáb 10 – dom 11** | Registro da série G. G1, G4 e G5. Coleta da G6. Esqueleto do site (`publica/`, templates, `tema.css`, workflow) com uma página de teste publicada pelo Actions. Ingestão dos três arquivos do TSE, em sequência e no cgroup |
| **seg 12** | **PR da página v1, por município:** topo público, aritmética e calculadora, lição de 2006/2022, ex-eleitores, reserva de comparecimento por município, pesquisas, tabela de alavancas preliminar. Merge = publicação. Se atrasar, sai na terça, sem cortar a verificação |
| **ter 13 – qui 15** | G2 (IE por seção, 2022). G3 por local de votação. Listas por UF e local. G7. **PR da v2** |
| **sex 16 – sex 23** | Atualizações com pesquisas novas. Em 24/10, a previsão v2 da B4 (já registrada) |
| **depois de 25/10** | B1–B4 com o mesmo módulo de IE, conferindo as faixas da G2. Migração da página conjuntura para o site. A pergunta 2 volta (série E: RDD de prefeitos e emendas, E3b; série F) |

Sobre a pergunta 2, um ponto a assentar antes de retomá-la: nos resultados comitados, o
afastamento dos pequenos aparece em 2018→2022 (+0,036) e em 2022→2026. Já 2014→2018 foi o
choque *urbano*. Os dados mostram, então, um processo contínuo desde 2018 mais a pegada
religiosa persistente, e não dois pontos fora da curva.

## Verificação

- **Reconciliação:**
  - seções = munzona = total oficial, por UF, candidato e turno;
  - aptos e comparecimento do detalhe por seção = munzona.
  - Testes em `tests/`, no padrão dos atuais.
- **IE:**
  - teste sintético (matriz conhecida → recuperada dentro do IC);
  - os totais do 2T de 2022 implicados batem com os oficiais;
  - as linhas somam 1.
- **LMDI:** os componentes somam a variação.
- **Site (`tests/test_publica.py`):**
  - `br`, `pp` e `mi` formatam certo;
  - o build com dados de exemplo roda sem erro de `StrictUndefined`;
  - os links internos e os arquivos de `dados/` referenciados existem;
  - `grava_json` é determinístico (mesmo hash em duas execuções).
- **Antes de cada merge:**
  - `just test`, `just repro` e `just status` limpos;
  - `just site-serve` aberto no navegador em largura de celular, nos temas claro e escuro, e
    com o JS desligado;
  - a calculadora conferida com a G1 à mão.
- **Depois do deploy:**
  - o run do Actions sai verde;
  - a página no ar mostra o commit e a data dos dados no rodapé;
  - a prévia do link aparece num teste de Open Graph.
