import writeXlsxFile from 'write-excel-file/browser';

/**
 * Triggers a browser download for a Blob or object URL.
 */
function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  triggerDownload(url, filename);
  // Revoke after the click has had a chance to start the download.
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

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
 * Extracts tabular rows (array of objects) from a Vega-Lite spec's inline data.
 * Vega-Lite embeds row data under spec.data.values. Returns [] if none found.
 */
export function rowsFromSpec(spec) {
  const values = spec?.data?.values;
  if (Array.isArray(values) && values.length > 0 && typeof values[0] === 'object') {
    return values;
  }
  return [];
}

/**
 * Returns the ordered column keys across all rows (union, first-seen order).
 */
function columnsOf(rows) {
  const cols = [];
  const seen = new Set();
  for (const row of rows) {
    for (const k of Object.keys(row)) {
      if (!seen.has(k)) { seen.add(k); cols.push(k); }
    }
  }
  return cols;
}

function csvCell(value) {
  if (value === null || value === undefined) return '';
  const s = typeof value === 'object' ? JSON.stringify(value) : String(value);
  // Quote if the value contains comma, quote, or newline; escape embedded quotes.
  if (/[",\n\r]/.test(s)) {
    return `"${s.replace(/"/g, '""')}"`;
  }
  return s;
}

/**
 * Exports an array of row objects as a CSV file.
 */
export function exportRowsAsCsv(rows, filename) {
  if (!rows?.length) return;
  const cols = columnsOf(rows);
  const header = cols.map(csvCell).join(',');
  const body = rows.map(r => cols.map(c => csvCell(r[c])).join(',')).join('\n');
  // Prepend BOM so Excel opens UTF-8 correctly.
  const blob = new Blob(['\uFEFF' + header + '\n' + body], { type: 'text/csv;charset=utf-8;' });
  downloadBlob(blob, `${filename}.csv`);
}

/**
 * Exports an array of row objects as a real .xlsx file.
 */
export async function exportRowsAsExcel(rows, filename) {
  if (!rows?.length) return;
  const cols = columnsOf(rows);

  const headerRow = cols.map(c => ({ value: c, fontWeight: 'bold' }));
  const dataRows = rows.map(r =>
    cols.map(c => {
      const v = r[c];
      if (v === null || v === undefined) return { value: '' };
      if (typeof v === 'number') return { type: Number, value: v };
      if (typeof v === 'boolean') return { type: Boolean, value: v };
      if (typeof v === 'object') return { value: JSON.stringify(v) };
      return { value: String(v) };
    })
  );

  await writeXlsxFile([headerRow, ...dataRows], {
    fileName: `${filename}.xlsx`,
    sheet: 'Data',
  });
}

/**
 * Exports a Vega view as a PNG or SVG image file.
 * `view` is the Vega View instance from the vega-embed result.
 */
export async function exportChartImage(view, format, filename) {
  if (!view) return;
  // scaleFactor=2 gives a crisp PNG; ignored for SVG.
  const url = await view.toImageURL(format, format === 'png' ? 2 : 1);
  triggerDownload(url, `${filename}.${format}`);
}
