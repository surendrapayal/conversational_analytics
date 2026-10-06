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

/** Splits a markdown table row into trimmed cell strings. */
function splitMarkdownRow(line) {
  let s = line.trim();
  if (s.startsWith('|')) s = s.slice(1);
  if (s.endsWith('|')) s = s.slice(0, -1);
  // Split on unescaped pipes.
  return s.split('|').map(c => c.replace(/\\\|/g, '|').trim());
}

/** True if a line is a markdown table separator row (e.g. | :--- | ---: |). */
function isSeparatorRow(line) {
  const cells = splitMarkdownRow(line);
  return cells.length > 0 && cells.every(c => /^:?-{1,}:?$/.test(c.replace(/\s/g, '')));
}

/** Converts a cell string to a number when it looks numeric, else keeps the string. */
function coerceCell(s) {
  if (s === '' || s === '-') return s;
  // Strip common currency/grouping before numeric test, but keep original if not numeric.
  const cleaned = s.replace(/[$,%]/g, '').replace(/,/g, '');
  if (/^-?\d+(\.\d+)?$/.test(cleaned)) {
    const n = Number(cleaned);
    if (Number.isFinite(n)) return n;
  }
  return s;
}

/** Finds a human-friendly title for a table from the nearest preceding
 * non-empty, non-table text line (e.g. a markdown heading). Returns '' if none. */
function titleBefore(lines, headerIdx) {
  for (let k = headerIdx - 1; k >= 0 && k >= headerIdx - 4; k--) {
    const t = lines[k].trim();
    if (t === '') continue;
    if (t.includes('|')) break; // ran into another table, stop
    // Strip markdown heading hashes and trailing colons.
    return t.replace(/^#+\s*/, '').replace(/[:：]\s*$/, '').trim();
  }
  return '';
}

/**
 * Extracts ALL GitHub-flavoured markdown tables from response text.
 * Returns an array of { title, rows } where rows is an array of row objects
 * keyed by that table's own column headers. Empty array if no tables.
 */
export function tablesFromMarkdown(text) {
  if (!text || typeof text !== 'string') return [];
  const lines = text.split(/\r?\n/);
  const tables = [];

  let i = 0;
  while (i < lines.length - 1) {
    const headerLine = lines[i];
    const sepLine = lines[i + 1];
    if (!headerLine.includes('|') || !isSeparatorRow(sepLine)) {
      i++;
      continue;
    }

    const headers = splitMarkdownRow(headerLine);
    if (headers.length < 1) { i++; continue; }

    const rows = [];
    let j = i + 2;
    for (; j < lines.length; j++) {
      const line = lines[j];
      if (!line.includes('|') || line.trim() === '') break; // table ended
      const cells = splitMarkdownRow(line);
      const row = {};
      headers.forEach((h, idx) => {
        row[h] = coerceCell(cells[idx] ?? '');
      });
      rows.push(row);
    }

    if (rows.length > 0) {
      tables.push({ title: titleBefore(lines, i), rows });
    }
    i = j; // continue scanning after this table
  }
  return tables;
}

/**
 * Backwards-compatible helper: rows of the FIRST markdown table (or []).
 */
export function rowsFromMarkdown(text) {
  const tables = tablesFromMarkdown(text);
  return tables.length > 0 ? tables[0].rows : [];
}

/**
 * Resolves all exportable tables for a response, as [{ title, rows }].
 * Order of preference:
 *   1. every markdown table in the response text (full columns)
 *   2. otherwise the chart's inline data.values as a single table
 * Returns [] when neither is available.
 */
export function resolveExportTables({ responseText, spec } = {}) {
  const mdTables = tablesFromMarkdown(responseText);
  if (mdTables.length > 0) return mdTables;
  const specRows = rowsFromSpec(spec);
  return specRows.length > 0 ? [{ title: '', rows: specRows }] : [];
}

/**
 * Resolves the best single table's rows for export (first table).
 * Kept for callers that only need one table.
 */
export function resolveExportRows({ responseText, spec } = {}) {
  const tables = resolveExportTables({ responseText, spec });
  return tables.length > 0 ? tables[0].rows : [];
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

/** Converts rows into write-excel-file sheet data (header + typed cells). */
function toSheetData(rows) {
  const cols = columnsOf(rows);
  const headerRow = cols.map(c => ({ value: String(c), fontWeight: 'bold', type: String }));
  const dataRows = rows.map(r =>
    cols.map(c => {
      const v = r[c];
      if (v === null || v === undefined || v === '') return { type: String, value: '' };
      if (typeof v === 'number' && Number.isFinite(v)) return { type: Number, value: v };
      if (typeof v === 'boolean') return { type: Boolean, value: v };
      if (typeof v === 'object') return { type: String, value: JSON.stringify(v) };
      return { type: String, value: String(v) };
    })
  );
  return [headerRow, ...dataRows];
}

/** Builds a valid, unique Excel sheet name (<=31 chars, no :\/?*[] chars). */
function sheetName(title, index, used) {
  let base = (title || `Table ${index + 1}`)
    .replace(/[\\/?*[\]:]/g, ' ')
    .trim()
    .slice(0, 28) || `Table ${index + 1}`;
  let name = base;
  let n = 2;
  while (used.has(name.toLowerCase())) {
    name = `${base.slice(0, 25)} ${n++}`;
  }
  used.add(name.toLowerCase());
  return name;
}

/**
 * Exports an array of row objects as a real .xlsx file (single sheet).
 */
export async function exportRowsAsExcel(rows, filename) {
  if (!rows?.length) return;
  // The browser build is synchronous and returns { toBlob, toFile }; it does
  // NOT auto-download from a `fileName` option. Call .toFile() to download.
  await writeXlsxFile(toSheetData(rows), { sheet: 'Data' }).toFile(`${filename}.xlsx`);
}

/**
 * Exports multiple tables as a single .xlsx file, one sheet per table.
 * `tables` is an array of { title, rows }.
 */
export async function exportTablesAsExcel(tables, filename) {
  const nonEmpty = (tables || []).filter(t => t.rows?.length);
  if (nonEmpty.length === 0) return;
  if (nonEmpty.length === 1) {
    return exportRowsAsExcel(nonEmpty[0].rows, filename);
  }
  // Multi-sheet form: an array of Sheet objects, each { data, sheet }.
  const used = new Set();
  const sheets = nonEmpty.map((t, idx) => ({
    data: toSheetData(t.rows),
    sheet: sheetName(t.title, idx, used),
  }));
  await writeXlsxFile(sheets).toFile(`${filename}.xlsx`);
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
