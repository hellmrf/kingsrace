# kingsrace

Análise exploratória de dados sobre as eleições presidenciais no Brasil, 2006–2026:
a geografia da queda de Lula entre 2022 e 2026, as transferências entre o 1º e o
2º turno de 2026 e a série histórica do voto petista.

O plano de pesquisa está em [docs/plano.md](docs/plano.md).

## Setup

Requer [uv](https://docs.astral.sh/uv/) e [just](https://just.systems/).

```sh
just setup     # uv sync + filtro nbstripout no git
just pull      # baixa os dados versionados do remoto R2 (depois de configurado)
just test
```

## Dados: DVC e o remoto R2

Este projeto usa uma grande diversidade de dados públicos oficiais que, somados, ocupam
espaço demais para serem versionados pelo git. Por isso, os arquivos de dados são
gerenciados pelo **DVC** (Data Version Control). O git guarda só pequenos arquivos `.dvc`
e o `dvc.lock`, com a origem e o hash de cada arquivo. O DVC também registra os resultados
de cada análise (métricas, gráficos e experimentos; ver [Resultados](#resultados-métricas-gráficos-e-experimentos)).

O DVC permite reproduzir exatamente cada etapa do trabalho: o download de todos os dados
brutos das fontes oficiais, o pré-processamento e o fluxo completo de análise. Enquanto as
fontes públicas continuarem disponíveis, qualquer pessoa pode reconstruir o projeto
inteiro partindo só dos dados oficiais.

Só que o pré-processamento é caro: baixar as fontes (mais de 10 GB), extrair e processar
consome várias vezes esse volume em disco, banda e tempo, e é uma etapa que não muda.
Por isso, o DVC guarda cada artefato, bruto ou já processado, num **cache remoto**, e
baixa só o que cada etapa precisa. O remoto também protege a reprodutibilidade quando uma
fonte muda: ele guarda a versão exata de cada arquivo usada na análise, identificada pelo
hash, mesmo que o órgão de origem a altere ou a retire do ar.

O remoto do projeto é um bucket privado no Cloudflare R2, já configurado no repositório
(`.dvc/config`). A configuração muda conforme você tenha ou não acesso a ele.

### Com acesso ao remoto do projeto

Com as chaves de acesso ao bucket, configure-as uma vez por máquina e baixe os dados:

```sh
# credenciais só no .dvc/config.local (fora do git)
uv run dvc remote modify --local r2 access_key_id <ACCESS_KEY_ID>
uv run dvc remote modify --local r2 secret_access_key <SECRET_ACCESS_KEY>
just pull
```

O `just pull` sempre termina acusando a falta dos zips de Empresas, Simples e Municípios do
CNPJ (`data/raw/receita/cnpj_*`, ~1,3 GB). Isso é esperado: eles ficam fora do R2 (decisões D7,
D9 e D11). Os de Estabelecimentos (~11 GB) nem ficam no DVC: são baixados, processados e
apagados, com URL e md5 em `data/reference/fontes_receita.csv`. O que a análise usa do CNPJ
já vem pronto pela etapa `receita`.

Para ver o estado do pipeline, prefira `just status` ao `dvc status`: é o mesmo comando sem
as dezenas de avisos de "etapa congelada" que todo `dvc import-url` produz.

### Sem acesso: reconstruir a partir das fontes públicas

Sem as chaves, dá para refazer tudo a partir das fontes oficiais. Se quiser guardar o
resultado num remoto seu (para não repetir o processo em outra máquina), crie um bucket no
R2 com um token de API com permissão *Object Read & Write* e aponte o DVC para ele. Com
`--local`, a configuração fica em `.dvc/config.local` (fora do git) e passa à frente do
remoto do projeto:

```sh
uv run dvc remote add --local -d meu s3://<bucket>/dvc
uv run dvc remote modify --local meu endpointurl https://<ACCOUNT_ID>.r2.cloudflarestorage.com
uv run dvc remote modify --local meu access_key_id <ACCESS_KEY_ID>
uv run dvc remote modify --local meu secret_access_key <SECRET_ACCESS_KEY>
```

Depois, baixe os dados brutos e rode o pipeline:

```sh
# 1. Fontes baixadas por URL (TSE, IBGE, MDS): o DVC baixa de novo da origem
uv run dvc update -R data/raw/tse data/raw/ibge data/raw/mds

# 2. RAIS e SIM vêm por FTP, que o DVC não baixa sozinho: as URLs estão no CSV
tail -n +2 data/reference/fontes_ftp.csv | while IFS=, read -r arquivo url _; do
  curl -fsS --create-dirs -o "$arquivo" "$url"
done
uv run dvc commit -f data/raw/rais/*.dvc data/raw/datasus/sim/*.dvc

# 3. CNPJ: baixa, processa e apaga um zip por vez (~1 h; usa até ~4 GB de RAM)
uv run python -m kingsrace.ingest.receita todos
uv run dvc commit -f receita

# 4. Todo o resto, até os notebooks; e, se configurou um remoto seu, envia para ele
just repro
just push
```

O `dvc update` baixa a versão **atual** de cada fonte. Se uma fonte mudou desde a análise
original, o hash no `.dvc` muda (aparece no `git diff`) e os resultados podem diferir dos
registrados. O mesmo vale para os arquivos do FTP: se o `dvc commit` alterar algum `.dvc`,
o arquivo baixado não é o mesmo que foi usado.

## Site público

As páginas públicas saem pelo GitHub Pages em <https://hellmrf.github.io/kingsrace/>
(decisão D12). A ordem é sempre a mesma:

1. **Pipeline (DVC):** as etapas gravam tabelas em `data/processed/` e as próprias métricas e
   gráficos em `resultados/<etapa>/`.
2. **Notebooks:** a análise em cima do pipeline. A cópia executada fica no git com as
   saídas, em `reports/notebooks/` (D14).
3. **Público:** `src/kingsrace/publica/<página>.py` só lê saídas do DVC e grava os dados da
   página em `site/dados/`. `site/` guarda os templates Jinja e os gráficos em JS.

```sh
just site          # dados do site (dvc repro site_*) e build em _site/
just site-serve    # prévia em http://localhost:8000
```

O merge na `main` publica: o Actions (`.github/workflows/pages.yml`) baixa do R2 só os
dados do site, com uma chave somente de leitura (`R2_ACCESS_KEY_ID`,
`R2_SECRET_ACCESS_KEY` nos secrets do repositório), monta o site e faz o deploy. Antes do
merge, rode `just push` para que os dados do site estejam no R2.

## Estrutura

```
data/
  raw/          fontes originais, imutáveis — versionadas pelo DVC, nunca pelo git
  interim/      intermediários descartáveis
  processed/    saídas do pipeline (dvc repro)
  reference/    tabelas pequenas feitas à mão, versionadas no git
src/kingsrace/  ingest → harmonize → features → models → viz
notebooks/      numerados (01_panorama … 08_mecanismos); saídas removidas no commit
resultados/     métricas e gráficos de cada notebook, registrados pelo DVCLive (D8)
reports/        relatório Quarto; notebooks/ guarda as cópias executadas, com saídas (D14)
site/           site público: templates, estático e dados (gerados pelo DVC)
docs/           plano, decisões, hipóteses, dicionário de dados
tests/          esquemas e reconciliação com totais oficiais
```

## Fluxo de dados

- **Fonte nova:** `uv run dvc import-url <url> data/raw/<fonte>/`. Depois, commit do
  `.dvc` gerado e `just push`.
- **Versão nova de uma fonte** (ex.: TSE após o 2º turno): `uv run dvc update <arquivo>.dvc`.
- **Reconstruir derivados:** `just repro`.

## Resultados: métricas, gráficos e experimentos

Cada notebook é uma etapa do pipeline (`nb_01_panorama` … `nb_08_mecanismos`) e registra,
pelo DVCLive, os números e gráficos de cada hipótese em `resultados/<notebook>/`
(decisão D8). Os nomes começam pelo ID da hipótese: `A1/M3/beta`, `E2a/salto/p`,
`B4/backtest_2022/G0/rmse_pp`; `<ID>/sustenta` é o veredito (0/1) pelo critério registrado.

```sh
just resultados                    # roda os notebooks pendentes; mostra o que mudou desde o commit
just resultados nb_08_mecanismos   # só um notebook (e o que vier antes dele no pipeline)
just compara main                  # métricas e gráficos desta revisão contra a main
uv run dvc plots diff HEAD~3       # gráficos lado a lado (abre dvc_plots/index.html)
uv run dvc exp show -A --only-changed  # tabela de métricas por commit, em todos os commits
uv run dvc pull reports/notebooks  # notebooks executados, com todas as saídas
```

- **No VS Code**, a extensão do DVC mostra as métricas por commit (aba *Experiments*) e os
  gráficos de várias revisões lado a lado (aba *Plots*). As tabelas de coeficientes usam o
  template `.dvc/plots/coeficientes.json`: ponto e IC de 95%, uma cor por revisão.
- **Experimentos** servem só para exploração, com os parâmetros da seção `exploracao` do
  `params.yaml` (ex.: `uv run dvc exp run nb_06_serie -S exploracao.c3_grupos=5`, depois
  `uv run dvc exp show --only-changed`). Um resultado confirmatório é o que está comitado.
- **Rodar um notebook à mão** grava os mesmos arquivos em `resultados/`: serve de rascunho.
  Antes de comitar, `just resultados` (o `dvc status` deve ficar limpo).

Decisões de projeto e cuidados metodológicos em [docs/decisoes.md](docs/decisoes.md).
O andamento e os achados ficam em [docs/diario.md](docs/diario.md).
