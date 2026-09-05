export default function FactcheckPanel({ factcheck }) {
  if (!factcheck) return null;
  if (!factcheck.enabled) {
    return (
      <div className="panel">
        <h3>Fact-check context</h3>
        <p className="muted">{factcheck.note || 'Not available'}</p>
      </div>
    );
  }
  const contexts = factcheck.contexts || [];
  return (
    <div className="panel">
      <h3>Fact-check context</h3>
      <ul className="signals">
        {contexts.map((item, i) => (
          <li key={i}>
            <span className="signal-name">Query: {item.query}</span>
            {item.context?.enabled ? (
              <ul className="reverse-list">
                {(item.context.results || []).slice(0, 3).map((r, idx) => (
                  <li key={idx} className="reverse-item">
                    <a href={r.link} target="_blank" rel="noreferrer">{r.title || r.link}</a>
                    <span className="muted">{r.snippet}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="muted">{item.context?.note || item.context?.error || 'No results'}</p>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
