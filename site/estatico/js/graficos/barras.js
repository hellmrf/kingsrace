// Barras horizontais com sinal: a barra parte do zero (à direita: rumo a Lula; à esquerda:
// rumo a Flávio, salvo outra cor). Rótulo de valor direto em cada barra, tooltip no hover.
// desenha(el, linhas, { rotulo, valor, formato, cor, dica, alturaBarra })
import { interativo } from "../componentes/dica.js";

const NS = "http://www.w3.org/2000/svg";
const css = (nome) => getComputedStyle(document.documentElement).getPropertyValue(nome).trim();

function no(tag, attrs = {}, pai) {
  const n = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
  if (pai) pai.append(n);
  return n;
}

// retângulo com cantos arredondados só na ponta do dado (4px), reto no zero
function caminhoBarra(x0, x1, y, h, r = 4) {
  const esq = Math.min(x0, x1), dir = Math.max(x0, x1);
  const w = dir - esq;
  const rr = Math.min(r, w / 2, h / 2);
  if (w <= 0) return "";
  if (x1 >= x0) {
    return `M${esq},${y}H${dir - rr}Q${dir},${y} ${dir},${y + rr}V${y + h - rr}Q${dir},${y + h} ${dir - rr},${y + h}H${esq}Z`;
  }
  return `M${dir},${y}H${esq + rr}Q${esq},${y} ${esq},${y + rr}V${y + h - rr}Q${esq},${y + h} ${esq + rr},${y + h}H${dir}Z`;
}

export function desenha(el, linhas, opcoes) {
  const {
    rotulo, valor, formato, cor = (d) => (valor(d) >= 0 ? "--pt" : "--adv"),
    dica = (d) => [[formato(valor(d)), rotulo(d)]], alturaBarra = 14, larguraRotulo = 120,
  } = opcoes;
  el.replaceChildren();
  const largura = Math.max(280, el.clientWidth || 600);
  const passo = alturaBarra + 10;
  const altura = linhas.length * passo + 8;
  const margemValor = 64;
  const valores = linhas.map(valor);
  const min = Math.min(0, ...valores), max = Math.max(0, ...valores);
  // espaço para o rótulo de valor do lado em que as barras crescem
  const area = [larguraRotulo + (min < 0 ? margemValor : 0), largura - (max > 0 ? margemValor : 8)];
  const escala = (v) => area[0] + ((v - min) / (max - min || 1)) * (area[1] - area[0]);
  const zero = escala(0);

  const svg = no("svg", { viewBox: `0 0 ${largura} ${altura}`, role: "img" }, el);
  no("line", { x1: zero, x2: zero, y1: 0, y2: altura, class: "base" }, svg);
  linhas.forEach((d, i) => {
    const y = 4 + i * passo;
    const g = no("g", {}, svg);
    const v = valor(d);
    no("text", { x: larguraRotulo - 8, y: y + alturaBarra / 2 + 4, "text-anchor": "end" }, g).textContent = rotulo(d);
    no("path", { d: caminhoBarra(zero, escala(v), y, alturaBarra), fill: css(cor(d)), class: "marca" }, g);
    const xTexto = v >= 0 ? escala(v) + 6 : escala(v) - 6;
    const t = no("text", {
      x: xTexto, y: y + alturaBarra / 2 + 4, "text-anchor": v >= 0 ? "start" : "end", class: "valor",
    }, g);
    t.textContent = formato(v);
    // alvo de hover maior que a marca: a linha inteira
    no("rect", { x: 0, y: y - 4, width: largura, height: passo, fill: "transparent" }, g);
    interativo(g, () => dica(d));
  });
  return svg;
}
