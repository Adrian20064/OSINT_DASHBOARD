const toggle = document.getElementById("theme-toggle");
toggle.addEventListener("change", () => {
  document.documentElement.classList.toggle("dark");
});

function fetchWhois() {
  const domain = document.getElementById("whois-input").value;
  document.getElementById(
    "whois-result"
  ).innerText = `Buscando WHOIS de ${domain}...`;
}

function scanEmail() {
  const email = document.getElementById("email-input").value;
  document.getElementById(
    "email-result"
  ).innerText = `Escaneando email ${email}...`;
}

function fetchShodan() {
  const ip = document.getElementById("shodan-ip").value;
  document.getElementById(
    "shodan-result"
  ).innerText = `Consultando Shodan para ${ip}...`;
}

function analyzeHash() {
  document.getElementById("hash-result").innerText = `Analizando archivo...`;
}

function crackHash() {
  const hash = document.getElementById("hash-input").value;
  document.getElementById("crack-result").innerText = `Crackeando ${hash}...`;
}

const cy = cytoscape({
  container: document.getElementById("cy"),

  // Elementos
  elements: [
    { data: { id: "email", label: "Email" } },
    { data: { id: "ip", label: "IP" } },
    { data: { id: "dominio", label: "Dominio" } },
    { data: { source: "email", target: "ip" } },
    { data: { source: "ip", target: "dominio" } },
  ],

  // Estilos
  style: [
    {
      selector: "node",
      style: {
        "background-color": "#3b82f6",
        label: "data(label)",
        color: "#fff",
        "text-valign": "center",
        "text-halign": "center",
      },
    },
    {
      selector: "edge",
      style: {
        width: 2,
        "line-color": "#9ca3af",
        "target-arrow-color": "#9ca3af",
        "target-arrow-shape": "triangle",
      },
    },
  ],

  // Disposición
  layout: {
    name: "grid",
    rows: 1,
    avoidOverlap: true,
    fit: true,
    padding: 10,
  },

  // ⚠️ Control de comportamiento
  userZoomingEnabled: false, // No hacer zoom con scroll
  userPanningEnabled: false, // No arrastrar el fondo
  boxSelectionEnabled: false,
  autoungrabify: true, // ❗ Impide mover nodos manualmente
});
