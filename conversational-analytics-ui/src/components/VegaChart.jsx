import { useEffect, useRef, useState } from 'react';
import embed from 'vega-embed';
import { baseName, exportChartImage } from '../utils/exportUtils';
import { exportConversationData } from '../api/client';

/**
 * Chart image export (PNG/SVG) is produced client-side from the rendered Vega view.
 * Table data export (CSV/Excel/PDF) is delegated to the backend, which re-runs the
 * conversation's stored SQL and streams an authoritative, RBAC-filtered, audited file.
 * (See docs/ADR-export.md — Option B.)
 */
export default function VegaChart({ vegaSpecs, conversationId, userId, role }) {
  const containerRef = useRef(null);
  const viewRef = useRef(null);
  const [selectedIdx, setSelectedIdx] = useState(0);
  const [exportError, setExportError] = useState('');
  const [busyFormat, setBusyFormat] = useState('');

  const current = vegaSpecs?.[selectedIdx];
  const spec = current?.spec;
  const label = current?.chart_type || 'chart';

  useEffect(() => {
    if (!containerRef.current || !spec) return;
    let cancelled = false;
    embed(containerRef.current, spec, {
      actions: { export: true, source: false, compiled: false, editor: false },
      theme: 'dark',
    })
      .then(result => {
        if (!cancelled) viewRef.current = result.view;
      })
      .catch(console.error);
    return () => { cancelled = true; };
  }, [spec]);

  if (!vegaSpecs?.length) return null;

  // Chart image → frontend (the rendered chart only exists client-side).
  const handleChartExport = async (format) => {
    setExportError('');
    try {
      await exportChartImage(viewRef.current, format, baseName(label));
    } catch (e) {
      console.error(`Chart ${format} export failed:`, e);
      setExportError(`Chart ${format.toUpperCase()} export failed: ${e.message}`);
    }
  };

  // Table data → backend (authoritative SQL result, audited).
  const handleDataExport = async (format) => {
    setExportError('');
    setBusyFormat(format);
    try {
      await exportConversationData({ conversationId, format, userId, role });
    } catch (e) {
      console.error(`Data ${format} export failed:`, e);
      setExportError(`Data export failed: ${e.message}`);
    } finally {
      setBusyFormat('');
    }
  };

  return (
    <div className="vega-wrapper">
      {vegaSpecs.length > 1 && (
        <div className="chart-switcher">
          <span className="chart-switcher-label">Chart type:</span>
          <select
            value={selectedIdx}
            onChange={e => setSelectedIdx(Number(e.target.value))}
            className="chart-select"
          >
            {vegaSpecs.map((v, i) => (
              <option key={i} value={i}>{v.chart_type}</option>
            ))}
          </select>
        </div>
      )}

      <div ref={containerRef} className="vega-container" />

      <div className="export-bar">
        <span className="export-group">
          <span className="export-label">Chart:</span>
          <button className="export-btn" onClick={() => handleChartExport('png')}>PNG</button>
          <button className="export-btn" onClick={() => handleChartExport('svg')}>SVG</button>
        </span>
        {conversationId && (
          <span className="export-group">
            <span className="export-label">Data:</span>
            <button className="export-btn" disabled={!!busyFormat} onClick={() => handleDataExport('csv')}>
              {busyFormat === 'csv' ? '…' : 'CSV'}
            </button>
            <button className="export-btn" disabled={!!busyFormat} onClick={() => handleDataExport('xlsx')}>
              {busyFormat === 'xlsx' ? '…' : 'Excel'}
            </button>
            <button className="export-btn" disabled={!!busyFormat} onClick={() => handleDataExport('pdf')}>
              {busyFormat === 'pdf' ? '…' : 'PDF'}
            </button>
          </span>
        )}
      </div>
      {exportError && <div className="export-error">{exportError}</div>}
    </div>
  );
}
