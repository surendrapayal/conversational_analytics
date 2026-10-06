import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import VegaChart from './VegaChart';

const ACTIVITY_META = {
  thinking: { icon: '💭', label: 'Thinking' },
  tool_call: { icon: '🛠️', label: 'Tool call' },
  tool_result: { icon: '📦', label: 'Tool result' },
};

function ActivityItem({ entry }) {
  const meta = ACTIVITY_META[entry.type] || { icon: '•', label: entry.type };

  let detail = null;
  if (entry.type === 'thinking') {
    detail = <div className="activity-text">{entry.reasoning}</div>;
  } else if (entry.type === 'tool_call') {
    detail = (
      <pre className="activity-code">
        {entry.tool}({JSON.stringify(entry.args, null, 2)})
      </pre>
    );
  } else if (entry.type === 'tool_result') {
    const output = typeof entry.output === 'string'
      ? entry.output
      : JSON.stringify(entry.output, null, 2);
    detail = <pre className="activity-code">{output}</pre>;
  }

  return (
    <div className="activity-item">
      <div className="activity-head">
        <span className="activity-icon">{meta.icon}</span>
        <span className="activity-label">{meta.label}</span>
        {entry.tool && <span className="activity-tool">{entry.tool}</span>}
      </div>
      {detail}
    </div>
  );
}

function ActivityPanel({ activity }) {
  const [open, setOpen] = useState(false);
  if (!activity || activity.length === 0) return null;

  return (
    <div className="activity-panel">
      <button className="activity-toggle" onClick={() => setOpen(o => !o)}>
        <span className={`activity-caret ${open ? 'open' : ''}`}>▶</span>
        {open ? 'Hide' : 'Show'} reasoning &amp; steps ({activity.length})
      </button>
      {open && (
        <div className="activity-list">
          {activity.map(entry => <ActivityItem key={entry.id} entry={entry} />)}
        </div>
      )}
    </div>
  );
}

export default function ChatMessage({ message }) {
  const isUser = message.role === 'user';

  return (
    <div className={`message ${isUser ? 'message-user' : 'message-assistant'} ${message.error ? 'message-error' : ''}`}>
      <div className="message-avatar">{isUser ? '👤' : '🤖'}</div>
      <div className="message-body">
        {!isUser && <ActivityPanel activity={message.activity} />}
        {message.loading ? (
          <div className="message-loading">
            <span className="dot" /><span className="dot" /><span className="dot" />
          </div>
        ) : (
          <>
            <div className="message-content">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
            </div>
            {message.vegaSpecs && <VegaChart vegaSpecs={message.vegaSpecs} />}
          </>
        )}
      </div>
    </div>
  );
}
