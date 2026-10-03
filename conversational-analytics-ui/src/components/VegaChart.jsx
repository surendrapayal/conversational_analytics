import { useEffect, useRef, useState } from 'react';
import embed from 'vega-embed';

export default function VegaChart({ vegaSpecs }) {
  const containerRef = useRef(null);
  const [selectedIdx, setSelectedIdx] = useState(0);

  useEffect(() => {
    if (!containerRef.current || !vegaSpecs?.length) return;
    const spec = vegaSpecs[selectedIdx]?.spec;
    if (!spec) return;
    embed(containerRef.current, spec, {
      actions: { export: true, source: false, compiled: false, editor: false },
      theme: 'dark',
    }).catch(console.error);
  }, [vegaSpecs, selectedIdx]);

  if (!vegaSpecs?.length) return null;

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
    </div>
  );
}
