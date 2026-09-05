export default function ReversePanel({ reverse }) {
  if (!reverse) return null;
  if (!reverse.enabled) {
    return (
      <div className="panel">
        <h3>Reverse search</h3>
        <p className="muted">{reverse.note || reverse.error || 'Not available'}</p>
      </div>
    );
  }
  const matches = reverse.matches || [];
  return (
    <div className="panel">
      <h3>Reverse search</h3>
      {matches.length === 0 ? (
        <p className="muted">No matches found.</p>
      ) : (
        <ul className="reverse-list">
          {matches.map((m, i) => (
            <li key={i} className="reverse-item">
              <a href={m.link} target="_blank" rel="noreferrer">{m.title || m.link}</a>
              <span className="muted">{m.source}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
