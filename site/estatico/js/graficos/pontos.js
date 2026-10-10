// Mapa de pontos proporcionais: um círculo por município, no centro eleitoral (média dos locais
// de votação), com área proporcional a |valor|. Cor pelo sinal (Lula ou Flávio) ou cor única.
// Sem camada de mapa externa: a forma do país aparece pelos próprios pontos.
// desenha(el, linhas, { valor, cor, dica, raioMax, legenda })
import { interativo } from "../componentes/dica.js";

const NS = "http://www.w3.org/2000/svg";
const css = (nome) => getComputedStyle(document.documentElement).getPropertyValue(nome).trim();

function no(tag, attrs = {}, pai) {
  const n = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
  if (pai) pai.append(n);
  return n;
}

export function desenha(el, linhas, { valor, cor, dica, raioMax = 22, legenda }) {
  el.replaceChildren();
  const pts = linhas.filter((d) => d.lat != null && d.lon != null && valor(d) !== 0 && valor(d) != null);
  const largura = Math.max(300, el.clientWidth || 600);
  // equirretangular com correção de cosseno na latitude média do Brasil (~−14°)
  const k = Math.cos((-14 * Math.PI) / 180);
  const lon0 = -74.5, lon1 = -34.0, lat0 = 6.0, lat1 = -34.0;
  const escalaX = largura / ((lon1 - lon0) * k);
  const altura = Math.round((lat0 - lat1) * escalaX);
  const x = (lon) => (lon - lon0) * k * escalaX;
  const y = (lat) => (lat0 - lat) * escalaX;
  const max = Math.max(...pts.map((d) => Math.abs(valor(d))));
  const raio = (v) => Math.sqrt(Math.abs(v) / max) * raioMax * (largura / 700);

  const svg = no("svg", { viewBox: `0 0 ${largura} ${altura}`, role: "img" }, el);
  // maiores primeiro, para os pequenos ficarem por cima; anel de superfície entre círculos
  for (const d of pts.slice().sort((a, b) => Math.abs(valor(b)) - Math.abs(valor(a)))) {
    const g = no("g", {}, svg);
    no("circle", {
      cx: x(d.lon), cy: y(d.lat), r: Math.max(0.8, raio(valor(d))),
      fill: css(cor(d)), "fill-opacity": 0.75, stroke: css("--superficie"), "stroke-width": 0.6, class: "marca",
    }, g);
    interativo(g, () => dica(d));
  }
  // legenda de tamanho: três círculos de referência, no canto
  if (legenda) {
    const gl = no("g", { transform: `translate(${largura - 12}, ${altura - 12})` }, svg);
    let dx = 0;
    for (const v of legenda.valores.slice().reverse()) {
      const r = raio(v);
      no("circle", { cx: -dx - r, cy: -r, r, fill: "none", stroke: css("--tinta-3") }, gl);
      no("text", { x: -dx - r, y: -2 * r - 4, "text-anchor": "middle", class: "eixo-t" }, gl).textContent = legenda.formato(v);
      dx += 2 * r + 14;
    }
  }
}
