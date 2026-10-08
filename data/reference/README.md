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
