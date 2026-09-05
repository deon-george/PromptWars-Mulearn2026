import { useState, useRef } from 'react';
import { analyzeMedia } from '../utils/api.js';

export default function Uploader({ onAnalyzed, busy, setBusy }) {
  const fileRef = useRef();
  const [fileName, setFileName] = useState('');

  const onSubmit = async (e) => {
    e.preventDefault();
    const file = fileRef.current?.files?.[0];
    if (!file) return;
    setFileName(file.name);
    setBusy(true);
    try {
      const data = await analyzeMedia(file);
      onAnalyzed(data);
    } catch (err) {
      alert(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <form onSubmit={onSubmit} className="panel">
      <h3>Upload media</h3>
      <p className="muted">Supported: image, audio, video</p>
      <input ref={fileRef} type="file" accept="image/*,audio/*,video/*" onChange={(e) => setFileName(e.target.files?.[0]?.name || '')} />
      <button disabled={busy} type="submit">{busy ? 'Analyzing…' : 'Analyze'}</button>
      {fileName ? <div className="filepill">{fileName}</div> : null}
    </form>
  );
}
