export default function VerificationPanel({ verification }) {
  if (!verification) {
    return (
      <div className="panel empty">
        <h3>Verification</h3>
        <p>Run analysis to view verification details.</p>
      </div>
    );
  }
  const sections = [
    { label: 'Provenance', data: verification.provenance },
    { label: 'Reverse search', data: verification.reverse_search },
    { label: 'Credibility', data: verification.credibility },
    { label: 'Metadata', data: verification.metadata },
    { label: 'OCR', data: verification.ocr },
    { label: 'Fact-check', data: verification.factcheck },
  ];
  return (
    <div className="panel">
      <h3>Verification</h3>
      {sections.map((section) => (
        <div key={section.label} className="verification-section">
          <strong>{section.label}</strong>
          <pre className="manifest">{JSON.stringify(section.data, null, 2)}</pre>
        </div>
      ))}
    </div>
  );
}
