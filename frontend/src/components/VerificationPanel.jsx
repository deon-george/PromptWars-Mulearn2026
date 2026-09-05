export default function VerificationPanel({ verification }) {
  if (!verification) {
    return (
      <div className="panel empty">
        <h3>Verification</h3>
        <p className="muted">Submit media to see reverse-search, provenance, credibility, OCR, and fact-check context.</p>
      </div>
    );
  }

  const {
    analysis,
    explanation,
    provenance,
    metadata,
    reverse_search,
    credibility,
    ocr,
    factcheck,
    score,
  } = verification;

  const disabled = { enabled: false, note: 'Not available' };
  const sections = [
    { title: 'Reverse search', data: reverse_search || disabled },
    { title: 'Provenance', data: provenance || disabled },
    { title: 'Source credibility', data: credibility || disabled },
    { title: 'OCR text', data: ocr || disabled },
    { title: 'Fact-check context', data: factcheck || disabled },
    { title: 'Explanation', data: explanation || disabled },
    { title: 'Detection signals', data: analysis || disabled },
  ];

  return (
    <div className="panel">
      <h3>Verification</h3>
      <div className="verification-sections">
        {sections.map((section) => (
          <VerificationSection key={section.title} {...section} />
        ))}
      </div>
    </div>
  );
}

function VerificationSection({ title, data }) {
  if (!data || typeof data !== 'object') {
    return (
      <div className="verification-section">
        <strong>{title}</strong>
        <p className="muted">No data</p>
      </div>
    );
  }

  const isDisabled = data.enabled === false;
  const hasError = !!data.error;
  const matches = data.matches || data.results || data.snippets;
  const text = data.text;
  const exif = data.exif;
  const contexts = data.contexts;

  return (
    <div className="verification-section">
      <strong>{title}</strong>
      {isDisabled && (
        <p className="muted">{data.note || 'Not available'}</p>
      )}
      {hasError && !isDisabled && (
        <p className="muted" style={{ color: 'var(--danger)' }}>
          Error: {data.error}
        </p>
      )}
      {matches && (
        <ul className="reverse-list">
          {(matches || []).slice(0, 8).map((item, idx) => (
            <li key={idx}>{typeof item === 'string' ? item : JSON.stringify(item)}</li>
          ))}
        </ul>
      )}
      {text && (
        <div>
          {typeof text === 'string' ? (
            <p>{text}</p>
          ) : (
            <ul>
              {(text || []).map((line, idx) => (
                <li key={idx}>{line}</li>
              ))}
            </ul>
          )}
        </div>
      )}
      {exif && (
        <div>
          <p className="muted">Metadata</p>
          <ul>
            {Object.entries(exif).map(([key, value]) => (
              <li key={key}>
                <strong>{key}</strong>: {value}
              </li>
            ))}
          </ul>
        </div>
      )}
      {contexts && (
        <ul className="signals">
          {(contexts || []).map((context, idx) => (
            <li key={idx}>{context}</li>
          ))}
        </ul>
      )}
      {!matches && !text && !exif && !contexts && !isDisabled && !hasError && (
        <pre className="manifest">{JSON.stringify(data, null, 2)}</pre>
      )}
    </div>
  );
}
