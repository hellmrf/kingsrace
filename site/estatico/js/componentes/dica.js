// Tooltip único da página: um <div class="dica"> que segue o ponteiro (ou o foco no teclado).
let caixa;

function garante() {
  if (!caixa) {
    caixa = document.createElement("div");
    caixa.className = "dica";
    caixa.setAttribute("role", "status");
    caixa.hidden = true;
    document.body.append(caixa);
  }
  return caixa;
}

function posiciona(x, y) {
  const c = garante();
  const largura = c.offsetWidth, altura = c.offsetHeight;
  const esq = Math.min(x + 14, window.innerWidth - largura - 8);
  const topo = y + altura + 20 > window.innerHeight ? y - altura - 12 : y + 14;
  c.style.left = `${Math.max(8, esq)}px`;
  c.style.top = `${Math.max(8, topo)}px`;
}

// linhas: [["valor em destaque", "explicação"], ...]
export function mostra(evento, linhas) {
  const c = garante();
  c.replaceChildren(
    ...linhas.map(([forte, fraco]) => {
      const p = document.createElement("div");
      if (forte) { const b = document.createElement("b"); b.textContent = forte; p.append(b); }
      if (fraco) { const s = document.createElement("span"); s.className = "s"; s.textContent = fraco; p.append(s); }
      return p;
    }),
  );
  c.hidden = false;
  if (evento.type === "focus") {
    const r = evento.target.getBoundingClientRect();
    posiciona(r.right, r.top);
  } else {
    posiciona(evento.clientX, evento.clientY);
  }
}

export function esconde() {
  if (caixa) caixa.hidden = true;
}

// Liga o tooltip a um elemento SVG ou HTML (mouse, toque e teclado).
export function interativo(el, linhas) {
  el.setAttribute("tabindex", "0");
  el.classList.add("alvo");
  const f = (e) => mostra(e, linhas());
  el.addEventListener("pointerenter", f);
  el.addEventListener("pointermove", f);
  el.addEventListener("pointerleave", esconde);
  el.addEventListener("focus", f);
  el.addEventListener("blur", esconde);
}
