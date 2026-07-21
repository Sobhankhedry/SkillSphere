let ws: WebSocket | null = null;
let reconnectTimer: ReturnType<typeof setTimeout> | null = null;

type NotificationCallback = (data: {
  id: string;
  type: string;
  title: string;
  message: string;
  link: string;
  created_at: string;
}) => void;

export function connectWebSocket(
  token: string,
  onNotification: NotificationCallback
) {
  if (ws && ws.readyState === WebSocket.OPEN) return;

  const wsUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws/notifications/";
  ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    console.log("WebSocket connected");
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onNotification(data);
    } catch {
      // ignore parse errors
    }
  };

  ws.onclose = () => {
    console.log("WebSocket disconnected, reconnecting in 5s...");
    if (reconnectTimer) clearTimeout(reconnectTimer);
    reconnectTimer = setTimeout(() => {
      if (token) connectWebSocket(token, onNotification);
    }, 5000);
  };

  ws.onerror = () => {
    ws?.close();
  };
}

export function disconnectWebSocket() {
  if (reconnectTimer) clearTimeout(reconnectTimer);
  if (ws) {
    ws.close();
    ws = null;
  }
}
