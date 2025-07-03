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

function analyzeFile() {
  const content = document.getElementById("fileContent").value;
  fetch(BASE_URL + "/api/file-analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content }),
  })
    .then((res) => res.json())
    .then((data) => {
      document.getElementById("fileResult").innerText = JSON.stringify(
        data,
        null,
        2
      );
    })
    .catch((err) => {
      document.getElementById("fileResult").innerText = "Error: " + err;
    });
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

function whoisLookup() {
  const domain = document.getElementById("whoisDomain").value;
  fetch(BASE_URL + "/api/whois", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ domain }),
  })
    .then((res) => res.json())
    .then((data) => {
      document.getElementById("whoisResult").innerText = JSON.stringify(
        data,
        null,
        2
      );
    })
    .catch((err) => {
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
