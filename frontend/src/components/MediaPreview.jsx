export default function MediaPreview({ result }) {
  if (!result) {
    return (
      <div className="panel empty">
        <h3>Preview</h3>
        <p>Upload media to see analysis results.</p>
      </div>
    );
  }
  const src = result.file_path;
  if (result.media_type === 'image' && src) {
    return (
      <div className="panel">
        <h3>Image preview</h3>
        <img src={src} alt="uploaded" />
      </div>
    );
  }
  if (result.media_type === 'video' && src) {
    return (
      <div className="panel">
        <h3>Video preview</h3>
        <video controls src={src} />
      </div>
    );
  }
  if (result.media_type === 'audio' && src) {
    return (
      <div className="panel">
        <h3>Audio preview</h3>
        <audio controls src={src} />
      </div>
    );
  }
  return (
    <div className="panel">
      <h3>Preview</h3>
      <p>Preview unavailable.</p>
    </div>
  );
}
