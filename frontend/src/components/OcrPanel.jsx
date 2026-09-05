export default function OcrPanel({ ocr }) {
  if (!ocr) return null;
  return (
    <div className="panel">
      <h3>OCR / Text extraction</h3>
      {ocr.enabled ? (
        <>
          <p className="muted">Engine: {ocr.engine} · Lines: {ocr.line_count ?? 0}</p>
          <pre className="manifest">{ocr.text || ''}</pre>
        </>
      ) : (
        <p className="muted">{ocr.error || ocr.note || 'OCR unavailable'}</p>
      )}
    </div>
  );
}
