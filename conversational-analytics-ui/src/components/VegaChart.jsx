import { useEffect, useRef, useState } from 'react';
import embed from 'vega-embed';
import {
  baseName,
  resolveExportTables,
  exportRowsAsCsv,
  exportRowsAsExcel,
  exportTablesAsExcel,
  exportChartImage,
} from '../utils/exportUtils';

export default function VegaChart({ vegaSpecs, responseText }) {
  const containerRef = useRef(null);
  const viewRef = useRef(null);
  const [selectedIdx, setSelectedIdx] = useState(0);
  const [tableIdx, setTableIdx] = useState(0);
  const [exportError, setExportError] = useState('');

  const current = vegaSpecs?.[selectedIdx];
  const spec = current?.spec;
  // Prefer the full markdown tables from the response; fall back to the chart's
  // inline data (which only contains the plotted fields).
  const tables = resolveExportTables({ responseText, spec });
  const activeTable = tables[Math.min(tableIdx, Math.max(0, tables.length - 1))];
  const rows = activeTable?.rows || [];
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

  const handleChartExport = async (format) => {
    setExportError('');
    try {
      await exportChartImage(viewRef.current, format, baseName(label));
    } catch (e) {
      console.error(`Chart ${format} export failed:`, e);
      setExportError(`Chart ${format.toUpperCase()} export failed: ${e.message}`);
    }
  };

  const handleTableExport = async (format) => {
    setExportError('');
    try {
      const name = baseName(activeTable?.title || label);
      if (format === 'csv') exportRowsAsCsv(rows, name);
      else await exportRowsAsExcel(rows, name);
    } catch (e) {
      console.error(`Table ${format} export failed:`, e);
      setExportError(`Data ${format.toUpperCase()} export failed: ${e.message}`);
    }
  };

  const handleAllTablesExcel = async () => {
    setExportError('');
    try {
      await exportTablesAsExcel(tables, baseName(label || 'tables'));
    } catch (e) {
      console.error('All-tables Excel export failed:', e);
      setExportError(`All-tables Excel export failed: ${e.message}`);
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
        {rows.length > 0 && (
          <span className="export-group">
            <span className="export-label">Data:</span>
            {tables.length > 1 && (
              <select
                className="chart-select export-table-select"
                value={Math.min(tableIdx, tables.length - 1)}
                onChange={e => setTableIdx(Number(e.target.value))}
                title="Choose which table to export"
              >
                {tables.map((t, i) => (
                  <option key={i} value={i}>{t.title || `Table ${i + 1}`}</option>
                ))}
              </select>
            )}
            <button className="export-btn" onClick={() => handleTableExport('csv')}>CSV</button>
            <button className="export-btn" onClick={() => handleTableExport('excel')}>Excel</button>
            {tables.length > 1 && (
              <button className="export-btn" onClick={handleAllTablesExcel}>All (Excel)</button>
            )}
          </span>
        )}
      </div>
      {exportError && <div className="export-error">{exportError}</div>}
    </div>
  );
}
