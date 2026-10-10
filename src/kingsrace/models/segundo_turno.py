"""Tabelas da série G (o caminho do 2º turno de 2026), registrada em docs/hipoteses.md.

Grava em data/processed/segundo_turno/:

- `transicao_2022.parquet`: matriz 1º → 2º turno de 2022 por UF e para o país (G2), com IC
  de 95% por bootstrap de municípios; `transicao_2022_replicas.parquet` guarda as réplicas,
  para os cenários do notebook herdarem a incerteza;
- `estoques_2026.parquet`: votos de cada origem no 1º turno de 2026, por UF (G1);
- `reserva_local.parquet` e `reserva_municipio.parquet`: abstenção, fatia de Lula, reserva
  líquida e rendimento por ponto de comparecimento no 1º turno de 2026 (G3), com os
  votantes perdidos desde o 2º turno de 2022;
- `ex_eleitores_amc.parquet`: LMDI dos votos de Lula do 2º turno de 2022 ao 1º de 2026 (G4).

E registra em resultados/segundo_turno/ (D12) as métricas `G*` e os dados de cada gráfico
(`plots/custom/G*.json`), que o `dvc plots` desenha e a página pública redesenha.

Uso: python -m kingsrace.models.segundo_turno
"""

from __future__ import annotations

import tempfile

import numpy as np
import polars as pl
import pyfixest as pf

from kingsrace import paths, resultados
from kingsrace.features.base import base_variacao
from kingsrace.features.decomposicao import decompoe_votos
from kingsrace.features.secao import casa_locais
from kingsrace.ingest.tse import CANDIDATO, csv_zip_para_parquet
from kingsrace.models.inferencia_ecologica import agrega, estima, grams_por_grupo

SAIDA = paths.PROCESSED / "segundo_turno"
CHAVE = ["uf", "cd_tse", "zona", "secao"]

# Origens do 1º turno e destinos do 2º; bn = brancos + nulos, abst = quem não votou
# (abstenção + seção não instalada, isto é, aptos − comparecimento).
ORIGENS_2022 = ["pt", "adv", "tebet", "ciro", "direita", "esquerda", "bn", "abst"]
ORIGENS_2026 = ["pt", "adv", "cury", "renan", "caiado", "zema", "direita", "esquerda", "bn", "abst"]
DESTINOS = ["pt", "adv", "bn", "abst"]


def com_origens(secao: pl.DataFrame) -> pl.DataFrame:
    """Renomeia `votos_x` para `x` e acrescenta `bn` e `abst`."""
    return secao.rename(
        {c: c.removeprefix("votos_") for c in secao.columns if c.startswith("votos_")}
    ).with_columns(
        bn=pl.col("brancos") + pl.col("nulos"),
        abst=pl.col("aptos") - pl.col("comparecimento"),
    )


def pares_2022(painel_secao: pl.DataFrame) -> pl.DataFrame:
    """Seções de 2022 casadas entre os turnos: origens com sufixo _1, destinos com _2."""
    s = com_origens(painel_secao.filter(pl.col("ano") == 2022))
    t1 = s.filter(pl.col("turno") == 1).select(
        *CHAVE, "cd_ibge", "aptos", *(pl.col(c).alias(f"{c}_1") for c in ORIGENS_2022)
    )
    t2 = s.filter(pl.col("turno") == 2).select(
        *CHAVE, *(pl.col(c).alias(f"{c}_2") for c in DESTINOS)
    )
    return t1.join(t2, on=CHAVE, how="inner")


def transicao(pares: pl.DataFrame, reps: int, semente: int) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Matriz por UF e nacional (BR), em formato longo, e as réplicas do bootstrap.

    O nacional agrega as UFs pelos votos de cada origem, réplica a réplica (a mesma réplica r
    de cada UF entra na réplica r do país; as UFs são reamostradas de forma independente).
    """
    origens = [f"{c}_1" for c in ORIGENS_2022]
    destinos = [f"{c}_2" for c in DESTINOS]
    pontos, todas, ns = {}, {}, {}
    for (uf,), parte in pares.sort("uf").group_by("uf", maintain_order=True):
        g = grams_por_grupo(parte, origens, destinos, "cd_ibge")
        pontos[uf], todas[uf], ns[uf] = estima(g, reps=reps, semente=semente)
    ufs = list(pontos)
    pontos["BR"] = agrega([pontos[u] for u in ufs], [ns[u] for u in ufs])
    todas["BR"] = np.stack(
        [agrega([todas[u][r] for u in ufs], [ns[u] for u in ufs]) for r in range(reps)]
    )
    ns["BR"] = sum(ns[u] for u in ufs)

    linhas, replicas = [], []
    for uf, b in pontos.items():
        inf, sup = np.percentile(todas[uf], [2.5, 97.5], axis=0)
        for i, o in enumerate(ORIGENS_2022):
            for j, d in enumerate(DESTINOS):
                linhas.append(
                    {"uf": uf, "origem": o, "destino": d, "b": b[i, j],
                     "ic_inf": inf[i, j], "ic_sup": sup[i, j], "n_origem": ns[uf][i]}
                )  # fmt: skip
        r, i, j = np.indices(todas[uf].shape).reshape(3, -1)
        replicas.append(
            pl.DataFrame(
                {
                    "uf": uf,
                    "rep": r,
                    "origem": np.array(ORIGENS_2022)[i],
                    "destino": np.array(DESTINOS)[j],
                    "b": todas[uf].ravel(),
                }
            )
        )
    return pl.DataFrame(linhas), pl.concat(replicas)


def estoques_2026(painel_secao: pl.DataFrame) -> pl.DataFrame:
    """Votos de cada origem no 1º turno de 2026, por UF (sem o exterior)."""
    s = com_origens(painel_secao.filter((pl.col("ano") == 2026) & (pl.col("turno") == 1)))
    return (
        s.group_by("uf")
        .agg(pl.col(ORIGENS_2026).sum(), pl.col("aptos").sum())
        .unpivot(index=["uf", "aptos"], on=ORIGENS_2026, variable_name="origem", value_name="n")
        .sort("uf", "origem")
    )


def reserva(df: pl.DataFrame) -> pl.DataFrame:
    """Reserva líquida e rendimento por ponto de comparecimento (G3), em qualquer nível.

    p = Lula / (Lula + Flávio). reserva = abstenções × (2p − 1): o saldo de votos se quem não
    votou votasse como quem votou no mesmo lugar. rendimento_pp = aptos × 0,01 × (2p − 1).
    """
    p = pl.col("votos_pt") / (pl.col("votos_pt") + pl.col("votos_adv"))
    nao_votou = pl.col("aptos") - pl.col("comparecimento")
    return df.with_columns(
        p_lula=p,
        nao_votou=nao_votou,
        abstencao=nao_votou / pl.col("aptos"),
        reserva=nao_votou * (2 * p - 1),
        rendimento_pp=pl.col("aptos") * 0.01 * (2 * p - 1),
    )


def perdidos(de: pl.DataFrame, para: pl.DataFrame, chave: list[str]) -> pl.DataFrame:
    """Votantes perdidos = (t_de − t_para) × aptos_para, com t = comparecimento / aptos.

    de: 2º turno de 2022; para: 1º turno de 2026. Positivo: votou-se menos agora.
    """
    t = pl.col("comparecimento") / pl.col("aptos")
    a = de.select(*chave, t_2022_2t=t)
    b = para.select(*chave, "aptos", t_2026_1t=t)
    return (
        a.join(b, on=chave, how="inner")
        .with_columns(perdidos=(pl.col("t_2022_2t") - pl.col("t_2026_1t")) * pl.col("aptos"))
        .drop("aptos")
    )


def reserva_por_local(painel_local: pl.DataFrame) -> pl.DataFrame:
    """Locais de 2026 (1º turno) com reserva e votantes perdidos desde o 2º turno de 2022."""
    l26 = reserva(painel_local.filter((pl.col("ano") == 2026) & (pl.col("turno") == 1)))
    l22 = painel_local.filter((pl.col("ano") == 2022) & (pl.col("turno") == 2))
    casados = casa_locais(
        l22.select("cd_tse", "zona", "nr_local", "nm_local", "aptos", "comparecimento"),
        l26.select("cd_tse", "zona", "nr_local", "nm_local", "aptos", "comparecimento"),
    )
    t22 = pl.col("comparecimento") / pl.col("aptos")
    t26 = pl.col("comparecimento_para") / pl.col("aptos_para")
    casados = casados.select(
        "cd_tse", "zona", "nr_local", t_2022_2t=t22, perdidos=(t22 - t26) * pl.col("aptos_para")
    )
    return l26.join(casados, on=["cd_tse", "zona", "nr_local"], how="left").select(
        "uf", "cd_tse", "cd_ibge", "amc_id", "zona", "nr_local", "nm_local", "endereco", "bairro",
        "lat", "lon", "secoes", "aptos", "comparecimento", "nao_votou", "abstencao",
        "votos_pt", "votos_adv", "votos_outros", "p_lula", "reserva", "rendimento_pp",
        "t_2022_2t", "perdidos",
    )  # fmt: skip


def reserva_por_municipio(
    painel_municipio: pl.DataFrame, painel_secao: pl.DataFrame
) -> pl.DataFrame:
    """Municípios no 1º turno de 2026: reserva, votantes perdidos e votos dos eliminados."""
    m26 = painel_municipio.filter((pl.col("ano") == 2026) & (pl.col("turno") == 1))
    m22 = painel_municipio.filter((pl.col("ano") == 2022) & (pl.col("turno") == 2))
    eliminados = (
        painel_secao.filter((pl.col("ano") == 2026) & (pl.col("turno") == 1))
        .group_by("cd_ibge")
        .agg(votos_eliminados=pl.sum_horizontal(f"votos_{g}" for g in ELIMINADOS_DIREITA).sum())
    )
    return (
        reserva(m26)
        .join(perdidos(m22, m26, ["cd_ibge"]), on="cd_ibge", how="left")
        .join(eliminados, on="cd_ibge", how="left")
    )


def ex_eleitores(painel_amc: pl.DataFrame) -> pl.DataFrame:
    """LMDI dos votos de Lula do 2º turno de 2022 ao 1º de 2026, por AMC (G4)."""

    def pleito(ano, turno, sufixo):
        return painel_amc.filter((pl.col("ano") == ano) & (pl.col("turno") == turno)).select(
            "amc_id",
            "uf",
            *(pl.col(c).alias(f"{c}_{sufixo}") for c in ("aptos", "comparecimento", "validos")),
            pl.col("votos_pt").alias(f"votos_{sufixo}"),
            pl.col("votos_adv").alias(f"adv_{sufixo}"),
        )

    base = pleito(2022, 2, "de").join(pleito(2026, 1, "para").drop("uf"), on="amc_id")
    return decompoe_votos(base).sort("amc_id")


# --- Cenários: os estoques de 2026 com as taxas de 2022 (G1 + G2) ---------------------------

# Linha da matriz de 2022 que cada origem de 2026 herda. Finalistas, brancos/nulos e abstenção
# herdam a própria linha em todos os cenários.
FIXAS = {"pt": "pt", "adv": "adv", "bn": "bn", "abst": "abst", "esquerda": "esquerda"}
ELIMINADOS_DIREITA = ["cury", "renan", "caiado", "zema", "direita"]
CENARIOS = {
    "perfil": {"cury": "tebet", "renan": "direita", "caiado": "direita", "zema": "direita",
               "direita": "direita"},
    "como_tebet": dict.fromkeys(ELIMINADOS_DIREITA, "tebet"),
    "como_ciro": dict.fromkeys(ELIMINADOS_DIREITA, "ciro"),
    "como_direita": dict.fromkeys(ELIMINADOS_DIREITA, "direita"),
}  # fmt: skip


def saldo_por_origem(b: dict[str, np.ndarray], estoques: pl.DataFrame, mapa: dict) -> dict:
    """Saldo Lula − Flávio no 2º turno trazido por cada origem de 2026, somado nas UFs.

    b: matriz (origens de 2022 × destinos) de cada UF. saldo_k = Σ_uf N_k · (B[pt] − B[adv]).
    """
    linha = {o: i for i, o in enumerate(ORIGENS_2022)}
    ipt, iadv = DESTINOS.index("pt"), DESTINOS.index("adv")
    saldo = dict.fromkeys(ORIGENS_2026, 0.0)
    for uf, n, origem in estoques.select("uf", "n", "origem").iter_rows():
        bl = b[uf][linha[(FIXAS | mapa)[origem]]]
        saldo[origem] += n * (bl[ipt] - bl[iadv])
    return saldo


def votos_finalistas(b: dict[str, np.ndarray], estoques: pl.DataFrame, mapa: dict) -> tuple:
    """Votos de Lula e de Flávio no 2º turno no cenário (sem o exterior): Σ N_k · B[destino]."""
    linha = {o: i for i, o in enumerate(ORIGENS_2022)}
    ipt, iadv = DESTINOS.index("pt"), DESTINOS.index("adv")
    lula = flavio = 0.0
    for uf, n, origem in estoques.select("uf", "n", "origem").iter_rows():
        bl = b[uf][linha[(FIXAS | mapa)[origem]]]
        lula += n * bl[ipt]
        flavio += n * bl[iadv]
    return lula, flavio


def cenarios(
    matriz: pl.DataFrame,
    replicas: pl.DataFrame,
    estoques: pl.DataFrame,
    exterior: dict[str, float],
) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Margem de Lula no 2º turno (votos) e fatia entre os dois em cada cenário, com IC.

    O exterior entra com os votos do 1º turno de cada finalista, fixos (`exterior`: pt, adv).
    A fatia `pt_2p` é a unidade das pesquisas (G6). Devolve também o saldo por origem do
    cenário `perfil`, comparado ao do 1º turno (quanto cada origem move a margem).
    """
    ext_margem = exterior["pt"] - exterior["adv"]

    def fatia(b, mapa):
        lula, flavio = votos_finalistas(b, estoques, mapa)
        return (lula + exterior["pt"]) / (lula + flavio + exterior["pt"] + exterior["adv"])

    ufs = [u for u in matriz["uf"].unique().to_list() if u != "BR"]

    def matrizes(df):
        return {
            uf: df.filter(pl.col("uf") == uf)
            .pivot(on="destino", index="origem", values="b")
            .sort(pl.col("origem").replace_strict({o: i for i, o in enumerate(ORIGENS_2022)}))
            .select(DESTINOS)
            .to_numpy()
            for uf in ufs
        }

    ponto = matrizes(matriz)
    reps = [matrizes(r) for _, r in replicas.sort("rep").group_by("rep", maintain_order=True)]
    linhas = []
    for nome, mapa in CENARIOS.items():
        m = sum(saldo_por_origem(ponto, estoques, mapa).values()) + ext_margem
        dist = [sum(saldo_por_origem(b, estoques, mapa).values()) + ext_margem for b in reps]
        inf, sup = np.percentile(dist, [2.5, 97.5]) if dist else (m, m)
        f = fatia(ponto, mapa)
        dist_f = [fatia(b, mapa) for b in reps]
        f_inf, f_sup = np.percentile(dist_f, [2.5, 97.5]) if dist_f else (f, f)
        linhas.append(
            {"cenario": nome, "margem": m, "ic_inf": inf, "ic_sup": sup,
             "pt_2p": f, "pt_2p_inf": f_inf, "pt_2p_sup": f_sup}
        )  # fmt: skip

    primeiro = dict(estoques.group_by("origem").agg(pl.col("n").sum()).iter_rows())
    base = {"pt": primeiro["pt"], "adv": -primeiro["adv"]}
    saldo = saldo_por_origem(ponto, estoques, CENARIOS["perfil"])
    componentes = pl.DataFrame(
        [{"origem": o, "votos_1t": primeiro[o], "saldo_2t": s, "efeito": s - base.get(o, 0.0)}
         for o, s in saldo.items()]
    )  # fmt: skip
    return pl.DataFrame(linhas), componentes


def padrao_2022(componentes: pl.DataFrame, b_br: dict) -> dict:
    """Taxas efetivas do cenário `perfil`, no formato das alavancas da calculadora da página.

    r_k = saldo (Lula − Flávio) no 2º turno por eleitor da origem k, somado nas UFs. Com elas,
    a identidade da G1 aplicada aos estoques nacionais reproduz a margem do cenário. A
    abstenção se divide em quantos votam (matriz nacional) e na fatia de Lula entre eles que
    dá o mesmo saldo.
    """
    s = {
        o: (sal, n)
        for o, n, sal in componentes.select("origem", "votos_1t", "saldo_2t").iter_rows()
    }
    r = {o: sal / n for o, (sal, n) in s.items()}
    elim_saldo = sum(s[o][0] for o in ELIMINADOS_DIREITA)
    elim_n = sum(s[o][1] for o in ELIMINADOS_DIREITA)
    votam = b_br[("abst", "pt")] + b_br[("abst", "adv")]
    return {
        "perda_base": 1 - r["pt"],
        "perda_flavio": 1 + r["adv"],
        "conversao": 0.0,
        "saldo_eliminados": elim_saldo / elim_n,
        "saldo_esquerda": r["esquerda"],
        "saldo_bn": r["bn"],
        "abst_votam": votam,
        "abst_lula": (r["abst"] / votam + 1) / 2,
    }


# --- Lições dos 2ºs turnos anteriores (G1, G3, G5) -------------------------------------------


def entre_turnos(painel_amc: pl.DataFrame) -> pl.DataFrame:
    """Votos ganhos por PT e adversário e variação do comparecimento entre os turnos."""
    tot = painel_amc.group_by("ano", "turno").agg(
        pl.col("votos_pt", "votos_adv", "votos_outros", "comparecimento", "brancos", "nulos").sum()
    )
    t1 = tot.filter(pl.col("turno") == 1).drop("turno")
    t2 = tot.filter(pl.col("turno") == 2).drop("turno")
    return (
        t1.join(t2, on="ano", suffix="_2")
        .select(
            pl.col("ano").cast(pl.String),
            pt_mi=(pl.col("votos_pt_2") - pl.col("votos_pt")) / 1e6,
            adv_mi=(pl.col("votos_adv_2") - pl.col("votos_adv")) / 1e6,
            comparecimento_mi=(pl.col("comparecimento_2") - pl.col("comparecimento")) / 1e6,
            outros_1t_mi=pl.col("votos_outros") / 1e6,
            vantagem_pt_1t_mi=(pl.col("votos_pt") - pl.col("votos_adv")) / 1e6,
        )
        .sort("ano")
    )


def licao_comparecimento(painel_secao: pl.DataFrame) -> pf.Feols:
    """Δ comparecimento (pp) do 1º para o 2º turno de 2022 contra a fatia de Lula no 1º, por
    seção, com efeito fixo de município e peso dos aptos (G3)."""
    s = (
        pares_2022(painel_secao)
        .with_columns(
            dt=100 * (pl.col("abst_1") - pl.col("abst_2")) / pl.col("aptos"),
            p_lula=100 * pl.col("pt_1") / (pl.col("pt_1") + pl.col("adv_1")),
        )
        .filter(pl.col("aptos") > 0)
    )
    return pf.feols(
        "dt ~ p_lula | cd_ibge",
        s.drop_nulls(["dt", "p_lula"]).to_pandas(),
        weights="aptos",
        vcov={"CRV1": "cd_ibge"},
    )


G5_TERMOS = {
    "z_evangelica": "% evangélica",
    "z_log_renda": "renda (log)",
    "z_aptos": "eleitorado (log)",
    "z_bolsa": "Auxílio Brasil (2022)",
}


def quem_se_moveu(painel_amc, cov, municipios) -> pl.DataFrame:
    """Δ logit do PT entre os turnos de cada eleição contra características da AMC (G5).

    Covariáveis padronizadas na eleição; efeito fixo de UF, peso dos aptos, erros por região
    imediata. A cobertura do Auxílio Brasil só entra em 2022.
    """
    linhas = []
    for ano in (2006, 2010, 2014, 2018, 2022):
        b = base_variacao(painel_amc, cov, municipios, (ano, 1), (ano, 2)).with_columns(
            log_renda=pl.col("renda_pc_mediana").log()
        )
        z = {
            "z_evangelica": "pct_evangelica",
            "z_log_renda": "log_renda",
            "z_aptos": "log_aptos_de",
        } | ({"z_bolsa": "familias_ab_100hab_2022"} if ano == 2022 else {})
        b = b.drop_nulls(list(z.values())).with_columns(
            ((pl.col(c) - pl.col(c).mean()) / pl.col(c).std()).alias(k) for k, c in z.items()
        )
        fit = pf.feols(
            f"delta_logit ~ pt_2p_logit_de + {' + '.join(z)} | uf",
            b.to_pandas(),
            weights="aptos_de",
            vcov={"CRV1": "cd_regiao_imediata"},
        )
        tidy = fit.tidy()
        for termo in z:
            linhas.append(
                {"ano": ano, "termo": termo, "coef": tidy.loc[termo, "Estimate"],
                 "ic_inf": tidy.loc[termo, "2.5%"], "ic_sup": tidy.loc[termo, "97.5%"]}
            )  # fmt: skip
    return pl.DataFrame(linhas)


def governador_2t(ano: int) -> pl.DataFrame:
    """UFs com e sem 2º turno para governador no ano, pelo cadastro de candidatos do TSE (G3b)."""
    with tempfile.TemporaryDirectory(dir=paths.INTERIM) as tmp:
        destino = paths.INTERIM / tmp / "governador.parquet"
        csv_zip_para_parquet(
            paths.RAW / "tse" / "consulta_cand" / f"consulta_cand_{ano}.zip",
            membro=f"consulta_cand_{ano}_BRASIL.csv",
            destino=destino,
            colunas=CANDIDATO,
            filtro="CD_CARGO = '3'",
        )
        c = pl.read_parquet(destino)
    return (
        c.group_by(pl.col("sg_uf").alias("uf"))
        .agg(tem_2t=(pl.col("ds_sit_tot_turno") == "2º TURNO").any())
        .with_columns(ano=pl.lit(ano, pl.Int16))
        .sort("uf")
    )


def base_que_faltou(matriz: pl.DataFrame, gov: pl.DataFrame) -> pl.DataFrame:
    """Fração dos eleitores de cada finalista no 1º turno de 2022 que não votou no 2º, por
    UF com ou sem 2º turno para governador (média ponderada pelos votos do 1º turno)."""
    return (
        matriz.filter((pl.col("uf") != "BR") & pl.col("origem").is_in(["pt", "adv"]))
        .filter(pl.col("destino") == "abst")
        .join(gov.filter(pl.col("ano") == 2022).select("uf", "tem_2t"), on="uf")
        .group_by("origem", "tem_2t")
        .agg(abst=(pl.col("b") * pl.col("n_origem")).sum() / pl.col("n_origem").sum(), ufs=pl.len())
        .sort("origem", "tem_2t")
    )


# --- Registro no DVC (D12) ------------------------------------------------------------------

FAIXAS = [5_000, 10_000, 20_000, 50_000, 100_000, 500_000]
ROTULOS = [
    "< 5 mil",
    "5–10 mil",
    "10–20 mil",
    "20–50 mil",
    "50–100 mil",
    "100–500 mil",
    "≥ 500 mil",
]


def registra(live, t: dict) -> None:
    """Métricas G* e dados de gráfico (mesmos nomes da página pública)."""
    m = resultados.metrica
    d = t["diferenca"]
    m(live, "G1/diferenca_mi", d / 1e6)
    m(live, "G1/exterior_margem_mi", t["exterior"] / 1e6)
    est = t["estoques"].group_by("origem").agg(pl.col("n").sum())
    estoque = dict(est.iter_rows())
    for o, n in estoque.items():
        m(live, f"G1/estoques_mi/{o}", n / 1e6)
    eliminados = sum(estoque[o] for o in [*ELIMINADOS_DIREITA, "esquerda"])
    # taxa líquida (Lula − Flávio) que fecharia a diferença sozinha
    for nome, n in {"eliminados": eliminados, "abst": estoque["abst"], "bn": estoque["bn"]}.items():
        m(live, f"G1/taxa_necessaria/{nome}", d / n)
    m(live, "G1/estoques_mi/eliminados", sum(estoque[o] for o in ELIMINADOS_DIREITA) / 1e6)
    m(live, "G1/valor_1pct_mi/conversao", 2 * estoque["adv"] / 100 / 1e6)
    m(live, "G1/valor_1pct_mi/eliminados", sum(estoque[o] for o in ELIMINADOS_DIREITA) / 100 / 1e6)
    resultados.serie(
        live,
        "G1_estoques_2026",
        est.filter(~pl.col("origem").is_in(["pt", "adv"]))
        .select("origem", mi=pl.col("n") / 1e6)
        .sort("mi", descending=True),
        x="mi",
        y="origem",
    )
    et = t["entre_turnos"]
    for row in et.iter_rows(named=True):
        resultados.metricas(
            live, f"G1/entre_turnos/{row['ano']}", {k: v for k, v in row.items() if k != "ano"}
        )
    resultados.serie(live, "G1_entre_turnos", et, x="ano", y=["pt_mi", "adv_mi"])

    br = t["matriz"].filter(pl.col("uf") == "BR")
    for row in br.iter_rows(named=True):
        resultados.metricas(
            live, f"G2/BR/{row['origem']}/{row['destino']}",
            {"b": row["b"], "ic_inf": row["ic_inf"], "ic_sup": row["ic_sup"]},
        )  # fmt: skip
    b = {(o, dd): v for o, dd, v in br.select("origem", "destino", "b").iter_rows()}
    m(live, "G2/validacao/retencao_pt", b[("pt", "pt")])
    m(live, "G2/validacao/retencao_adv", b[("adv", "adv")])
    m(live, "G2/validacao/passa", min(b[("pt", "pt")], b[("adv", "adv")]) > 0.9)
    n_or = dict(br.filter(pl.col("destino") == "pt").select("origem", "n_origem").iter_rows())
    for dd, real in t["real_2t_2022"].items():
        implicado = sum(n_or[o] * b[(o, dd)] for o in ORIGENS_2022)
        m(live, f"G2/validacao/implicado_menos_real_mil/{dd}", (implicado - real) / 1e3)
    resultados.coeficientes(
        live,
        "G2_transicao_BR",
        br.filter(pl.col("destino").is_in(["pt", "adv"])).with_columns(
            rotulo=pl.col("origem") + " → " + pl.col("destino")
        ),
        coef="b",
    )
    cen = t["cenarios"]
    for row in cen.iter_rows(named=True):
        resultados.metricas(
            live, f"G2/cenarios/{row['cenario']}",
            {"margem_mi": row["margem"] / 1e6, "ic_inf_mi": row["ic_inf"] / 1e6,
             "ic_sup_mi": row["ic_sup"] / 1e6, "pt_2p": row["pt_2p"],
             "pt_2p_inf": row["pt_2p_inf"], "pt_2p_sup": row["pt_2p_sup"]},
        )  # fmt: skip
    resultados.coeficientes(
        live,
        "G2_cenarios",
        cen.with_columns(pl.col("margem", "ic_inf", "ic_sup") / 1e6),
        rotulo="cenario",
        coef="margem",
    )
    comp = t["componentes"]
    for row in comp.iter_rows(named=True):
        m(live, f"G2/efeito_perfil_mi/{row['origem']}", row["efeito"] / 1e6)
    efeito = dict(comp.select("origem", "efeito").iter_rows())
    m(live, "G2/efeito_perfil_mi/renan_caiado", (efeito["renan"] + efeito["caiado"]) / 1e6)
    resultados.metricas(live, "G2/padrao_2022", padrao_2022(comp, b))
    resultados.serie(
        live,
        "G2_efeito_por_origem",
        comp.select("origem", mi=pl.col("efeito") / 1e6).sort("mi"),
        x="mi",
        y="origem",
    )

    rm = t["reserva_municipio"]
    lula = pl.col("p_lula") > 0.5
    g3 = rm.select(
        nao_votou_mi=pl.col("nao_votou").sum() / 1e6,
        reserva_mi=pl.col("reserva").sum() / 1e6,
        reserva_lula_mi=pl.col("reserva").filter(lula).sum() / 1e6,
        rendimento_pp_lula_mil=pl.col("rendimento_pp").filter(lula).sum() / 1e3,
        perdidos_mi=pl.col("perdidos").sum() / 1e6,
        perdidos_onde_lula_lidera_mi=pl.col("perdidos").filter(lula).sum() / 1e6,
    ).row(0, named=True)
    resultados.metricas(live, "G3/BR", g3)
    m(live, "G3/locais/casados", t["reserva_local"]["perdidos"].is_not_null().mean())
    por_uf = (
        rm.group_by("uf")
        .agg(
            reserva_lula_mil=pl.col("reserva").filter(lula).sum() / 1e3,
            rendimento_pp_lula_mil=pl.col("rendimento_pp").filter(lula).sum() / 1e3,
        )
        .sort("reserva_lula_mil", descending=True)
    )
    resultados.serie(live, "G3_reserva_uf", por_uf, x="reserva_lula_mil", y="uf")
    lic = t["licao_comparecimento"]
    resultados.ajuste(live, "G3/licao_2022", lic, "p_lula")
    for row in t["base_que_faltou"].iter_rows(named=True):
        lado = "com" if row["tem_2t"] else "sem"
        resultados.metricas(
            live,
            f"G3b/2022/{row['origem']}/{lado}_governador",
            {"abst": row["abst"], "ufs": row["ufs"]},
        )
    gov26 = t["governador"].filter(pl.col("ano") == 2026)
    m(live, "G3b/2026/ufs_com_governador", int(gov26["tem_2t"].sum()))
    m(live, "G3b/2026/votos_lula_sem_governador_mi", t["estoques"].join(gov26, on="uf").filter(
        (pl.col("origem") == "pt") & ~pl.col("tem_2t")
    )["n"].sum() / 1e6)  # fmt: skip

    ex = t["ex_eleitores"]
    tot = ex.select(
        pl.col("delta", "c_eleitorado", "c_comparecimento", "c_validos", "c_fatia").sum()
    ).row(0, named=True)
    resultados.metricas(
        live, "G4/componentes_mi", {k.removeprefix("c_"): v / 1e6 for k, v in tot.items()}
    )
    fatia_uf = ex.group_by("uf").agg(fatia_mil=pl.col("c_fatia").sum() / 1e3).sort("fatia_mil")
    resultados.serie(live, "G4_fatia_uf", fatia_uf, x="fatia_mil", y="uf")
    fatia_faixa = (
        ex.with_columns(
            faixa=pl.col("aptos_de").bin_intervals(FAIXAS, labels=ROTULOS).cast(pl.String)
        )
        .group_by("faixa")
        .agg(fatia_mil=pl.col("c_fatia").sum() / 1e3, aptos_mi=pl.col("aptos_de").sum() / 1e6)
        .sort(pl.col("faixa").replace_strict({r: i for i, r in enumerate(ROTULOS)}))
    )
    for row in fatia_faixa.iter_rows(named=True):
        m(live, f"G4/fatia_mil/{resultados.chave(row['faixa'])}", row["fatia_mil"])
    resultados.serie(live, "G4_fatia_faixa", fatia_faixa, x="fatia_mil", y="faixa")

    g5 = t["quem_se_moveu"]
    for termo in G5_TERMOS:
        parte = g5.filter(pl.col("termo") == termo).with_columns(
            rotulo=pl.col("ano").cast(pl.String)
        )
        for row in parte.iter_rows(named=True):
            resultados.metricas(
                live, f"G5/{termo}/{row['ano']}",
                {"coef": row["coef"], "ic_inf": row["ic_inf"], "ic_sup": row["ic_sup"]},
            )  # fmt: skip
        resultados.coeficientes(live, f"G5_{termo}", parte)


def executa() -> None:
    cfg = resultados.params("segundo_turno")
    SAIDA.mkdir(parents=True, exist_ok=True)
    painel_secao = pl.read_parquet(paths.PROCESSED / "painel_secao.parquet")
    painel_local = pl.read_parquet(paths.PROCESSED / "painel_local.parquet")
    painel_municipio = pl.read_parquet(paths.PROCESSED / "painel_municipio.parquet")
    painel_amc = pl.read_parquet(paths.PROCESSED / "painel_amc.parquet")
    votos = pl.read_parquet(paths.PROCESSED / "votos_municipio.parquet")
    cov = pl.read_parquet(paths.PROCESSED / "covariaveis_amc.parquet")
    municipios = pl.read_parquet(paths.PROCESSED / "municipios.parquet")

    t = {}
    t["matriz"], replicas = transicao(pares_2022(painel_secao), cfg["reps"], cfg["semente"])
    t["estoques"] = estoques_2026(painel_secao)
    t["reserva_local"] = reserva_por_local(painel_local)
    t["reserva_municipio"] = reserva_por_municipio(painel_municipio, painel_secao)
    t["ex_eleitores"] = ex_eleitores(painel_amc)
    arquivos = {
        "matriz": "transicao_2022",
        "estoques": "estoques_2026",
        "reserva_local": "reserva_local",
        "reserva_municipio": "reserva_municipio",
        "ex_eleitores": "ex_eleitores_amc",
    }
    for nome, arquivo in arquivos.items():
        t[nome].write_parquet(SAIDA / f"{arquivo}.parquet")
    replicas.write_parquet(SAIDA / "transicao_2022_replicas.parquet")

    v26 = votos.filter((pl.col("ano") == 2026) & (pl.col("turno") == 1))
    por_papel = dict(v26.group_by("papel").agg(pl.col("votos").sum()).iter_rows())
    t["diferenca"] = por_papel["adversario"] - por_papel["pt"]
    ext = dict(
        v26.filter(pl.col("uf") == "ZZ").group_by("papel").agg(pl.col("votos").sum()).iter_rows()
    )
    t["exterior"] = ext.get("pt", 0) - ext.get("adversario", 0)
    t["cenarios"], t["componentes"] = cenarios(
        t["matriz"],
        replicas,
        t["estoques"],
        {"pt": ext.get("pt", 0), "adv": ext.get("adversario", 0)},
    )
    t["cenarios"].write_parquet(SAIDA / "cenarios_2026.parquet")
    t["componentes"].write_parquet(SAIDA / "efeito_por_origem_2026.parquet")

    p2 = pares_2022(painel_secao)
    t["real_2t_2022"] = {d: float(p2[f"{d}_2"].sum()) for d in DESTINOS}
    t["entre_turnos"] = entre_turnos(painel_amc)
    t["licao_comparecimento"] = licao_comparecimento(painel_secao)
    t["quem_se_moveu"] = quem_se_moveu(painel_amc, cov, municipios)
    t["governador"] = pl.concat([governador_2t(2022), governador_2t(2026)])
    t["governador"].write_parquet(SAIDA / "governador_2t.parquet")
    t["base_que_faltou"] = base_que_faltou(t["matriz"], t["governador"])

    live = resultados.abre_etapa("segundo_turno")
    registra(live, t)
    live.end()


if __name__ == "__main__":
    executa()
