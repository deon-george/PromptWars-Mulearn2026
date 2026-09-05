export default function CredibilityPanel({ credibility }) {
  if (!credibility) return null;
  const score = Number(credibility.score ?? 0);
  const color = score > 70 ? 'var(--ok)' : score > 35 ? 'var(--warn)' : 'var(--danger)';
  return (
    <div className="panel">
      <h3>Source credibility</h3>
      <div className="score-ring" style={{ color }}>
        <span>{score.toFixed(1)}</span>
      </div>
      <ul className="signals">
        {(credibility.reasons || []).map((r, i) => (
          <li key={i} className="signal-name">{r}</li>
        ))}
      </ul>
      <p className="muted">Domain: {credibility.domain || 'unknown'}</p>
    </div>
  );
}
