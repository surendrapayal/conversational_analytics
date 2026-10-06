import { useState, useEffect, useRef } from 'react';
import { fetchSessions, fetchSessionDetail } from '../api/client';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import VegaChart from '../components/VegaChart';
import ActivityPanel from '../components/ActivityPanel';
import { useChat } from '../hooks/useChat';

function Pagination({ page, totalPages, onChange }) {
  return (
    <div className="pagination">
      <button className="page-btn" disabled={page <= 1} onClick={() => onChange(page - 1)}>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="15 18 9 12 15 6"/></svg>
        Prev
      </button>
      <span className="page-info">{page} / {totalPages}</span>
      <button className="page-btn" disabled={page >= totalPages} onClick={() => onChange(page + 1)}>
        Next
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="9 18 15 12 9 6"/></svg>
      </button>
    </div>
  );
}

function SessionList({ userId, onSelect, selectedId }) {
  const [data, setData]     = useState(null);
  const [page, setPage]     = useState(1);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    fetchSessions({ userId, page, pageSize: 15 })
      .then(setData).catch(console.error).finally(() => setLoading(false));
  }, [userId, page]);

  return (
    <div className="session-list">
      <div className="session-list-header">
        <span className="section-title">Sessions</span>
        {data && <span className="count-badge">{data.total}</span>}
      </div>
      {loading && <div className="list-loading"><div className="spinner-sm"/></div>}
      {!loading && data?.sessions.map(s => (
        <button
          key={s.session_id}
          className={`session-item ${selectedId === s.session_id ? 'session-item-active' : ''}`}
          onClick={() => onSelect(s.session_id)}
        >
          <div className="session-item-row">
            <span className="session-avatar">{(s.user_id || 'G')[0].toUpperCase()}</span>
            <div className="session-item-info">
              <div className="session-item-top">
                <span className="session-user">{s.user_id}</span>
                {s.role && <span className="role-pill">{s.role}</span>}
              </div>
              <div className="session-item-meta">
                <span>{s.total_conversations} msgs</span>
                <span className="dot-sep">·</span>
                <span>{new Date(s.last_activity).toLocaleDateString()}</span>
              </div>
            </div>
          </div>
        </button>
      ))}
      {data?.total_pages > 1 && <Pagination page={page} totalPages={data.total_pages} onChange={setPage} />}
    </div>
  );
}

function InlineChat({ sessionId, userId, role }) {
  const { messages, streaming, steps, sendMessage } = useChat({ userId, role, sessionId });
  const [input, setInput]   = useState('');
  const [error, setError]   = useState('');
  const bottomRef           = useRef(null);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages, steps]);

  const handleSend = () => {
    const q = input.trim();
    if (!q || streaming) return;
    if (q.length < 5) { setError('Min 5 characters'); return; }
    setError(''); setInput(''); sendMessage(q);
  };

  if (!messages.length) return null;

  return (
    <div className="inline-chat">
      <div className="inline-chat-title">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
        Follow-up conversation
      </div>
      <div className="inline-chat-messages">
        {messages.map(m => (
          <div key={m.id} className={`inline-msg ${m.role === 'user' ? 'inline-msg-user' : 'inline-msg-assistant'}`}>
            <div className="inline-msg-bubble">
              {m.loading
                ? <span className="inline-loading">Thinking…</span>
                : <ReactMarkdown remarkPlugins={[remarkGfm]}>{m.content}</ReactMarkdown>
              }
            </div>
            {m.vegaSpecs && <VegaChart vegaSpecs={m.vegaSpecs} />}
          </div>
        ))}
        {streaming && steps.length > 0 && (
          <div className="inline-steps">{steps[steps.length - 1]}…</div>
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}

function SessionDetail({ sessionId, userId, role }) {
  const [data, setData]       = useState(null);
  const [page, setPage]       = useState(1);
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState(null);
  const [input, setInput]     = useState('');
  const [error, setError]     = useState('');
  const { messages, streaming, steps, sendMessage } = useChat({ userId, role });
  const bottomRef = useRef(null);

  useEffect(() => {
    if (!sessionId) return;
    setLoading(true); setExpanded(null); setData(null);
    fetchSessionDetail({ sessionId, page, pageSize: 10 })
      .then(setData).catch(console.error).finally(() => setLoading(false));
  }, [sessionId, page]);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  if (!sessionId) return (
    <div className="detail-empty">
      <div className="detail-empty-icon">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
      </div>
      <p>Select a session to view its conversations</p>
    </div>
  );

  const handleSend = () => {
    const q = input.trim();
    if (!q || streaming) return;
    if (q.length < 5) { setError('Min 5 characters'); return; }
    setError(''); setInput(''); sendMessage(q);
  };

  return (
    <div className="session-detail">
      {/* Header */}
      {data && (
        <div className="session-detail-header">
          <div className="sdh-left">
            <div className="sdh-avatar">{(data.user_id || 'G')[0].toUpperCase()}</div>
            <div>
              <div className="sdh-title">{data.user_id}</div>
              <div className="sdh-meta">
                {data.role && <span className="role-pill">{data.role}</span>}
                <span className="meta-item">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                  {data.total_conversations} conversations
                </span>
                <span className="meta-item">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                  {new Date(data.last_activity).toLocaleString()}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {loading && <div className="list-loading"><div className="spinner-sm"/></div>}

      {/* Conversation cards */}
      {!loading && data && (
        <div className="conversation-list">
          {data.conversations.map((c, i) => (
            <div key={c.conversation_id} className={`conv-card ${expanded === i ? 'conv-card-open' : ''}`}>
              <button className="conv-card-header" onClick={() => setExpanded(expanded === i ? null : i)}>
                <div className="conv-header-left">
                  <div className="conv-q-badge">Q</div>
                  <span className="conv-question-full">{c.user_query}</span>
                </div>
                <div className="conv-header-right">
                  {c.has_vega && (
                    <span className="chart-badge">
                      <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
                      Chart
                    </span>
                  )}
                  <span className="conv-time">{new Date(c.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                  <span className="conv-date">{new Date(c.created_at).toLocaleDateString()}</span>
                  <span className="conv-ms">{(c.execution_ms / 1000).toFixed(1)}s</span>
                  <svg className={`chevron ${expanded === i ? 'chevron-up' : ''}`} width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="6 9 12 15 18 9"/></svg>
                </div>
              </button>

              {expanded === i && (
                <div className="conv-card-body">
                  <ActivityPanel activity={c.activity} />
                  <div className="conv-response-text">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{c.agent_response}</ReactMarkdown>
                  </div>
                  {c.has_vega && c.vega_spec && (
                    <VegaChart vegaSpecs={[{ chart_type: 'Chart', spec: c.vega_spec }]} />
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {data?.total_pages > 1 && <Pagination page={page} totalPages={data.total_pages} onChange={setPage} />}

      {/* Follow-up chat messages */}
      {messages.length > 0 && (
        <div className="followup-messages">
          <div className="followup-divider">
            <span>Follow-up conversation</span>
          </div>
          {messages.map(m => (
            <div key={m.id} className={`inline-msg ${m.role === 'user' ? 'inline-msg-user' : 'inline-msg-assistant'}`}>
              <div className="inline-msg-bubble">
                {m.loading
                  ? <span className="inline-loading"><div className="spinner-sm"/>Thinking…</span>
                  : <ReactMarkdown remarkPlugins={[remarkGfm]}>{m.content}</ReactMarkdown>
                }
              </div>
              {m.vegaSpecs && <VegaChart vegaSpecs={m.vegaSpecs} />}
            </div>
          ))}
          {streaming && steps.length > 0 && (
            <div className="inline-steps">{steps[steps.length - 1]}…</div>
          )}
          <div ref={bottomRef} />
        </div>
      )}

      {/* Ask question input */}
      {sessionId && (
        <div className="history-input-bar">
          {error && <div className="input-error">{error}</div>}
          <div className="history-input-row">
            <input
              className={`history-input ${error ? 'chat-input-invalid' : ''}`}
              value={input}
              onChange={e => { setInput(e.target.value); if (error) setError(''); }}
              onKeyDown={e => e.key === 'Enter' && handleSend()}
              placeholder="Ask a follow-up question about this session…"
              disabled={streaming}
            />
            <button className="send-btn" onClick={handleSend} disabled={streaming || !input.trim()}>
              {streaming
                ? <div className="spinner-sm" style={{ borderTopColor: 'white' }} />
                : <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
              }
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default function HistoryPage({ userId, role }) {
  const [selectedSession, setSelectedSession] = useState(null);
  return (
    <div className="history-page">
      <div className="page-header">
        <h1 className="page-title">Conversation History</h1>
      </div>
      <div className="history-layout">
        <SessionList userId={userId} onSelect={setSelectedSession} selectedId={selectedSession} />
        <SessionDetail sessionId={selectedSession} userId={userId} role={role} />
      </div>
    </div>
  );
}
