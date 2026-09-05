const API_BASE = '/api';

export async function analyzeMedia(file) {
  const form = new FormData();
  form.append('file', file);
  const res = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    body: form,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function reverseSearch(file) {
  const form = new FormData();
  form.append('file', file);
  const res = await fetch(`${API_BASE}/reverse-search`, {
    method: 'POST',
    body: form,
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function getProvenance(file) {
  const form = new FormData();
  form.append('file', file);
  const res = await fetch(`${API_BASE}/provenance`, {
    method: 'POST',
    body: form,
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}
