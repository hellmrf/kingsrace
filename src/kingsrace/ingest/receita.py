"""CNPJ da Receita Federal: organizações religiosas (E2b) e MEIs (E7a).

Arquivos brutos em data/raw/receita/cnpj_<versão>/ (dvc import-url do compartilhamento
público da Receita). CSVs sem cabeçalho, `;`, latin-1, um por zip. Cada CSV é extraído para
o disco já convertido para UTF-8 (`csv_extraido`), lido pelo DuckDB e apagado:

- a extensão `zipfs` do DuckDB descomprime o arquivo inteiro na memória (7 GB num zip de
  Estabelecimentos), o que derruba uma máquina de 8 GB;
- o latin-1 nativo do DuckDB recusa bytes 0x80–0x9F, que aparecem em alguns registros (0x8F
  em Estabelecimentos0 de 2026-09); o ISO_8859_1 da extensão `encodings` aceita, mas é ~15x
  mais lento. O latin-1 do Python aceita os 256 bytes.

O cadastro é um retrato da data de geração: CNPJs baixados continuam nele, com a data da
situação atual.

Os brutos não ficam no disco nem no R2 (decisões D7): `python -m kingsrace.ingest.receita
todos` baixa cada zip de Estabelecimentos, extrai dele uma parte pequena e apaga a cópia
local (o `.dvc` guarda URL e hash). Saídas em data/interim/receita/:

- `religiosas.parquet`: estabelecimentos (matriz e filiais) com CNAE principal 9491-0/00,
  com razão social e natureza jurídica da empresa e a data em que deixaram de existir;
- `mei_estoque.parquet`: MEIs ativos em 31/12 de cada ano, por município da matriz;
- `municipios_receita.parquet`: código da Receita, nome e UF (a tabela da Receita não tem UF).
"""

import os
import subprocess
import sys
import zipfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import duckdb
import yaml

from kingsrace import paths

VERSAO = "2026-09"
URL = (
    "https://arquivos.receitafederal.gov.br/public.php/dav/files/gn672Ad4CF8N6TK/"
    "Dados/Cadastros/CNPJ/{versao}/{arquivo}"
)
CNAE_RELIGIOSA = "9491000"
# situação cadastral que encerra o CNPJ na data da situação: 1 nula, 4 inapta, 8 baixada
SITUACOES_FIM = (1, 4, 8)
ANOS_MEI = range(2009, 2027)  # o MEI começou em julho de 2009
MEMORIA = os.environ.get("KINGSRACE_DUCKDB_MEMORIA", "2GB")
THREADS = int(os.environ.get("KINGSRACE_DUCKDB_THREADS", "4"))

ESTABELECIMENTOS = [
    "cnpj_basico",
    "cnpj_ordem",
    "cnpj_dv",
    "matriz_filial",
    "nome_fantasia",
    "situacao",
    "data_situacao",
    "motivo_situacao",
    "cidade_exterior",
    "pais",
    "data_inicio",
    "cnae_principal",
    "cnae_secundaria",
    "tipo_logradouro",
    "logradouro",
    "numero",
    "complemento",
    "bairro",
    "cep",
    "uf",
    "municipio",
    "ddd1",
    "telefone1",
    "ddd2",
    "telefone2",
    "ddd_fax",
    "fax",
    "email",
    "situacao_especial",
    "data_situacao_especial",
]
EMPRESAS = [
    "cnpj_basico",
    "razao_social",
    "natureza_juridica",
    "qualificacao_responsavel",
    "capital_social",
    "porte",
    "ente_federativo",
]
SIMPLES = [
    "cnpj_basico",
    "opcao_simples",
    "data_opcao_simples",
    "data_exclusao_simples",
    "opcao_mei",
    "data_opcao_mei",
    "data_exclusao_mei",
]


def data(col: str) -> str:
    """Expressão SQL que converte AAAAMMDD em DATE (zeros e vazios viram NULL)."""
    return f"try_strptime(nullif(nullif({col}, '00000000'), '0'), '%Y%m%d')::DATE"


def fim(situacao: str, data_situacao: str) -> str:
    """Data em que o CNPJ deixou de existir (NULL se ativo, suspenso ou sem data)."""
    return f"CASE WHEN try_cast({situacao} AS INTEGER) IN {SITUACOES_FIM} THEN {data_situacao} END"


def conexao() -> duckdb.DuckDBPyConnection:
    """DuckDB com memória limitada: o padrão (80% da RAM) derruba uma máquina de 8 GB."""
    con = duckdb.connect()
    con.sql("SET enable_progress_bar=false")
    con.sql(f"SET memory_limit='{MEMORIA}'")
    con.sql(f"SET threads={THREADS}")
    con.sql("SET preserve_insertion_order=false")
    con.sql(f"SET temp_directory='{paths.INTERIM / 'receita' / 'duckdb_tmp'}'")
    return con


@contextmanager
def csv_extraido(zip_path: Path) -> Iterator[Path]:
    """Extrai o único CSV do zip, em blocos e já em UTF-8, e o apaga ao sair."""
    destino = paths.INTERIM / "receita" / "partes" / f"_{zip_path.stem}.csv"
    with zipfile.ZipFile(zip_path) as z:
        (membro,) = z.namelist()
        with z.open(membro) as origem, destino.open("wb") as saida:
            while bloco := origem.read(1 << 24):
                saida.write(bloco.decode("latin-1").encode())
    try:
        yield destino
    finally:
        destino.unlink(missing_ok=True)


def le_csv(csv: Path, colunas: list[str]) -> str:
    """`read_csv` de um CSV da Receita extraído por `csv_extraido`.

    Sequencial: com `strict_mode=false` (aspas soltas em alguns campos) o leitor paralelo do
    DuckDB recusa os arquivos da Receita. Escape fixo em `"`: o detector às vezes escolhe `'`
    e então um campo como `"SABESP'"` engole os seguintes.
    """
    nomes = ", ".join(f"'{c}'" for c in colunas)
    return (
        f"read_csv('{csv}', delim=';', quote='\"', escape='\"', header=false, "
        f"all_varchar=true, names=[{nomes}], strict_mode=false, parallel=false)"
    )


def pastas(versao: str) -> tuple[Path, Path]:
    raw = paths.RAW / "receita" / f"cnpj_{versao}"
    saida = paths.INTERIM / "receita"
    (saida / "partes").mkdir(parents=True, exist_ok=True)
    return raw, saida


def prepara_mei(versao: str = VERSAO) -> None:
    """MEIs do Simples (CNPJ básico, opção e exclusão) → partes/mei_simples.parquet."""
    raw, saida = pastas(versao)
    with csv_extraido(raw / "Simples.zip") as csv:
        conexao().sql(f"""
            COPY (
                SELECT cnpj_basico,
                       {data("data_opcao_mei")} AS opcao,
                       {data("data_exclusao_mei")} AS exclusao
                FROM {le_csv(csv, SIMPLES)}
                WHERE {data("data_opcao_mei")} IS NOT NULL
            ) TO '{saida / "partes" / "mei_simples.parquet"}' (FORMAT parquet)
        """)


def processa_estabelecimentos(i: int, versao: str = VERSAO) -> None:
    """Extrai de Estabelecimentos<i>.zip as igrejas, o estoque de MEIs e a UF dos municípios."""
    raw, _ = pastas(versao)
    with csv_extraido(raw / f"Estabelecimentos{i}.zip") as csv:
        _processa_estabelecimentos(i, csv)


def _processa_estabelecimentos(i: int, csv: Path) -> None:
    partes = paths.INTERIM / "receita" / "partes"
    con = conexao()
    con.sql(f"CREATE VIEW mei AS SELECT * FROM '{partes / 'mei_simples.parquet'}'")
    con.sql(f"CREATE VIEW e AS SELECT * FROM {le_csv(csv, ESTABELECIMENTOS)}")
    con.sql(f"""
        COPY (
            SELECT cnpj_basico, cnpj_ordem, matriz_filial, nome_fantasia, situacao,
                   {data("data_situacao")} AS data_situacao,
                   {data("data_inicio")} AS data_inicio,
                   uf, municipio
            FROM e WHERE cnae_principal = '{CNAE_RELIGIOSA}'
        ) TO '{partes / f"religiosas_{i}.parquet"}' (FORMAT parquet)
    """)
    anos = ", ".join(str(a) for a in ANOS_MEI)
    con.sql(f"""
        COPY (
            WITH m AS (
                SELECT e.uf, e.municipio, mei.opcao,
                       least(mei.exclusao, {fim("e.situacao", data("e.data_situacao"))}) AS fim
                FROM e JOIN mei USING (cnpj_basico)
                WHERE e.matriz_filial = '1'
            )
            SELECT uf, municipio, ano, count(*) AS meis
            FROM m, (SELECT unnest([{anos}]) AS ano) a
            WHERE m.opcao <= make_date(ano, 12, 31)
              AND (m.fim IS NULL OR m.fim > make_date(ano, 12, 31))
            GROUP BY ALL
        ) TO '{partes / f"mei_estoque_{i}.parquet"}' (FORMAT parquet)
    """)
    con.sql(f"""
        COPY (SELECT municipio, uf, count(*) AS n FROM e GROUP BY ALL)
        TO '{partes / f"ufs_{i}.parquet"}' (FORMAT parquet)
    """)


def finaliza(versao: str = VERSAO) -> None:
    """Junta as partes, acrescenta a razão social e monta a tabela de municípios."""
    raw, saida = pastas(versao)
    partes = saida / "partes"
    con = conexao()
    con.sql(f"CREATE TABLE religiosas AS SELECT * FROM '{partes}/religiosas_*.parquet'")
    con.sql(
        "CREATE TABLE empresas "
        "(cnpj_basico VARCHAR, razao_social VARCHAR, natureza_juridica VARCHAR)"
    )
    for i in range(10):
        with csv_extraido(raw / f"Empresas{i}.zip") as csv:
            con.sql(f"""
                INSERT INTO empresas
                SELECT cnpj_basico, razao_social, natureza_juridica
                FROM {le_csv(csv, EMPRESAS)} SEMI JOIN religiosas USING (cnpj_basico)
            """)
    con.sql(f"""
        COPY (
            SELECT r.*, e.razao_social, e.natureza_juridica,
                   {fim("r.situacao", "r.data_situacao")} AS data_fim
            FROM religiosas r LEFT JOIN empresas e USING (cnpj_basico)
        ) TO '{saida / "religiosas.parquet"}' (FORMAT parquet, COMPRESSION zstd)
    """)
    con.sql(f"""
        COPY (
            SELECT uf, municipio, ano, sum(meis)::BIGINT AS meis
            FROM '{partes}/mei_estoque_*.parquet' GROUP BY ALL ORDER BY ALL
        ) TO '{saida / "mei_estoque.parquet"}' (FORMAT parquet)
    """)
    with csv_extraido(raw / "Municipios.zip") as csv:
        con.sql(f"""
            COPY (
                SELECT m.codigo AS municipio, m.nome, u.uf
                FROM {le_csv(csv, ["codigo", "nome"])} m
                LEFT JOIN (
                    SELECT municipio, arg_max(uf, n) AS uf
                    FROM (SELECT municipio, uf, sum(n) AS n
                          FROM '{partes}/ufs_*.parquet' GROUP BY ALL)
                    GROUP BY municipio
                ) u ON u.municipio = m.codigo
                ORDER BY m.codigo
            ) TO '{saida / "municipios_receita.parquet"}' (FORMAT parquet)
        """)


def _dvc(*args: str) -> None:
    subprocess.run(["dvc", *args], check=True, cwd=paths.ROOT)


def baixa(arquivo: str, versao: str = VERSAO) -> Path:
    """`dvc import-url` do arquivo, marcado para não ir ao R2 (`push: false`)."""
    raw, _ = pastas(versao)
    _dvc("import-url", "--force", "-q", URL.format(versao=versao, arquivo=arquivo), str(raw) + "/")
    dvc_file = raw / f"{arquivo}.dvc"
    meta = yaml.safe_load(dvc_file.read_text())
    meta["outs"][0]["push"] = False
    dvc_file.write_text(yaml.safe_dump(meta, sort_keys=False, allow_unicode=True))
    _dvc("commit", "-f", "-q", str(dvc_file))  # recalcula o md5 do .dvc, que mudou acima
    return raw / arquivo


def apaga_local(arquivo: Path) -> None:
    """Apaga o arquivo e o objeto do cache do DVC (fica só o `.dvc`, com URL e hash)."""
    md5 = yaml.safe_load(Path(f"{arquivo}.dvc").read_text())["outs"][0]["md5"]
    cache = paths.ROOT / ".dvc" / "cache" / "files" / "md5" / md5[:2] / md5[2:]
    arquivo.unlink(missing_ok=True)
    cache.unlink(missing_ok=True)


def todos(versao: str = VERSAO) -> None:
    """Baixa, processa e apaga um zip de Estabelecimentos por vez; depois junta tudo."""
    raw, saida = pastas(versao)
    for arquivo in ("Simples.zip", "Municipios.zip", *(f"Empresas{i}.zip" for i in range(10))):
        if not (raw / arquivo).exists():
            baixa(arquivo, versao)
    if not (saida / "partes" / "mei_simples.parquet").exists():
        prepara_mei(versao)
    for i in range(10):
        if (saida / "partes" / f"ufs_{i}.parquet").exists():
            continue  # já processado (permite retomar depois de uma falha)
        zip_path = raw / f"Estabelecimentos{i}.zip"
        if not zip_path.exists():  # sobra de uma execução que falhou no processamento
            baixa(zip_path.name, versao)
        processa_estabelecimentos(i, versao)
        apaga_local(zip_path)
        print(f"Estabelecimentos{i} processado", flush=True)
    finaliza(versao)


if __name__ == "__main__":
    {"todos": todos, "finaliza": finaliza, "mei": prepara_mei}[sys.argv[1]]()
