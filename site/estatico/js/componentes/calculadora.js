// Calculadora da virada (série G1): margem de Lula no 2º turno = Σ estoque × saldo de cada grupo
// do 1º turno. Os valores iniciais são as taxas de 2022 da etapa segundo_turno (DVC); com eles,
// a margem é a do cenário "perfil" (G2/cenarios/perfil).
import { br, mi, sinal } from "../formato.js";

const ALAVANCAS = [
  { id: "perda_base", passo: 0.001, min: 0, max: 0.08, fmt: (v) => br(100 * v, 1) + "%" },
  { id: "conversao", passo: 0.001, min: 0, max: 0.05, fmt: (v) => br(100 * v, 1) + "%" },
  { id: "saldo_eliminados", passo: 0.01, min: -0.8, max: 0.8, fmt: (v) => sinal(100 * v, 0) + " pp" },
  { id: "abst_votam", passo: 0.005, min: 0, max: 0.25, fmt: (v) => br(100 * v, 1) + "%" },
  { id: "abst_lula", passo: 0.01, min: 0, max: 1, fmt: (v) => br(100 * v, 0) + "%" },
  { id: "saldo_bn", passo: 0.01, min: -0.6, max: 0.6, fmt: (v) => sinal(100 * v, 0) + " pp" },
  { id: "perda_flavio", passo: 0.001, min: 0, max: 0.08, fmt: (v) => br(100 * v, 1) + "%" },
];

export function margem(n, t, exterior) {
  return (
    n.pt * (1 - t.perda_base) -
    n.adv * (1 - t.perda_flavio) +
    2 * n.adv * t.conversao +
    n.eliminados * t.saldo_eliminados +
    n.esquerda * t.saldo_esquerda +
    n.bn * t.saldo_bn +
    n.abst * t.abst_votam * (2 * t.abst_lula - 1) +
    exterior
  );
}

// contribuição de cada alavanca em relação ao padrão de 2022 (milhões de votos)
function efeitos(n, t, p) {
  return {
    perda_base: -n.pt * (t.perda_base - p.perda_base),
    conversao: 2 * n.adv * (t.conversao - p.conversao),
    saldo_eliminados: n.eliminados * (t.saldo_eliminados - p.saldo_eliminados),
    abst_votam: n.abst * (t.abst_votam * (2 * p.abst_lula - 1) - p.abst_votam * (2 * p.abst_lula - 1)),
    abst_lula: n.abst * t.abst_votam * 2 * (t.abst_lula - p.abst_lula),
    saldo_bn: n.bn * (t.saldo_bn - p.saldo_bn),
    perda_flavio: n.adv * (t.perda_flavio - p.perda_flavio),
  };
}

export function liga(raiz, dados) {
  const { n, padrao_2022: p, exterior_mi: exterior } = dados;
  const t = { ...p };
  const saida = raiz.querySelector("[data-calc-margem]");
  const veredito = raiz.querySelector("[data-calc-veredito]");
  const desvio = raiz.querySelector("[data-calc-desvio]");

  function atualiza() {
    const m = margem(n, t, exterior);
    const e = efeitos(n, t, p);
    saida.textContent = sinal(m, 1) + " mi";
    saida.classList.toggle("pt", m > 0);
    saida.classList.toggle("adv", m <= 0);
    veredito.textContent = m > 0 ? `Lula vence por ${mi(m)} de votos` : `Flávio vence por ${mi(-m)} de votos`;
    const total = Object.values(e).reduce((a, b) => a + b, 0);
    desvio.textContent = `${sinal(total, 1)} mi em relação ao padrão de 2022`;
    for (const a of ALAVANCAS) {
      raiz.querySelector(`[data-calc-valor="${a.id}"]`).textContent = a.fmt(t[a.id]);
      raiz.querySelector(`[data-calc-efeito="${a.id}"]`).textContent = sinal(e[a.id], 2) + " mi";
    }
  }

  for (const a of ALAVANCAS) {
    const input = raiz.querySelector(`input[name="${a.id}"]`);
    Object.assign(input, { min: a.min, max: a.max, step: a.passo, value: p[a.id] });
    input.disabled = false;
    input.addEventListener("input", () => {
      t[a.id] = Number(input.value);
      atualiza();
    });
  }
  raiz.querySelector("[data-calc-reinicia]").addEventListener("click", () => {
    Object.assign(t, p);
    for (const a of ALAVANCAS) raiz.querySelector(`input[name="${a.id}"]`).value = p[a.id];
    atualiza();
  });
  raiz.querySelector("[data-calc-reinicia]").hidden = false;
  atualiza();
}
