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

export async function fetchSessionDetail({ sessionId, page = 1, pageSize = 20 }) {
  const params = new URLSearchParams({ page, page_size: pageSize });
  const res = await fetch(`${BASE_URL}/api/v1/sessions/${sessionId}?${params}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}
