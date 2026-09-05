export default function HeatmapPanel({ media, mediaType }) {
  if (!media || mediaType !== 'image') {
    return (
      <div className="panel empty">
        <h3>Manipulation zones</h3>
        <p>Image analysis produces a per-region heatmap.</p>
      </div>
    );
  }
  const { heatmap, width, height } = media;
  const rows = heatmap?.length || 0;
  const cols = heatmap?.[0]?.length || 0;
  return (
    <div className="panel">
      <h3>Manipulation zones</h3>
      <div className="heatmap">
        {Array.from({ length: rows }).map((_, r) => (
          <div className="heatmap-row" key={r}>
            {Array.from({ length: cols }).map((_, c) => {
              const value = Number(heatmap?.[r]?.[c] || 0);
              const opacity = 0.15 + value * 0.85;
              return (
                <div
                  key={c}
                  className="heatmap-cell"
                  title={`x=${c} y=${r} anomaly=${value.toFixed(2)}`}
                  style={{ background: `rgba(248,113,113,${opacity.toFixed(2)})` }}
                />
              );
            })}
          </div>
        ))}
      </div>
      <p className="muted">Resolution: {width}×{height}</p>
    </div>
  );
}
