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

// Shodan Lookup (simulado o real)
function shodanLookup() {
  const shodanRes = document.getElementById("shodanResult");
  showLoading(shodanRes);

  const ip = document.getElementById("shodanIp").value;

  fetch(BASE_URL + "/api/shodan", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ip }),
  })
    .then((res) => res.json())
    .then((data) => {
      showResult(shodanRes, JSON.stringify(data, null, 2));
    })
    .catch((err) => {
      showResult(shodanRes, "Error: " + err);
    });
}

// Nmap + Whois Scan
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

async function runLocalScan() {
  const ip = document.getElementById("scanInput").value.trim();
  const runNmap = chkNmap.checked;
  const runWhois = document.getElementById("chkWhois").checked;

  if (!ip) {
    alert("Por favor ingresa una IP o dominio.");
    return;
  }
  if (!runNmap && !runWhois) {
    alert("Selecciona al menos Nmap o Whois para ejecutar.");
    return;
  }

  let nmapParams = "";
  if (runNmap) {
    const customParams = document.getElementById("nmapParams").value.trim();
    const selectParams = document.getElementById("nmapSelect").value;
    nmapParams = customParams || selectParams || "-sV -p 80,443";
  }

  const loader = document.getElementById("loader");
  const nmapTitle = document.getElementById("nmapTitle");
  const whoisTitle = document.getElementById("whoisTitle");
  const nmapResult = document.getElementById("nmapResult");
  const whoisResult = document.getElementById("whoisResult");

  loader.classList.remove("hidden");
  nmapResult.classList.add("hidden");
  whoisResult.classList.add("hidden");
  nmapTitle.classList.add("hidden");
  whoisTitle.classList.add("hidden");

  try {
    const response = await fetch("/api/scan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ip, runNmap, runWhois, nmapParams }),
    });

    const data = await response.json();

    toggleLoadingState(True);

    if (data.error) {
      alert("Error: " + data.error);
      return;
    }

    if (data.nmap_result) {
      nmapTitle.classList.remove("hidden");
      nmapResult.classList.remove("hidden");
      nmapResult.innerText = data.nmap_result;
    }
    if (data.whois_result) {
      whoisTitle.classList.remove("hidden");
      whoisResult.classList.remove("hidden");
      whoisResult.innerText = data.whois_result;
    }
  } catch (error) {
    toggleLoadingState(false);
    alert("Error al consultar: " + error.message);
  }
}

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

//funcion login
function login() {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();
  const resultBox = document.getElementById("loginResult");

  fetch(`${BASE_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ username, password }),
  })
    .then((res) => {
      if (res.redirected) {
        location.href = res.url; // redirige si el backend responde con un redirect
      } else {
        return res.text().then((text) => {
          resultBox.innerText = "Inicio de sesión fallido.";
        });
      }
    })
    .catch((err) => {
      resultBox.innerText = "Error de conexión: " + err;
    });
}
fetch(`${BASE_URL}/protected`).then((res) => {
  if (!res.ok) {
    document.getElementById("loginSection").style.display = "block";
  } else {
    document.getElementById("loginSection").style.display = "none";
  }
});
