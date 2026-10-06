import { useEffect, useRef, useState } from 'react';
import embed from 'vega-embed';
import {
  baseName,
  rowsFromSpec,
  exportRowsAsCsv,
  exportRowsAsExcel,
  exportChartImage,
} from '../utils/exportUtils';

export default function VegaChart({ vegaSpecs }) {
  const containerRef = useRef(null);
  const viewRef = useRef(null);
  const [selectedIdx, setSelectedIdx] = useState(0);

  const current = vegaSpecs?.[selectedIdx];
  const spec = current?.spec;
  const rows = spec ? rowsFromSpec(spec) : [];
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
    try {
      await exportChartImage(viewRef.current, format, baseName(label));
    } catch (e) {
      console.error(`Chart ${format} export failed:`, e);
    }
  };

  const handleTableExport = async (format) => {
    try {
      const name = baseName(label);
      if (format === 'csv') exportRowsAsCsv(rows, name);
      else await exportRowsAsExcel(rows, name);
    } catch (e) {
      console.error(`Table ${format} export failed:`, e);
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
            <button className="export-btn" onClick={() => handleTableExport('csv')}>CSV</button>
            <button className="export-btn" onClick={() => handleTableExport('excel')}>Excel</button>
          </span>
        )}
      </div>
    </div>
  );
}
