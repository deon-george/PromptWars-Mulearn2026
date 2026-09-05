export default function ScorePanel({ score }) {
  const s = score || {};
  const overall = Number(s.overall ?? 0);
  const color = overall > 70 ? 'var(--danger)' : overall > 35 ? 'var(--warn)' : 'var(--ok)';
  return (
    <div className="panel">
      <h3>Synthetic score</h3>
      <div className="score">
        <div className="score-ring" style={{ color }}>
          <span>{overall.toFixed(1)}%</span>
        </div>
        <div className="score-labels">
          <div><span style={{ background: 'var(--ok)' }} /> Low</div>
          <div><span style={{ background: 'var(--warn)' }} /> Mixed</div>
          <div><span style={{ background: 'var(--danger)' }} /> High</div>
        </div>
      </div>
      <div className="score-breakdown">
        <div>Detection <strong>{Number(s.detection ?? 0).toFixed(1)}</strong></div>
        <div>Source <strong>{Number(s.source ?? 0).toFixed(1)}</strong></div>
        <div>Explanation confidence <strong>{Number(s.explanation_confidence ?? 0).toFixed(1)}</strong></div>
      </div>
    </div>
  );
}
