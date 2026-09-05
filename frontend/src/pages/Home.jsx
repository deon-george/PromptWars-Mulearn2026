import { useState } from 'react';
import Uploader from '../components/Uploader.jsx';
import ScorePanel from '../components/ScorePanel.jsx';
import ExplainPanel from '../components/ExplainPanel.jsx';
import VerificationPanel from '../components/VerificationPanel.jsx';
import MediaPreview from '../components/MediaPreview.jsx';
import HeatmapPanel from '../components/HeatmapPanel.jsx';

export default function Home() {
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);

  const onAnalyzed = (data) => {
    setResult(data);
  };

  return (
    <div className="page">
      <header className="topbar">
        <div className="brand">
          <div className="logo" />
          <div>
            <div className="title">PromptWars Media Verification</div>
            <div className="muted">Deepfake · AI manipulation · Reverse context · Explanation</div>
          </div>
        </div>
      </header>

      <section className="layout">
        <aside>
          <Uploader onAnalyzed={onAnalyzed} busy={busy} setBusy={setBusy} />
          <ScorePanel score={result?.score} />
          <ExplainPanel explanation={result?.explanation} />
          <VerificationPanel verification={result} />
        </aside>
        <main>
          <MediaPreview result={result} />
          <HeatmapPanel media={result?.analysis} mediaType={result?.media_type} />
        </main>
      </section>

      <footer className="footer">
        Analysis is signal-based and may be wrong. Treat as supporting context, not legal evidence.
      </footer>
    </div>
  );
}
