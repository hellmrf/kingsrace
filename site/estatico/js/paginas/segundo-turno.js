// Página "Como virar": desenha os gráficos com os dados das etapas do DVC (graficos.json, mesmos
// nomes do `dvc plots`) e liga a calculadora e a busca.
import { desenha as barras } from "../graficos/barras.js";
import { desenha as pares } from "../graficos/pares.js";
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

  const desenhos = {
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

  const calc = document.querySelector("[data-calculadora]");
  if (calc) ligaCalculadora(calc, pagina.calculadora);
  const busca = document.querySelector("[data-busca]");
  if (busca) ligaBusca(busca, base);
  document.documentElement.dataset.pronto = "1";
  return { mi };
}
