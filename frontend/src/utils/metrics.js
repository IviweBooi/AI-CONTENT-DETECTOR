// Simple client-side metrics store using localStorage.
// this is gonna be backed by a database in the final version.

const KEY = 'aicd_metrics_v1';

function read() {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return { totalScans: 0, feedbackCount: 0, accuracy: 85 };
    const parsed = JSON.parse(raw) || {};
    return {
      totalScans: Number(parsed.totalScans) || 0,
      feedbackCount: Number(parsed.feedbackCount) || 0,
      // Defaults to 85% until replaced by backend evaluation
      accuracy: Number(parsed.accuracy) || 85,
    };
  } catch {
    return { totalScans: 0, feedbackCount: 0, accuracy: 85 };
  }
}

function write(next) {
  try { localStorage.setItem(KEY, JSON.stringify(next)); } catch {}
}

export function getMetrics() { return read(); }

export function incrementScan() {
  const m = read();
  const next = { ...m, totalScans: m.totalScans + 1 };
  write(next);
  return next;
}

export function addFeedback() {
  const m = read();
  const next = { ...m, feedbackCount: m.feedbackCount + 1 };
  write(next);
  return next;
}

export function setAccuracy(accuracyPercent) {
  const m = read();
  const a = Math.max(0, Math.min(100, Number(accuracyPercent) || m.accuracy));
  const next = { ...m, accuracy: a };
  write(next);
  return next;
}
