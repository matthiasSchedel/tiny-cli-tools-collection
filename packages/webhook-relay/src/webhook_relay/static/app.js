const rows = document.getElementById("rows");
const details = document.getElementById("details");
const refresh = document.getElementById("refresh");
let pollTimer = null;

async function fetchRequests() {
  const response = await fetch("/_relay/requests");
  const data = await response.json();
  rows.innerHTML = "";
  data.forEach((item) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${item.id}</td><td>${item.method}</td><td>${item.path}</td><td>${item.timestamp}</td>`;
    tr.addEventListener("click", () => {
      details.textContent = JSON.stringify(item, null, 2);
    });
    rows.appendChild(tr);
  });
}

refresh.addEventListener("click", fetchRequests);
fetchRequests();

function startPolling() {
  if (pollTimer !== null) return;
  pollTimer = window.setInterval(fetchRequests, 2000);
}

function connectWebSocket() {
  const protocol = location.protocol === "https:" ? "wss" : "ws";
  const ws = new WebSocket(`${protocol}://${location.host}/_relay/ws`);
  ws.addEventListener("message", fetchRequests);
  ws.addEventListener("error", startPolling);
  ws.addEventListener("close", startPolling);
}

async function initRealtime() {
  try {
    const response = await fetch("/_relay/capabilities");
    if (!response.ok) {
      startPolling();
      return;
    }
    const capabilities = await response.json();
    if (capabilities.websocket) {
      connectWebSocket();
      return;
    }
  } catch {
    // Fall back to polling when capability probing fails.
  }
  startPolling();
}

initRealtime();
