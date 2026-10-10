// Busca por município: filtra a tabela de municípios (dados/segundo-turno/municipios.json) e,
// ao escolher um, carrega os locais de votação dele (dados/segundo-turno/locais/<código>.json).
import { br, pct, sinal } from "../formato.js";

const norm = (s) => s.normalize("NFD").replace(/\p{Diacritic}/gu, "").toLowerCase();

function linha(celulas) {
  const tr = document.createElement("tr");
  for (const [texto, numero] of celulas) {
    const td = document.createElement("td");
    td.textContent = texto;
    if (numero) td.className = "n";
    tr.append(td);
  }
  return tr;
}

export async function liga(raiz, base) {
  const entrada = raiz.querySelector("input[type=search]");
  const lista = raiz.querySelector("[data-busca-municipios] tbody");
  const locais = raiz.querySelector("[data-busca-locais]");
  const corpoLocais = locais.querySelector("tbody");
  const titulo = locais.querySelector("[data-busca-titulo]");
  const municipios = await (await fetch(`${base}municipios.json`)).json();
  entrada.disabled = false;

  async function mostraLocais(m) {
    const r = await fetch(`${base}locais/${m.cd_ibge}.json`);
    const doMunicipio = r.ok ? await r.json() : [];
    titulo.textContent = `${m.nome} (${m.uf}): ${doMunicipio.length} locais de votação`;
    corpoLocais.replaceChildren(...doMunicipio.slice(0, 200).map((l) => {
      const tr = linha([
        [l.nome, false], [l.bairro ?? "", false], [br(l.aptos, 0), true], [pct(l.abstencao), true],
        [pct(l.p_lula, 0), true], [sinal(l.rendimento_pp, 0), true],
        [l.perdidos == null ? "—" : sinal(l.perdidos, 0), true],
      ]);
      const td = document.createElement("td");
      if (l.lat != null) {
        const a = document.createElement("a");
        a.href = `https://www.openstreetmap.org/?mlat=${l.lat}&mlon=${l.lon}#map=17/${l.lat}/${l.lon}`;
        a.textContent = "mapa";
        a.rel = "noopener";
        a.target = "_blank";
        td.append(a);
      }
      tr.append(td);
      return tr;
    }));
    locais.hidden = false;
  }

  function filtra() {
    const q = norm(entrada.value.trim());
    const achados = q.length < 2 ? [] : municipios.filter((m) => norm(m.nome).includes(q)).slice(0, 12);
    lista.replaceChildren(...achados.map((m) => {
      const tr = linha([
        [`${m.nome} (${m.uf})`, false], [br(m.aptos, 0), true], [pct(m.p_lula, 0), true],
        [pct(m.abstencao), true], [sinal(m.rendimento_pp, 0), true],
        [m.perdidos == null ? "—" : sinal(m.perdidos, 0), true],
      ]);
      tr.tabIndex = 0;
      tr.classList.add("clicavel");
      tr.addEventListener("click", () => mostraLocais(m));
      tr.addEventListener("keydown", (e) => { if (e.key === "Enter") mostraLocais(m); });
      return tr;
    }));
  }
  entrada.addEventListener("input", filtra);
}
