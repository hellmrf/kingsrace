// Barras agrupadas verticais: para cada categoria (ex.: eleição), uma barra por série, a partir
// do zero (valores negativos descem). Legenda acima, rótulo de valor em cada barra, tooltip.
// desenha(el, linhas, { categoria, series: [{ chave, nome, cor }], formato, unidade })
import { interativo } from "../componentes/dica.js";

const NS = "http://www.w3.org/2000/svg";
const css = (nome) => getComputedStyle(document.documentElement).getPropertyValue(nome).trim();

function no(tag, attrs = {}, pai) {
  const n = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
  if (pai) pai.append(n);
  return n;
}

function barraVertical(x, y0, y1, w, r = 4) {
  const topo = Math.min(y0, y1), fundo = Math.max(y0, y1), h = fundo - topo;
  const rr = Math.min(r, w / 2, h / 2);
  if (h <= 0) return "";
  if (y1 <= y0) {  // positiva: arredonda em cima
    return `M${x},${fundo}V${topo + rr}Q${x},${topo} ${x + rr},${topo}H${x + w - rr}Q${x + w},${topo} ${x + w},${topo + rr}V${fundo}Z`;
  }
  return `M${x},${topo}V${fundo - rr}Q${x},${fundo} ${x + rr},${fundo}H${x + w - rr}Q${x + w},${fundo} ${x + w},${fundo - rr}V${topo}Z`;
}

export function desenha(el, linhas, { categoria, series, formato, unidade = "" }) {
  el.replaceChildren();
  const legenda = document.createElement("div");
  legenda.className = "legenda";
  for (const s of series) {
    const span = document.createElement("span");
    const i = document.createElement("i");
    i.style.background = `var(${s.cor})`;
    span.append(i, s.nome);
    legenda.append(span);
  }
  el.append(legenda);

  const largura = Math.max(300, el.clientWidth || 600), altura = 240;
  const m = { topo: 22, baixo: 28, esq: 8, dir: 8 };
  const valores = linhas.flatMap((d) => series.map((s) => d[s.chave]));
  const min = Math.min(0, ...valores), max = Math.max(0, ...valores);
  const folga = min < 0 ? 18 : 0;  // rótulo das barras negativas acima dos rótulos do eixo
  const y = (v) => m.topo + ((max - v) / (max - min || 1)) * (altura - m.topo - m.baixo - folga);
  const banda = (largura - m.esq - m.dir) / linhas.length;
  const w = Math.min(28, (banda * 0.7) / series.length);

  const svg = no("svg", { viewBox: `0 0 ${largura} ${altura}`, role: "img" }, el);
  no("line", { x1: m.esq, x2: largura - m.dir, y1: y(0), y2: y(0), class: "base" }, svg);
  linhas.forEach((d, i) => {
    const centro = m.esq + banda * (i + 0.5);
    const inicio = centro - (w * series.length + 2 * (series.length - 1)) / 2;
    no("text", { x: centro, y: altura - 8, "text-anchor": "middle", class: "eixo-t" }, svg).textContent = d[categoria];
    series.forEach((s, j) => {
      const v = d[s.chave], x = inicio + j * (w + 2);  // 2px de superfície entre as barras
      const g = no("g", {}, svg);
      no("path", { d: barraVertical(x, y(0), y(v), w), fill: css(s.cor), class: "marca" }, g);
      const t = no("text", {
        x: x + w / 2, y: v >= 0 ? y(v) - 5 : y(v) + 13, "text-anchor": "middle", class: "valor",
      }, g);
      t.textContent = formato(v);
      no("rect", { x: x - 1, y: m.topo - 18, width: w + 2, height: altura - m.topo, fill: "transparent" }, g);
      interativo(g, () => [[formato(v) + unidade, `${s.nome}, ${d[categoria]}`]]);
    });
  });
}
