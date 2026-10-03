import { useEffect, useRef, useState } from 'react';
import ChatMessage from '../components/ChatMessage';
import StepIndicator from '../components/StepIndicator';
import { useChat } from '../hooks/useChat';

const SUGGESTIONS = [
  'What is the net sales in each location?',
  'Show top 10 best-selling menu items',
  'What is the table utilization rate by location?',
  'Revenue trend over the last 30 days',
];

export default function ChatPage({ userId, role }) {
  const { messages, streaming, steps, sendMessage, clearChat } = useChat({ userId, role });
  const [input, setInput] = useState('');
  const [validationError, setValidationError] = useState('');
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, steps]);

  const handleSend = () => {
    const q = input.trim();
    if (!q || streaming) return;
    if (q.length < 5) {
      setValidationError('Query must be at least 5 characters.');
      return;
    }
    setValidationError('');
    setInput('');
    sendMessage(q);
  };

  const handleKey = e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  const handleInputChange = e => {
    setInput(e.target.value);
    if (validationError) setValidationError('');
  };

  return (
    <div className="chat-page">
      <div className="chat-header">
        <h1 className="chat-title">Conversational Analytics</h1>
        {messages.length > 0 && (
          <button className="btn btn-ghost" onClick={clearChat}>New Chat</button>
        )}
      </div>

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="chat-empty">
            <div className="empty-icon">📊</div>
            <h2>Ask anything about your restaurant data</h2>
            <p>Query sales, inventory, reservations, employees and more using natural language.</p>
            <div className="suggestions">
              {SUGGESTIONS.map((s, i) => (
                <button key={i} className="suggestion-chip" onClick={() => sendMessage(s)}>{s}</button>
              ))}
            </div>
          </div>
        ) : (
          messages.map(msg => <ChatMessage key={msg.id} message={msg} />)
        )}
        {streaming && <StepIndicator steps={steps} />}
        <div ref={bottomRef} />
      </div>

      <div className="chat-input-bar">
        <div className="chat-input-wrapper">
          {validationError && <div className="input-error">{validationError}</div>}
          <div className="chat-input-row">
            <textarea
              className={`chat-input ${validationError ? 'chat-input-invalid' : ''}`}
              value={input}
              onChange={handleInputChange}
              onKeyDown={handleKey}
              placeholder="Ask a question about your data... (min 5 characters)"
              rows={1}
              disabled={streaming}
            />
            <button
              className={`send-btn ${streaming ? 'send-btn-disabled' : ''}`}
              onClick={handleSend}
              disabled={streaming || !input.trim()}
            >
              {streaming ? '⏳' : '➤'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
