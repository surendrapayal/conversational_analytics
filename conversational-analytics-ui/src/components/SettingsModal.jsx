import { useState } from 'react';
import { ROLES } from '../api/client';

export default function SettingsModal({ userId, role, onSave, onClose }) {
  const [localUserId, setLocalUserId] = useState(userId);
  const [localRole, setLocalRole] = useState(role);

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
        </div>
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" onClick={() => { onSave(localUserId, localRole); onClose(); }}>
            Save
          </button>
        </div>
      </div>
    </div>
  );
}
