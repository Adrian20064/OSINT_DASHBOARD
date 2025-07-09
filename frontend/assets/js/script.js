const BASE_URL = "https://osint-dashboard.onrender.com";

// Utilidades visuales
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
  const email = document.getElementById("emailInput").value;
  const emailRes = document.getElementById("emailResult");
  showLoading(emailRes);

  fetch(`${BASE_URL}/api/email-check`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  })
    .then(async (res) => {
      const text = await res.text();
      try {
        if (!res.ok) throw new Error(`Error HTTP ${res.status}: ${text}`);
        return JSON.parse(text);
      } catch {
        // Si no es JSON, mostrar texto crudo para depurar
        throw new Error(text);
      }
    })
    .then((data) => showResult(emailRes, JSON.stringify(data, null, 2)))
    .catch((err) => showResult(emailRes, "Error: " + err.message));
}
// File Analysis
function analyzeUploadedFile() {
  const input = document.getElementById("fileUpload");
  const file = input.files[0];
  const uploadRes = document.getElementById("uploadResult");

  if (!file) {
    alert("Selecciona un archivo primero.");
    uploadRes.style.display = "none";
    return;
  }

  showLoading(uploadRes, "Procesando archivo...");

  const reader = new FileReader();
  reader.onload = (event) => {
    const base64Content = event.target.result.split(",")[1];

    fetch(`${BASE_URL}/api/file-analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ filename: file.name, content: base64Content }),
    })
      .then((res) => res.json())
      .then((data) => showResult(uploadRes, JSON.stringify(data, null, 2)))
      .catch((err) => showResult(uploadRes, "Error: " + err));
  };

  reader.readAsDataURL(file);
}

// Hash Generator
function hashText() {
  const text = document.getElementById("hashText").value;
  const algorithm = document.getElementById("hashAlg").value;
  const hashRes = document.getElementById("hashResult");

  showLoading(hashRes);

  fetch(`${BASE_URL}/api/hash`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, algorithm }),
  })
    .then((res) => res.json())
    .then((data) => showResult(hashRes, JSON.stringify(data, null, 2)))
    .catch((err) => showResult(hashRes, "Error: " + err));
}

// Super OSINT (Shodan + Whois + IP-API + DNS)
async function runSuperShodan() {
  const target = document.getElementById("superTarget").value.trim();
  const tools = Array.from(
    document.querySelectorAll('input[name="superTools"]:checked')
  ).map((cb) => cb.value);

  const loader = document.getElementById("superLoader");
  const resultsContainer = document.getElementById("superResults");

  if (!target || tools.length === 0) {
    alert("Completa los campos: objetivo y herramientas.");
    return;
  }

  loader.classList.remove("hidden");
  resultsContainer.classList.add("hidden");

  document.querySelectorAll("#superResults > div").forEach((el) => {
    el.classList.add("hidden");
  });

  try {
    const res = await fetch(`${BASE_URL}/api/super-osint`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ target, tools }),
    });

    const contentType = res.headers.get("content-type") || "";
    const isJson = contentType.includes("application/json");

    if (!res.ok) {
      const text = await res.text();
      throw new Error(`HTTP ${res.status}: ${text.slice(0, 150)}...`);
    }

    if (!isJson) {
      const text = await res.text();
      throw new Error("Respuesta no es JSON. Contenido: " + text.slice(0, 150));
    }

    const data = await res.json();
    loader.classList.add("hidden");

    if (data.error) {
      alert("Error del servidor: " + data.error);
      return;
    }

    const results = data.results || data;
    showSuperResults(results, tools);
  } catch (err) {
    loader.classList.add("hidden");
    console.error("Error en runSuperShodan:", err);
    alert("Error: " + err.message);
  }
}
// Mostrar resultados dinámicos
function showSuperResults(data, tools) {
  const resultsContainer = document.getElementById("superResults");

  const showToolResult = (id, content) => {
    const container = document.getElementById(id);
    if (container) {
      container.querySelector("pre").textContent =
        typeof content === "string"
          ? content
          : JSON.stringify(content, null, 2);
      container.classList.remove("hidden");
    }
  };

  if (tools.includes("theharvester") && data.theharvester)
    showToolResult("theharvesterResult", data.theharvester);

  if (tools.includes("nmap") && data.nmap)
    showToolResult("nmapResult", data.nmap);

  if (tools.includes("whois") && data.whois)
    showToolResult("whoisResult", data.whois);

  if (tools.includes("dns") && data.dns) {
    let container = document.getElementById("dnsResult");
    if (!container) {
      container = document.createElement("div");
      container.id = "dnsResult";
      container.className = "bg-gray-100 rounded-md p-4";
      document.getElementById("superResults").appendChild(container);
    }
    container.innerHTML = `
      <h3 class="font-bold text-red-600 mb-2">DNS Lookup</h3>
      <pre class="max-h-48 overflow-auto text-sm">${JSON.stringify(
        data.dns,
        null,
        2
      )}</pre>
    `;
    container.classList.remove("hidden");
  }

  resultsContainer.classList.remove("hidden");
}

// Nmap toggle
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

// DOM Ready
document.addEventListener("DOMContentLoaded", () => {
  setupNmapToggle();
});

//modo oscuro
function toggleDarkMode() {
  document.documentElement.classList.toggle("dark");
}

//creador de contraseñas seguras
function generateSecurePassword() {
  const length = parseInt(document.getElementById("passwordLength").value);
  const includeUpper = document.getElementById("includeUppercase").checked;
  const includeLower = document.getElementById("includeLowercase").checked;
  const includeNumbers = document.getElementById("includeNumbers").checked;
  const includeSymbols = document.getElementById("includeSymbols").checked;

  let charset = "";
  if (includeLower) charset += "abcdefghijklmnopqrstuvwxyz";
  if (includeUpper) charset += "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
  if (includeNumbers) charset += "0123456789";
  if (includeSymbols) charset += "!@#$%^&*()-_=+[]{};:,.<>?";

  if (!charset) {
    alert("Selecciona al menos una opción de carácter.");
    return;
  }

  let password = "";
  for (let i = 0; i < length; i++) {
    password += charset.charAt(Math.floor(Math.random() * charset.length));
  }

  document.getElementById("generatedPassword").innerText = password;
  document.getElementById("passwordOutput").classList.remove("hidden");
}

function copyPassword() {
  const passText = document.getElementById("generatedPassword").innerText;
  navigator.clipboard.writeText(passText).then(() => {
    alert("¡Contraseña copiada al portapapeles!");
  });
}

//Verificador de contraseñas (fortaleza)
function checkPasswordStrength() {
  const input = document.getElementById("passwordStrengthInput");
  const bar = document.getElementById("passwordStrengthBar");
  const text = document.getElementById("passwordStrengthText");
  const result = zxcvbn(input.value);

  const strengthLevels = [
    { text: "Muy débil 😟", color: "bg-red-500", width: "20%" },
    { text: "Débil 😕", color: "bg-orange-400", width: "40%" },
    { text: "Regular 😐", color: "bg-yellow-400", width: "60%" },
    { text: "Fuerte 🙂", color: "bg-green-500", width: "80%" },
    { text: "Muy fuerte 😎", color: "bg-green-700", width: "100%" },
  ];

  const level = strengthLevels[result.score];

  bar.className = `h-2 rounded-md transition-all duration-300 ease-in-out ${level.color}`;
  bar.style.width = level.width;
  text.textContent = `${level.text} (${result.score}/4) - ${
    result.feedback.suggestions.join(" ") || "Buena contraseña."
  }`;
}

//Verificador de contraseñas si han sifo filtradas

function checkPasswordLeak() {
  const password = document.getElementById("passwordInput").value.trim();
  const result = document.getElementById("passwordLeakResult");
  if (!password) {
    alert("Por favor ingresa una contraseña.");
    return;
  }

  result.textContent = "Consultando base de datos...";

  fetch(`${BASE_URL}/api/check-password-leak`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ password }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.error) {
        result.textContent = `Error: ${data.error}`;
      } else if (data.leaked) {
        result.textContent = `⚠️ ¡Atención! La contraseña ha sido filtrada ${data.count} veces.\n\n${data.message}`;
      } else {
        result.textContent = `✅ La contraseña no fue encontrada en bases públicas.\n\n${data.message}`;
      }
    })
    .catch((err) => {
      result.textContent = `Error: ${err.message}`;
    });
}
