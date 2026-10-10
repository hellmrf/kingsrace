# data/reference

Tabelas pequenas, feitas ou curadas à mão, versionadas diretamente no git
(ex.: `candidatos.csv`, correspondências manuais, previsão congelada do 2T).
Regra prática: se passar de ~1 MB ou puder ser baixado de uma fonte, não é daqui.

| Tabela | Conteúdo |
|---|---|
| `candidatos.csv` | papel de cada número especial por ano: `pt`, `adversario`, `anulado` (votos que o TSE não conta como válidos). Brancos (95) e nulos (96) são fixos no código; demais números = `outro`. |
| `municipios_overrides.csv` | correspondências TSE→IBGE que o casamento por UF + nome não resolve, com o motivo. |
| `amc.csv` | municípios agrupados em áreas mínimas comparáveis (`amc_id` ≥ 9000000); os não listados usam o próprio código IBGE. |
| `totais_oficiais.csv` | totais nacionais por candidato e turno, usados no teste de reconciliação. |
| `denominacoes.csv` | regras (regex sobre a razão social, por prioridade) que classificam organizações religiosas do CNPJ em grupo e denominação (E2b). Commitada antes de cruzar com o voto. |
| `municipios_overrides_receita.csv` | correspondências Receita→IBGE que o casamento por UF + nome não resolve. |
| `fontes_ftp.csv` | URL de origem dos brutos baixados por FTP (RAIS, SIM), que o `dvc import-url` não suporta; o hash fica no `.dvc` de cada arquivo. |
| `fontes_receita.csv` | versão, URL, md5 e tamanho dos zips de Estabelecimentos do CNPJ, que são apagados depois de processados e não ficam no DVC; a ingestão para se um novo download não bater com o md5 anotado. |
| `pesquisas_2026.csv` | últimas pesquisas de cada instituto antes do 1º turno de 2026 e a do 2º turno usada na previsão v1. |
| `pesquisas_serie_2025_2026.csv` | 2º turno simulado Lula × Flávio, jun/2025 a out/2026, da Wikipédia (pt), com ~20% das linhas conferidas na fonte (`conferido`); linhas `divergente` já trazem o valor da fonte. |
| `aprovacao_lula_2025_2026.csv` | aprovação do trabalho de Lula pela Quaest, jan/2025 a out/2026, lida dos relatórios do instituto. A partir de ago/2026 a pergunta muda um pouco (coluna `pergunta`). |
| `linha_do_tempo.csv` | eventos de 2006 a 2026 com faixa (`eua`, `brasil`, `urnas`), grau de evidência (`documentado`, `reportado`, `alegado`, `refutado`), fonte e `conferido`. Alimenta a página `reports/conjuntura`. |
| `grupos_terceiros.csv` | grupo de cada candidato eliminado em 2022 e 2026 (Tebet, Ciro, Cury, Renan, Caiado, Zema, direita, esquerda), para o painel por seção e a inferência ecológica da série G. |
| `institutos.csv` | nome de cada instituto como aparece nas tabelas de pesquisas → nome canônico (a correção pelo viés do 1º turno casa por ele). |
| `pesquisas_2t_cruzamentos.csv` | voto no 2º turno por voto no 1º turno (`grupo_1t`: lula, flavio, cury, renan, caiado, zema, outros, branco_nulo, nao_votou), em % do grupo, com fonte e `conferido`. Vazia até algum instituto publicar. |

**Para acrescentar uma pesquisa de 2º turno:** uma linha em `pesquisas_serie_2025_2026.csv`
(fim de campo, amostra, Lula, Flávio, brancos/nulos/indecisos, `base` total ou válidos, fonte,
url, data da consulta e `conferido`). Se o instituto for novo, também em `institutos.csv`.
Depois, `just pesquisas`, que refaz a G6, os dados do site e o build. Com o commit, a
mudança fica no histórico das métricas (`dvc metrics diff`).
| `evidencias_mobilizacao.csv` | estudos sobre o que move o comparecimento e o voto (G7), com o achado em uma frase, a referência, o grau de evidência e `conferido`. |
