# data/raw

Cópias imutáveis das fontes originais. **Nunca commitar arquivos daqui no git.**

Cada arquivo entra pelo DVC (ex.: `dvc import-url <url> data/raw/tse/`), que grava um
`.dvc` com URL + hash no git e guarda o conteúdo no cache local e no remoto R2.
Para trazer uma versão nova de uma fonte (ex.: TSE após o 2º turno), use `dvc update`
explicitamente — nunca sobrescreva o arquivo à mão.
