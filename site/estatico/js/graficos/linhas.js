// Série no tempo das pesquisas (G6): faixa da correção (λ de 0 a 1), linha da média corrigida,
// um ponto por pesquisa e linhas de referência (50%, padrão de 2022, previsão). O eixo vai do
// 1º turno ao dia da eleição, para mostrar o tempo que resta. Tooltip por dia (cruz).
// desenha(el, { media, pontos, referencias, inicio, fim }, { formato })
import { mostra, esconde } from "../componentes/dica.js";

const NS = "http://www.w3.org/2000/svg";
const css = (nome) => getComputedStyle(document.documentElement).getPropertyValue(nome).trim();
const dia = (s) => new Date(`${s}T12:00:00`);
const curto = (d) => d.toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit" });

function no(tag, attrs = {}, pai) {
  const n = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
  if (pai) pai.append(n);
  return n;
}

export function desenha(el, { media, pontos, referencias, inicio, fim }, { formato }) {
  el.replaceChildren();
  const largura = Math.max(300, el.clientWidth || 600), altura = 280;
  const m = { topo: 12, baixo: 26, esq: 34, dir: 120 };
  const t0 = dia(inicio).getTime(), t1 = dia(fim).getTime();
  const x = (s) => m.esq + ((dia(s).getTime() - t0) / (t1 - t0)) * (largura - m.esq - m.dir);
  const valores = [
    ...media.flatMap((d) => [d.bruta, d.correcao_total]),
    ...pontos.flatMap((p) => [p.s, p.corrigido]),
    ...referencias.map((r) => r.valor),
  ];
  const lo = Math.floor(Math.min(...valores) - 0.5), hi = Math.ceil(Math.max(...valores) + 0.5);
  const y = (v) => m.topo + ((hi - v) / (hi - lo)) * (altura - m.topo - m.baixo);

  const svg = no("svg", { viewBox: `0 0 ${largura} ${altura}`, role: "img" }, el);
  for (let v = lo; v <= hi; v += 1) {
    no("line", { x1: m.esq, x2: largura - m.dir, y1: y(v), y2: y(v), class: "grade" }, svg);
    no("text", { x: m.esq - 6, y: y(v) + 4, "text-anchor": "end", class: "eixo-t" }, svg).textContent = `${v}`;
  }
  // eixo do tempo: 1º turno, cada segunda-feira e a eleição
  const marcas = [inicio, fim];
  for (let t = t0; t <= t1; t += 86400000) {
    const d = new Date(t);
    if (d.getDay() === 1) marcas.push(d.toISOString().slice(0, 10));
  }
  // rótulos do eixo sem se sobrepor: a eleição sempre; os demais se houver 44 px livres
  const ordenadas = [...new Set(marcas)].sort();
  let ultimoX = -Infinity;
  for (const s of ordenadas) {
    const px = x(s);
    if (s !== fim && (px - ultimoX < 44 || x(fim) - px < 70)) continue;
    no("text", { x: px, y: altura - 8, "text-anchor": "middle", class: "eixo-t" }, svg).textContent =
      s === fim ? "25/10 eleição" : curto(dia(s));
    ultimoX = px;
  }
  no("line", { x1: x(fim), x2: x(fim), y1: m.topo, y2: altura - m.baixo, class: "base" }, svg);

  // referências, com rótulo direto à direita; rótulos próximos se afastam (mín. 13 px)
  const rotulos = referencias.map((r) => ({ r, ty: y(r.valor) + 4 })).sort((a, b) => a.ty - b.ty);
  for (let i = 1; i < rotulos.length; i++) {
    if (rotulos[i].ty - rotulos[i - 1].ty < 13) rotulos[i].ty = rotulos[i - 1].ty + 13;
  }
  for (const { r, ty } of rotulos) {
    no("line", {
      x1: m.esq, x2: largura - m.dir, y1: y(r.valor), y2: y(r.valor),
      stroke: css(r.cor ?? "--tinta-3"), "stroke-width": r.forte ? 1.5 : 1, "stroke-dasharray": r.forte ? "" : "4 3",
    }, svg);
    no("text", { x: largura - m.dir + 6, y: ty, class: "eixo-t" }, svg).textContent =
      `${r.rotulo} ${formato(r.valor)}`;
  }

  // faixa da correção e média corrigida
  if (media.length) {
    const topo = media.map((d) => `${x(d.data)},${y(Math.max(d.bruta, d.correcao_total))}`);
    const base = media.slice().reverse().map((d) => `${x(d.data)},${y(Math.min(d.bruta, d.correcao_total))}`);
    no("polygon", { points: [...topo, ...base].join(" "), fill: css("--pt-lavado") }, svg);
    no("polyline", {
      points: media.map((d) => `${x(d.data)},${y(d.corrigida)}`).join(" "),
      fill: "none", stroke: css("--pt"), "stroke-width": 2, "stroke-linejoin": "round",
    }, svg);
  }
  // pesquisas: o valor bruto, vazado; o corrigido, cheio, ligados por um traço
  for (const p of pontos) {
    no("line", { x1: x(p.campo_fim), x2: x(p.campo_fim), y1: y(p.s), y2: y(p.corrigido), stroke: css("--eixo") }, svg);
    no("circle", { cx: x(p.campo_fim), cy: y(p.s), r: 4, fill: css("--superficie"), stroke: css("--pt"), "stroke-width": 1.5 }, svg);
    no("circle", { cx: x(p.campo_fim), cy: y(p.corrigido), r: 4, fill: css("--pt"), stroke: css("--superficie"), "stroke-width": 2 }, svg);
  }

  // cruz no hover: o dia mais próximo da média
  const cruz = no("line", { y1: m.topo, y2: altura - m.baixo, stroke: css("--tinta-3"), visibility: "hidden" }, svg);
  const alvo = no("rect", { x: m.esq, y: 0, width: largura - m.esq - m.dir, height: altura, fill: "transparent" }, svg);
  alvo.addEventListener("pointermove", (e) => {
    const r = svg.getBoundingClientRect();
    const px = ((e.clientX - r.left) / r.width) * largura;
    let melhor = media[0];
    for (const d of media) if (Math.abs(x(d.data) - px) < Math.abs(x(melhor.data) - px)) melhor = d;
    if (!melhor) return;
    cruz.setAttribute("x1", x(melhor.data));
    cruz.setAttribute("x2", x(melhor.data));
    cruz.setAttribute("visibility", "visible");
    const doDia = pontos.filter((p) => p.campo_fim === melhor.data).map((p) => [`${p.instituto}: ${formato(p.s)}`, `corrigido ${formato(p.corrigido)}`]);
    mostra(e, [[formato(melhor.corrigida), `média corrigida em ${curto(dia(melhor.data))} (${melhor.institutos} institutos)`],
      [`${formato(Math.min(melhor.bruta, melhor.correcao_total))} a ${formato(Math.max(melhor.bruta, melhor.correcao_total))}`, "faixa da correção"], ...doDia]);
  });
  alvo.addEventListener("pointerleave", () => { cruz.setAttribute("visibility", "hidden"); esconde(); });
}
