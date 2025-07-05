const BASE_URL = "http://127.0.0.1:5000";
const chkNmap = document.getElementById("chkNmap");
const nmapParamsDiv = document.getElementById("nmapParamsDiv");

function showLoading(element, message = "Cargando...") {
  element.classList.remove("animate__fadeIn", "opacity-100");
  element.classList.add("opacity-50");
  element.innerText = message;
  element.style.display = "block";
}

function showResult(element, content) {
  element.innerText = content;
  element.classList.remove("opacity-50");
  element.classList.add("animate__animated", "animate__fadeIn", "opacity-100");
  element.style.display = "block";
}

// Email Checker
function checkEmail() {
  const emailRes = document.getElementById("emailResult");
  showLoading(emailRes);

  const email = document.getElementById("emailInput").value;
  fetch(BASE_URL + "/api/email-check", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  })
    .then((res) => res.json())
    .then((data) => {
      showResult(emailRes, JSON.stringify(data, null, 2));
    })
    .catch((err) => {
      showResult(emailRes, "Error: " + err);
    });
}

// File Analysis
function analyzeUploadedFile() {
  const uploadRes = document.getElementById("uploadResult");
  const input = document.getElementById("fileUpload");
  const file = input.files[0];

  if (!file) {
    alert("Selecciona un archivo primero.");
    uploadRes.style.display = "none";
    return;
  }

  showLoading(uploadRes, "Procesando archivo...");

  const reader = new FileReader();
  reader.onload = function (event) {
    const base64Content = event.target.result.split(",")[1];

    fetch(BASE_URL + "/api/file-analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        filename: file.name,
        content: base64Content,
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        showResult(uploadRes, JSON.stringify(data, null, 2));
      })
      .catch((err) => {
        showResult(uploadRes, "Error: " + err);
      });
  };
  reader.readAsDataURL(file);
}

// Hash Generator
function hashText() {
  const hashRes = document.getElementById("hashResult");
  showLoading(hashRes);

  const text = document.getElementById("hashText").value;
  const algorithm = document.getElementById("hashAlg").value;

  fetch(BASE_URL + "/api/hash", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, algorithm }),
  })
    .then((res) => res.json())
    .then((data) => {
      showResult(hashRes, JSON.stringify(data, null, 2));
    })
    .catch((err) => {
      showResult(hashRes, "Error: " + err);
    });
}
//SuperSHODAN
// Función para ejecutar SuperShodan (OSINT integrado)
async function runSuperShodan() {
  const target = document.getElementById("superTarget").value.trim();
  const checkboxes = document.querySelectorAll(
    'input[name="superTools"]:checked'
  );
  const tools = Array.from(checkboxes).map((cb) => cb.value);

  const loader = document.getElementById("superLoader");
  const resultsContainer = document.getElementById("superResults");

  // Validación
  if (!target) {
    alert("Por favor ingresa una IP, dominio o email.");
    return;
  }
  if (tools.length === 0) {
    alert("Selecciona al menos una herramienta.");
    return;
  }

  // Mostrar loader y ocultar resultados anteriores
  loader.classList.remove("hidden");
  resultsContainer.classList.add("hidden");

  // Ocultar todos los resultados individuales
  document.querySelectorAll("#superResults > div").forEach((el) => {
    el.classList.add("hidden");
  });

  try {
    const response = await fetch(BASE_URL + "/api/super-osint", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ target, tools }),
    });

    const data = await response.json();

    // Ocultar loader
    loader.classList.add("hidden");

    if (data.error) {
      alert("Error: " + data.error);
      return;
    }

    // Mostrar los resultados de cada herramienta
    if (tools.includes("theharvester") && data.theharvester) {
      const container = document.getElementById("theharvesterResult");
      container.querySelector("pre").textContent = JSON.stringify(
        data.theharvester,
        null,
        2
      );
      container.classList.remove("hidden");
    }

    if (tools.includes("nmap") && data.nmap) {
      const container = document.getElementById("nmapResult");
      container.querySelector("pre").textContent =
        typeof data.nmap === "string"
          ? data.nmap
          : JSON.stringify(data.nmap, null, 2);
      container.classList.remove("hidden");
    }

    if (tools.includes("whois") && data.whois) {
      const container = document.getElementById("whoisResult");
      container.querySelector("pre").textContent =
        typeof data.whois === "string"
          ? data.whois
          : JSON.stringify(data.whois, null, 2);
      container.classList.remove("hidden");
    }

    if (tools.includes("dns") && data.dns) {
      // Si agregaste un contenedor para DNS
      const container =
        document.getElementById("dnsResult") || document.createElement("div");
      container.innerHTML = `
        <h3 class="font-bold text-red-600 mb-2">DNS Lookup</h3>
        <pre class="max-h-48 overflow-auto text-sm">${JSON.stringify(
          data.dns,
          null,
          2
        )}</pre>
      `;
      container.className = "bg-gray-100 rounded-md p-4";
      resultsContainer.appendChild(container);
      container.classList.remove("hidden");
    }

    // Mostrar el contenedor de resultados
    resultsContainer.classList.remove("hidden");
  } catch (error) {
    loader.classList.add("hidden");
    alert("Error al consultar: " + error.message);
    console.error("Error en runSuperShodan:", error);
  }
}

// Función para mostrar/ocultar parámetros de Nmap (si decides mantener esta funcionalidad)
function setupNmapToggle() {
  const chkNmap = document.getElementById("chkNmap");
  const nmapParamsDiv = document.getElementById("nmapParamsDiv");

  if (chkNmap && nmapParamsDiv) {
    chkNmap.addEventListener("change", () => {
      if (chkNmap.checked) {
        nmapParamsDiv.classList.remove("hidden");
        nmapParamsDiv.style.maxHeight = nmapParamsDiv.scrollHeight + "px";
      } else {
        nmapParamsDiv.style.maxHeight = "0";
        setTimeout(() => nmapParamsDiv.classList.add("hidden"), 500);
        document.getElementById("nmapSelect").value = "";
        document.getElementById("nmapParams").value = "";
      }
    });
  }
}

// Inicialización cuando el DOM esté cargado
document.addEventListener("DOMContentLoaded", function () {
  setupNmapToggle(); // Solo si mantienes esta funcionalidad
});
//carga
function toggleLoadingState(isLoading) {
  const button = document.querySelector("button");
  const loader = document.getElementById("loader");

  if (isLoading) {
    button.disabled = true;
    button.innerHTML = `<span class="spinner"></span> Consultando...`;
    loader.classList.remove("hidden");
  } else {
    button.disabled = false;
    button.innerText = "Consultar";
    loader.classList.add("hidden");
  }
}
