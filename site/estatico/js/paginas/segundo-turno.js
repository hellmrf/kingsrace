// Página "Como virar": desenha os gráficos com os dados das etapas do DVC (graficos.json, mesmos
// nomes do `dvc plots`) e liga a calculadora e a busca.
import { desenha as barras } from "../graficos/barras.js";
import { desenha as pares } from "../graficos/pares.js";
import { desenha as linhas } from "../graficos/linhas.js";
import { desenha as pontos } from "../graficos/pontos.js";
import { liga as ligaCalculadora } from "../componentes/calculadora.js";
import { liga as ligaBusca } from "../componentes/busca.js";
import { br, mi, sinal } from "../formato.js";

async function json(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${url}: ${r.status}`);
  return r.json();
}

export async function iniciar(base) {
  const [graficos, pagina] = await Promise.all([json(`${base}graficos.json`), json(`${base}pagina.json`)]);
  const rot = pagina.rotulo_origem;
  const alvo = (id) => document.querySelector(`[data-grafico="${id}"]`);

  const g6 = pagina.g6;
  const desenhos = {
    G6_media: (el) =>
      linhas(el, {
        media: graficos.G6_media,
        pontos: graficos.G6_pesquisas,
        referencias: [
          { rotulo: "empate", valor: 50, forte: true, cor: "--eixo" },
          { rotulo: "padrão de 2022", valor: 100 * g6.modelo.perfil, cor: "--adv" },
          { rotulo: "previsão de 8/10", valor: 100 * g6.modelo.b4_v1, cor: "--tinta-3" },
        ],
        inicio: "2026-10-04",
        fim: "2026-10-25",
      }, { formato: (v) => `${br(v, 1)}%` }),
    G1_entre_turnos: (el) =>
      pares(el, graficos.G1_entre_turnos, {
        categoria: "ano",
        series: [
          { chave: "pt_mi", nome: "PT", cor: "--pt" },
          { chave: "adv_mi", nome: "Adversário", cor: "--adv" },
        ],
        formato: (v) => sinal(v, 1),
        unidade: " mi",
      }),
    G2_efeito_por_origem: (el) =>
      barras(el, graficos.G2_efeito_por_origem, {
        rotulo: (d) => rot[d.origem] ?? d.origem,
        valor: (d) => d.mi,
        formato: (v) => sinal(v, 2),
        dica: (d) => [[`${sinal(d.mi, 2)} mi`, `${rot[d.origem] ?? d.origem}: quanto move a margem de Lula`]],
        larguraRotulo: 150,
      }),
    G3_reserva_uf: (el) =>
      barras(el, graficos.G3_reserva_uf.slice(0, 15), {
        rotulo: (d) => d.uf,
        valor: (d) => d.reserva_lula_mil,
        formato: (v) => br(v, 0),
        cor: () => "--pt",
        dica: (d) => [[`${br(d.reserva_lula_mil, 0)} mil votos`, `${d.uf}: reserva onde Lula lidera`],
          [`${br(d.rendimento_pp_lula_mil, 1)} mil`, "por ponto de comparecimento"]],
        larguraRotulo: 40,
      }),
    G4_fatia_uf: (el) =>
      barras(el, graficos.G4_fatia_uf.slice(0, 15), {
        rotulo: (d) => d.uf,
        valor: (d) => d.fatia_mil,
        formato: (v) => br(v, 0),
        cor: () => "--adv",
        dica: (d) => [[`${br(d.fatia_mil, 0)} mil votos`, `${d.uf}: votos de Lula perdidos na fatia`]],
        larguraRotulo: 40,
      }),
  };

  const redesenha = () => {
    for (const [id, f] of Object.entries(desenhos)) {
      const el = alvo(id);
      if (el) f(el);
    }
  };
  redesenha();
  let espera;
  window.addEventListener("resize", () => {
    clearTimeout(espera);
    espera = setTimeout(redesenha, 150);
  });

  ligaMapa(base);

  const calc = document.querySelector("[data-calculadora]");
  if (calc) ligaCalculadora(calc, pagina.calculadora);
  const busca = document.querySelector("[data-busca]");
  if (busca) ligaBusca(busca, base);
  document.documentElement.dataset.pronto = "1";
  return { mi };
}

const MODOS = {
  mobilizar: {
    arquivo: "municipios.json",
    sub: "Votos líquidos para Lula a cada ponto de comparecimento a mais. Vermelho: onde Lula lidera; azul: onde Flávio lidera.",
    valor: (d) => d.rendimento_pp,
    cor: (d) => (d.rendimento_pp >= 0 ? "--pt" : "--adv"),
    dica: (d) => [[`${sinal(d.rendimento_pp, 0)} votos por ponto`, `${d.nome} (${d.uf})`],
      [`${br(100 * d.p_lula, 0)}% Lula entre os dois`, `abstenção de ${br(100 * d.abstencao, 1)}%`]],
    legenda: { valores: [500, 2000, 8000], formato: (v) => (v >= 1000 ? `${br(v / 1000, 0)} mil` : br(v, 0)) },
  },
  conversar: {
    arquivo: "amcs.json",
    sub: "Votos que Lula perdeu na fatia entre quem votou, do 2º turno de 2022 ao 1º de 2026: onde estão os ex-eleitores.",
    valor: (d) => d.fatia,
    cor: () => "--adv",
    dica: (d) => [[`${br(-d.fatia, 0)} votos perdidos`, `${d.nome} (${d.uf})`]],
    legenda: { valores: [5000, 50000, 300000], formato: (v) => `${br(v / 1000, 0)} mil` },
  },
};

function ligaMapa(base) {
  const el = document.querySelector('[data-grafico="mapa"]');
  if (!el) return;
  const sub = document.querySelector("[data-mapa-sub]");
  const botoes = document.querySelectorAll("[data-mapa]");
  const cache = new Map();
  let atual = "mobilizar";
  async function mostra(modo) {
    atual = modo;
    const cfg = MODOS[modo];
    if (!cache.has(cfg.arquivo)) cache.set(cfg.arquivo, await json(`${base}${cfg.arquivo}`));
    for (const b of botoes) b.setAttribute("aria-pressed", String(b.dataset.mapa === modo));
    sub.textContent = cfg.sub;
    pontos(el, cache.get(cfg.arquivo), cfg);
  }
  for (const b of botoes) b.addEventListener("click", () => mostra(b.dataset.mapa));
  let espera;
  window.addEventListener("resize", () => {
    clearTimeout(espera);
    espera = setTimeout(() => mostra(atual), 200);
  });
  mostra(atual);
}
