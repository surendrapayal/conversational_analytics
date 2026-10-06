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

## 4. Recommendation

**Split ownership by source of truth:**

1. **Chart PNG/SVG → Frontend. Permanently.** The rendered chart only exists client-side; there is no reason to move it server-side.

2. **Table CSV/Excel → decide by requirement:**
   - **Convenience-grade, small data, no governance need →** Frontend is acceptable (Option A), provided the data-completeness gap is accepted or mitigated.
   - **Must be complete / large / governed (RBAC + audit + compliance) →** Backend (Option B).

**Guidance for a production analytics platform:** treat exported data as a **governed data egress**, not a UI convenience. That favours **Option B for table data** (backend) while keeping **chart image on the frontend**. The clinching reasons:

- **Completeness** — the frontend provably does not hold the full result set today.
- **Governance** — RBAC is already enforced on queries; exports should inherit it and be auditable.

---

## 5. Decision

> _To be completed by the architecture team._

- [ ] **Option A** — Frontend owns all export (accept derived-data limitation).
- [ ] **Option B** — Backend owns table data export; frontend owns chart image export. *(Recommended for production/governed data.)*
- [ ] Other: _______________________________________________

**Rationale / notes:**

_(record the decision reasoning here)_

---

## 6. Consequences

**If Option A:**
- Document that exports reflect "what is displayed," not the full query result.
- Keep hardening the markdown/spec extraction; add tests for multi-table and wide-table cases.

**If Option B:**
- Add `result_columns` / `result_rows` capture in the agent pipeline and persist per conversation (define retention + PII policy).
- Add the streaming export endpoint with RBAC checks and audit logging.
- Add rate limiting and a max-rows / max-size guardrail.
- Frontend calls the endpoint for data; continues to handle chart images locally.

---

## 7. One-line summary

> Chart image export is a frontend responsibility (the rendered chart only exists client-side). Table data export is a frontend responsibility **only** if exports are small, convenience-grade, and ungoverned; otherwise it is a **backend** responsibility, because the backend is the only tier with the complete, RBAC-filtered, auditable result set. The current implementation is fully frontend and reconstructs data from the chart/markdown, which is not authoritative.
