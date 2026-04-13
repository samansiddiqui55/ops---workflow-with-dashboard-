const API_BASE = process.env.REACT_APP_BACKEND_URL
  ? `${process.env.REACT_APP_BACKEND_URL}/api`
  : "/api";

// WebSocket URL - derive from backend URL
const WS_BASE = process.env.REACT_APP_BACKEND_URL
  ? process.env.REACT_APP_BACKEND_URL.replace("https://", "wss://").replace("http://", "ws://")
  : `ws://${window.location.host}`;

export function createTicketWebSocket(onMessage) {
  const wsUrl = `${WS_BASE}/api/ws/tickets`;
  let ws = null;
  let reconnectTimeout = null;
  let pingInterval = null;

  function connect() {
    try {
      ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log("WebSocket connected");
        // Send ping every 30 seconds to keep alive
        pingInterval = setInterval(() => {
          if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send("ping");
          }
        }, 30000);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type !== "pong") {
            onMessage(data);
          }
        } catch (e) {
          console.error("WebSocket parse error:", e);
        }
      };

      ws.onclose = () => {
        console.log("WebSocket disconnected, reconnecting in 5s...");
        clearInterval(pingInterval);
        reconnectTimeout = setTimeout(connect, 5000);
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
      };
    } catch (e) {
      console.error("WebSocket connection failed:", e);
      reconnectTimeout = setTimeout(connect, 5000);
    }
  }

  connect();

  // Return cleanup function
  return () => {
    clearInterval(pingInterval);
    clearTimeout(reconnectTimeout);
    if (ws) {
      ws.close();
    }
  };
}

export async function fetchTickets() {
  const response = await fetch(`${API_BASE}/tickets/`);

  if (!response.ok) {
    throw new Error("Failed to fetch tickets");
  }

  return await response.json();
}

export async function resolveTicket(ticketId, payload) {
  const response = await fetch(`${API_BASE}/tickets/${ticketId}/resolve`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("Failed to resolve ticket");
  }

  return await response.json();
}

// Analytics endpoints
export async function fetchAnalyticsSummary(period = "all") {
  const url = period === "all" 
    ? `${API_BASE}/analytics/summary`
    : `${API_BASE}/analytics/summary?period=${period}`;
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error("Failed to fetch analytics");
  }

  return await response.json();
}

export async function fetchIssuesByClient(period = "1m") {
  const response = await fetch(`${API_BASE}/analytics/issues-by-client?period=${period}`);

  if (!response.ok) {
    throw new Error("Failed to fetch issues by client");
  }

  return await response.json();
}

export async function fetchIssueTypes(period = "1m") {
  const response = await fetch(`${API_BASE}/analytics/issue-types?period=${period}`);

  if (!response.ok) {
    throw new Error("Failed to fetch issue types");
  }

  return await response.json();
}

export async function fetchTimeSeries(period = "1m") {
  const response = await fetch(`${API_BASE}/analytics/time-series?period=${period}`);

  if (!response.ok) {
    throw new Error("Failed to fetch time series");
  }

  return await response.json();
}

export async function triggerEmailPoll() {
  const response = await fetch(`${API_BASE}/test/email-poll`, {
    method: "POST",
  });

  if (!response.ok) {
    throw new Error("Failed to trigger email poll");
  }

  return await response.json();
}
