// Números no padrão brasileiro: o mesmo formato de kingsrace.publica.comum (Python).
const MENOS = "−";

const arred = (x, casas) => Number(x.toFixed(casas));

export function br(x, casas = 1) {
  const texto = Math.abs(x).toLocaleString("pt-BR", {
    minimumFractionDigits: casas,
    maximumFractionDigits: casas,
  });
  return (arred(x, casas) < 0 ? MENOS : "") + texto;
}

export const sinal = (x, casas = 1) => (arred(x, casas) > 0 ? "+" : "") + br(x, casas);
export const pct = (fracao, casas = 1) => br(100 * fracao, casas) + "%";
export const mi = (milhoes, casas = 1) =>
  br(milhoes, casas) + (Math.abs(arred(milhoes, casas)) < 2 ? " milhão" : " milhões");
export const mil = (milhares) => br(milhares, 0) + " mil";
