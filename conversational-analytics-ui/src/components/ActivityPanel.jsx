import { useState } from 'react';

const ACTIVITY_META = {
  step: { icon: '➡️', label: 'Step' },
  thinking: { icon: '💭', label: 'Thinking' },
  tool_call: { icon: '🛠️', label: 'Tool call' },
  tool_result: { icon: '📦', label: 'Tool result' },
};

function ActivityItem({ entry }) {
  const meta = ACTIVITY_META[entry.type] || { icon: '•', label: entry.type };

  let detail = null;
  if (entry.type === 'step') {
    detail = <div className="activity-text">{entry.message}</div>;
  } else if (entry.type === 'thinking') {
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

/**
 * Collapsible activity timeline.
 * @param {Object[]} activity - array of activity entries
 * @param {boolean}  live     - true while the message is still streaming;
 *                              auto-expands and shows a "working" indicator.
 */
export default function ActivityPanel({ activity, live = false }) {
  // null = user hasn't toggled; fall back to auto behaviour (open while live).
  const [userOpen, setUserOpen] = useState(null);
  const open = userOpen === null ? live : userOpen;

  if (!activity || activity.length === 0) return null;

  return (
    <div className="activity-panel">
      <button className="activity-toggle" onClick={() => setUserOpen(!open)}>
        <span className={`activity-caret ${open ? 'open' : ''}`}>▶</span>
        {open ? 'Hide' : 'Show'} reasoning &amp; steps ({activity.length})
        {live && <span className="activity-live-dot" />}
      </button>
      {open && (
        <div className="activity-list">
          {activity.map((entry, i) => <ActivityItem key={entry.id ?? i} entry={entry} />)}
          {live && (
            <div className="activity-item activity-working">
              <div className="activity-head">
                <span className="activity-icon"><span className="step-spinner" /></span>
                <span className="activity-label">Working…</span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
