const STEP_ICONS = {
  'Identifying available data sources': '🗂️',
  'Analysing data structure': '🔍',
  'Validating query': '✅',
  'Retrieving data': '⚡',
};

export default function StepIndicator({ steps }) {
  if (!steps?.length) return null;
  return (
    <div className="step-indicator">
      {steps.map((step, i) => (
        <div key={i} className="step-item">
          <span className="step-icon">{STEP_ICONS[step] || '⚙️'}</span>
          <span className="step-text">{step}</span>
        </div>
      ))}
      <div className="step-item step-thinking">
        <span className="step-spinner" />
        <span className="step-text">Thinking...</span>
      </div>
    </div>
  );
}
