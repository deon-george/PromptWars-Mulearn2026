export default function ExplainPanel({ explanation }) {
  if (!explanation) return null;
  return (
    <div className="panel">
      <h3>Explainability</h3>
      <p className="lead">{explanation.plain_english}</p>
      <ul className="signals">
        {explanation.top_signals?.map((item) => (
          <li key={item.name}>
            <span className="signal-name">{item.name}</span>
            <span className="signal-bar">
              <span className="signal-fill" style={{ width: `${Math.min(100, item.score * 100).toFixed(1)}%` }} />
            </span>
            <span className="signal-value">{item.level || ''} {(item.score * 100).toFixed(1)}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
