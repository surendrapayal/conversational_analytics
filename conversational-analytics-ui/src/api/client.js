const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const ROLES = ['admin', 'general_manager', 'location_manager', 'chef', 'waiter', 'cashier', 'analyst'];

export const STREAM_MODES = ['standard', 'verbose'];

export async function* streamQuery({ userId, query, sessionId, role, streamMode = 'standard' }) {
  const res = await fetch(`${BASE_URL}/api/v1/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(sessionId && { 'X-Session-Id': sessionId }),
      ...(role && { role }),
    },
    body: JSON.stringify({ user_id: userId, query, stream_mode: streamMode }),
  });

  if (!res.ok) throw new Error(`HTTP ${res.status}`);

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop();
    let event = null;
    for (const line of lines) {
      if (line.startsWith('event:')) event = line.slice(6).trim();
      if (line.startsWith('data:')) {
        try {
          const data = JSON.parse(line.slice(5).trim());
          yield { event, data };
        } catch { /* skip malformed */ }
      }
    }
  }
}

export async function fetchSessions({ userId, page = 1, pageSize = 20 }) {
  const params = new URLSearchParams({ page, page_size: pageSize });
  if (userId) params.set('user_id', userId);
  const res = await fetch(`${BASE_URL}/api/v1/sessions?${params}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function fetchSessionDetail({ sessionId, page = 1, pageSize = 20, streamMode = 'standard' }) {
  const params = new URLSearchParams({ page, page_size: pageSize, stream_mode: streamMode });
  const res = await fetch(`${BASE_URL}/api/v1/sessions/${sessionId}?${params}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

// Backend-owned data export (CSV / Excel / PDF). The server re-runs the stored
// query and streams an authoritative file; we just download it.
export const DATA_EXPORT_FORMATS = ['csv', 'xlsx', 'pdf'];

function parseFilename(contentDisposition, fallback) {
  if (!contentDisposition) return fallback;
  // Prefer RFC 5987 filename*=UTF-8''...
  const star = /filename\*=UTF-8''([^;]+)/i.exec(contentDisposition);
  if (star) { try { return decodeURIComponent(star[1]); } catch { /* ignore */ } }
  const plain = /filename="?([^";]+)"?/i.exec(contentDisposition);
  return plain ? plain[1] : fallback;
}

export async function exportConversationData({ conversationId, format, userId, role }) {
  const params = new URLSearchParams({ format });
  if (userId) params.set('user_id', userId);
  const res = await fetch(
    `${BASE_URL}/api/v1/conversations/${conversationId}/export?${params}`,
    { headers: { ...(role && { role }) } },
  );
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try { detail = (await res.json()).detail || detail; } catch { /* ignore */ }
    throw new Error(detail);
  }
  const blob = await res.blob();
  const filename = parseFilename(
    res.headers.get('Content-Disposition'),
    `export.${format === 'xlsx' ? 'xlsx' : format}`,
  );
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
