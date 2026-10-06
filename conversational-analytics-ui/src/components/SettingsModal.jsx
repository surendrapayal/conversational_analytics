import { useState } from 'react';
import { ROLES, STREAM_MODES } from '../api/client';

const STREAM_MODE_HELP = {
  standard: 'Concise progress updates while the agent works.',
  verbose: 'Detailed step-by-step reasoning and tool activity.',
};

export default function SettingsModal({ userId, role, streamMode, onSave, onClose }) {
  const [localUserId, setLocalUserId] = useState(userId);
  const [localRole, setLocalRole] = useState(role);
  const [localStreamMode, setLocalStreamMode] = useState(streamMode || 'standard');

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Settings</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">
          <label className="form-label">User ID</label>
          <input
            className="form-input"
            value={localUserId}
            onChange={e => setLocalUserId(e.target.value)}
            placeholder="e.g. admin"
          />
          <label className="form-label" style={{ marginTop: '1rem' }}>Role</label>
          <select className="form-input" value={localRole} onChange={e => setLocalRole(e.target.value)}>
            <option value="">No role</option>
            {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
          </select>
          <label className="form-label" style={{ marginTop: '1rem' }}>Stream Mode</label>
          <select
            className="form-input"
            value={localStreamMode}
            onChange={e => setLocalStreamMode(e.target.value)}
          >
            {STREAM_MODES.map(m => (
              <option key={m} value={m}>{m.charAt(0).toUpperCase() + m.slice(1)}</option>
            ))}
          </select>
          <p className="form-hint">{STREAM_MODE_HELP[localStreamMode]}</p>
        </div>
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" onClick={() => { onSave(localStreamMode); onClose(); }}>
            Save
          </button>
        </div>
      </div>
    </div>
  );
}
