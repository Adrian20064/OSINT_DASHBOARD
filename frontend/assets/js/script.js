const BASE_URL = "http://127.0.0.1:5000";

function checkEmail() {
  const email = document.getElementById("emailInput").value;
  fetch(BASE_URL + "/api/email-check", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  })
    .then((res) => res.json())
    .then((data) => {
      document.getElementById("emailResult").innerText = JSON.stringify(
        data,
        null,
        2
      );
    })
    .catch((err) => {
      document.getElementById("emailResult").innerText = "Error: " + err;
    });
}

function analyzeUploadedFile() {
  const input = document.getElementById("fileUpload");
  const file = input.files[0];

  if (!file) {
    alert("Selecciona un archivo primero.");
    return;
  }

  const reader = new FileReader();
  reader.onload = function (event) {
    const base64Content = event.target.result.split(",")[1]; // extraer solo la base64

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
        document.getElementById("uploadResult").innerText = JSON.stringify(
          data,
          null,
          2
        );
      })
      .catch((err) => {
        document.getElementById("uploadResult").innerText = "Error: " + err;
      });
  };

  reader.readAsDataURL(file); // lee el archivo y lo convierte en dataURL base64
}

function hashText() {
  const text = document.getElementById("hashText").value;
  fetch(BASE_URL + "/api/hash", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  })
    .then((res) => res.json())
    .then((data) => {
      document.getElementById("hashResult").innerText = JSON.stringify(
        data,
        null,
        2
      );
    })
    .catch((err) => {
      document.getElementById("hashResult").innerText = "Error: " + err;
    });
}

function shodanLookup() {
  const ip = document.getElementById("shodanIp").value;
  fetch(BASE_URL + "/api/shodan", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ip }),
  })
    .then((res) => res.json())
    .then((data) => {
      document.getElementById("shodanResult").innerText = JSON.stringify(
        data,
        null,
        2
      );
    })
    .catch((err) => {
      document.getElementById("shodanResult").innerText = "Error: " + err;
    });
}

function runLocalScan() {
  const ip = document.getElementById("scanInput").value;

  fetch(BASE_URL + "/api/scan", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ip }),
  })
    .then((res) => res.json())
    .then((data) => {
      document.getElementById("nmapResult").innerText =
        data.nmap_result || "No Nmap";
      document.getElementById("whoisResult").innerText =
        data.whois_result || "No Whois";
    })
    .catch((err) => {
      document.getElementById("nmapResult").innerText = "Error: " + err;
      document.getElementById("whoisResult").innerText = "Error: " + err;
    });
}

function hashText() {
  const text = document.getElementById("hashText").value;
  const algorithm = document.getElementById("hashAlg").value;

  fetch("/api/hash", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: text, algorithm: algorithm }),
  })
    .then((res) => res.json())
    .then((data) => {
      document.getElementById("hashResult").innerText = JSON.stringify(
        data,
        null,
        2
      );
    })
    .catch((err) => {
      document.getElementById("hashResult").innerText = "Error: " + err;
    });
}
