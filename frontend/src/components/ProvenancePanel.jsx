export default function ProvenancePanel({ provenance }) {
  if (!provenance) return null;
  return (
    <div className="panel">
      <h3>Provenance</h3>
      <p className="muted">{provenance.error || 'No provenance data available.'}</p>
    </div>
  );
}
