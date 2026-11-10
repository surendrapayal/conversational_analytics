// Chart image export helpers (frontend-owned).
// Table data export (CSV/Excel/PDF) is handled by the backend — see
// `exportConversationData` in api/client.js and docs/ADR-export.md (Option B).

/** Triggers a browser download for an object URL. */
function triggerDownload(href, filename) {
  const a = document.createElement('a');
  a.href = href;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
}

/**
 * Builds a filename-safe slug from a label, with a timestamp.
 * e.g. baseName('Sales by location') -> 'sales-by-location_20260110-1532'
 */
export function baseName(label = 'export') {
  const slug = String(label)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 60) || 'export';
  const d = new Date();
  const pad = n => String(n).padStart(2, '0');
  const stamp = `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}-${pad(d.getHours())}${pad(d.getMinutes())}`;
  return `${slug}_${stamp}`;
}

/**
 * Exports a Vega view as a PNG or SVG image file.
 * `view` is the Vega View instance from the vega-embed result.
 * Chart image export stays on the frontend (the rendered chart only exists client-side).
 */
export async function exportChartImage(view, format, filename) {
  if (!view) return;
  // scaleFactor=2 gives a crisp PNG; ignored for SVG.
  const url = await view.toImageURL(format, format === 'png' ? 2 : 1);
  triggerDownload(url, `${filename}.${format}`);
}
