# Stage Reports

Format per spec §14: files created/modified, important decisions, commands run + actual results, unresolved research questions, exact commands for next stage.

---

## Stage 1 — Specification and architecture

**Date:** 2026-10-14

### Files created or modified
- `docs/REQUIREMENTS.md` — full acceptance checklist (gates G1-G13, checks C1-C14, functional F/T/E/R/P/S/M/X items, research questions).
- `docs/ARCHITECTURE.md` — layered design, file structure, dataclasses, calculation flow, validation/error strategy, testing strategy.
- `docs/STAGE_REPORTS.md` — this file.
- `.gitignore` — venv, sqlite db, caches, env files.
- `git init` + initial commit.

### Important decisions
1. **Engine is pure Python, no Django imports** (`calculator/` package) — enables direct unit testing, CSV export and scenario comparison to reuse one code path (spec §5, §8, tests P11/P12).
2. **Dataclass-based I/O** (`AssignmentInputs` -> `AssignmentResult`) instead of dicts — keeps precision (Decimal), makes totals reconciliation testable.
3. **Traceability as data**: every rendered money row carries `derivation` + `source_ids`, so the audit trail and source citations come from the same structure (spec §5, §6).
4. **Reference data as a Django app** (`reference`) holding official-source records and immigration content, rendered with a shared citation macro — ensures every displayed rule has a link (gate G3).
5. **Decimal everywhere** in the engine; explicit rounding only at display boundaries (spec §5).
6. **Fail-safe gross-up**: typed `NonConvergenceError`, tolerance + max iterations, iteration history exposed (spec §5).
7. Research-first rule: no rate/fee enters code without an official URL recorded in `docs/RESEARCH.md` and `reference/sources.py`.

### Commands run and actual results
- `Get-ChildItem -Force` -> empty directory, no git repo. Confirmed clean start.
- `python --version` -> `Python 3.14.6`; `python -c "import django; print(django.get_version())"` -> `5.1.3` (Django already available in the environment; will still pin it in `requirements.txt`).
- No application code executed this stage (specification only, per instruction "Start with Stage 1 only").

### Unresolved research questions
Ten open questions logged in `docs/REQUIREMENTS.md` §4 (UK 2026/27 rates, employer NIC 2026/27, HS212/PAYE72028 mechanics, UK-Switzerland social security convention, Swiss hypothetical tax figures, AHV/ALV rates, UK immigration route for Swiss nationals, ETA for business visits, passport rules, fees/processing times). All to be resolved with official sources in Stage 3 and Stage 5.

### Exact commands for next stage (Stage 2)
```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
django-admin startproject config .
python manage.py startapp costtool
python manage.py startapp reference
python manage.py migrate
python manage.py runserver
```
Then verify the base template with both tabs loads, add a smoke test, and commit.

---

## Stage 2 - Project setup

**Date:** 2026-10-14

### Files created or modified
- `requirements.txt` - pinned `Django==6.1.2`.
- `config/settings.py` - env-driven `DJANGO_SECRET_KEY` / `DJANGO_DEBUG` / `DJANGO_ALLOWED_HOSTS`, apps registered (`costtool`, `reference`), project-level `templates/` and `static/` dirs, `en-gb` locale, explicit security settings (XFrameOptions DENY, nosniff, referrer policy, SameSite cookies; HSTS/SSL redirect when `DEBUG=0`).
- `config/urls.py` - `/` -> costtool, `/immigration/` -> reference, `/admin/`.
- `costtool/` - views.py, urls.py, templates/costtool/cost_estimate.html, tests.py (3 smoke tests).
- `reference/` - views.py, urls.py, templates/reference/immigration.html.
- `templates/base.html` - header, two primary tabs with `aria-current`, footer disclaimer, blocks.
- `static/css/app.css` - restrained palette (navy/ink/teal accent), panels, responsive tabs, focus-visible styles, visually-hidden helper.
- `static/js/app.js` - progressive enhancement (tab highlight fallback).

### Important decisions
1. **Django version changed 5.1.3 -> 6.1.2**: Python 3.14 is the only interpreter available; Django 5.1 test client crashed on 3.14 (`AttributeError: 'super' object has no attribute 'dicts'` inside template `Context.__copy__`). Django 6.1.2 is the current stable release with Python 3.14 support; pinned it in `requirements.txt`. All later stages target 6.1.2.
2. Settings read secrets/config from environment with a clearly-labelled dev-only fallback key (no real secret in the repo); production hardening activates automatically when `DEBUG=0`.
3. Tab structure implemented as two URL namespaces (`costtool:`, `reference:`) so each tab is an independent app - matches architecture and keeps navigation stable as features are added.
4. Smoke tests use `SimpleTestCase` (no DB) for speed; full `TestCase` tests arrive with the engine.

### Commands run and actual results
- `python -m venv .venv` + `pip install -r requirements.txt` -> `venv django 5.1.3` initially, upgraded to `6.1.2`.
- `django-admin startproject config .` + `startapp costtool` + `startapp reference` -> OK.
- `manage.py migrate` -> all migrations applied (admin, auth, contenttypes, sessions), exit OK.
- `manage.py check` -> `System check identified no issues (0 silenced).`
- `manage.py test -v 2` (after Django upgrade) -> `Ran 3 tests ... OK`.
- Live server smoke: `runserver 127.0.0.1:8765` -> `GET /` = 200, `GET /immigration/` = 200, both tab labels present.

### Unresolved research questions
Unchanged from Stage 1 (docs/REQUIREMENTS.md section 4). No new questions raised this stage.

### Exact commands for next stage (Stage 3)
```
.\.venv\Scripts\Activate.ps1
python manage.py test            # confirm still green before starting
```
Then: research official sources (GOV.UK 2026/27 rates and thresholds, HS212, PAYE72028, UK-CH social security, Swiss FTA calculator, AHV/ALV rates), record them in `docs/RESEARCH.md` + `reference/sources.py`, implement `calculator/` modules (`models`, `uk_tax`, `grossup`, `swiss_tax`, `swiss_social`, `employer_charges`, `benefits`, `assignment`) and the unit tests in `tests/`.

---

## Stage 3 - Research and calculation engine

**Date:** 2026-10-14

### Files created or modified
- `calculator/` (new pure-Python package, no Django imports):
  `__init__.py`, `exceptions.py`, `rounding.py`, `models.py`, `uk_tax.py`,
  `employee_nic.py`, `grossup.py`, `swiss_social.py`, `swiss_tax.py`,
  `benefits.py`, `employer_charges.py`, `assignment.py`.
- `reference/sources.py` - `Source` dataclass + `SOURCES` registry (14 official
  sources) with `get_source()` / `all_sources()`.
- `docs/RESEARCH.md` - source log, derived UK and Swiss rules, modelling
  assumptions A1-A10, open items.
- `tests/` (new): `__init__.py`, `test_uk_tax.py`, `test_grossup.py`,
  `test_swiss.py`, `test_assignment.py`, `test_employer_charges.py`,
  `test_sources.py`.
- `docs/STAGE_REPORTS.md` - this report.

### Important decisions
1. **Federal DBG tariff implemented as cumulative anchors with linear
   interpolation** (exact at every published point, no PDF-extraction drift);
   uniform 11.5% of total taxable income above CHF 793,900 per Form 58c.
2. **Zurich Steuerfuss corrected to 95% canton + 119% city = 214%** (not the
   earlier working note of 217%). Confirmed from the ESTV "Steuersatz und
   Steuerfuss" January 2026 document, the canton ("95 Prozent" for 2026/2027)
   and the city. This supersedes the pre-Stage-3 note.
3. **AHV/IV/EO carries no ceiling** (5.3% on all salary); only ALV is capped at
   CHF 148,200 (1.1%). Corrects the Stage-1 research list.
4. **Cantonal tariff is Zurich StG section 35 (1) Grundtarif** (verified in the
   consolidated StG, in force 1.1.2026), with ZStB Nr. 34.1 cited for the
   index-adjusted deductions.
5. **Net cost model** adopted: total employer cost = net home pay + benefits
   paid for + employer-paid UK income tax (grossed up) + employer Class 1 NIC +
   Class 1A NIC. Documented in `docs/RESEARCH.md` A2/A3.
6. **Gross-up converges in ~20 iterations** at tolerance GBP 0.01; the full
   iteration history is retained and exposed (`GrossUpResult.history`).
7. **Typed exceptions** (`CalculatorValidationError`, `NonConvergenceError`) with
   no partial results on failure; `NonConvergenceError` carries the history.
8. **Source traceability as data**: every `MoneyLine` carries `source_ids`, and
   `tests/test_sources.py` asserts each referenced id exists and is well formed
   (supports gate G3/C3).
9. Hypothetical Swiss deductions are explicitly labelled estimates (A5),
   flagged per spec E13.

### Commands run and actual results
- Downloaded official tariffs (PowerShell `Invoke-WebRequest`, TLS1.2) and
  extracted Text with `pypdf`:
  - `ur_bundestarif_2026.pdf` (ESTV Form 58c 2026) -> federal anchors verified.
  - `estv_steuerfuss_2026.pdf` -> Zurich 95% canton + 119% city confirmed.
  - `zh_stg.pdf` -> section 35 Grundtarif brackets verified.
- `python manage.py test -v 2` -> `Found 51 test(s) ... Ran 51 tests ... OK`.
- Engine smoke run on the supplied case (`AssignmentInputs()`):
  - Year 1 (2026/27): I GBP 160,570.12; T GBP 106,290.09; employer NIC GBP
    33,279.03; Class 1A GBP 6,000.00; cost GBP 312,139.25.
  - Year 2 (2027/28): I GBP 152,024.67; T GBP 99,298.36; employer NIC GBP
    31,548.45; Class 1A GBP 5,400.00; cost GBP 288,271.48.
  - Total employer cost GBP 600,410.73; multiple of home pay 1.94.
  - Hypothetical Swiss tax on CHF 170,000: taxable CHF 152,459.80; federal
    CHF 7,346.13; cantonal/communal CHF 24,386.54; total CHF 31,732.66.
- `python manage.py check` -> no issues.

### Unresolved research questions
- Hypothetical Swiss standard deductions (A5) remain estimates pending a manual
  run of the ESTV / Zurich calculators.
- Final federal/cantonal rounding rules (5-centime / CHF 100) not applied (A10).
- Social-security jurisdiction option (Swiss A1 / certificate of coverage for a
  <=24-month posting) is modelled as a flag but not yet surfaced in the UI.
- UK immigration research deferred to Stage 5.

### Exact commands for next stage (Stage 4)
```
.\.venv\Scripts\Activate.ps1
python manage.py test
python manage.py runserver
```
Then: build `costtool/forms.py` (AssignmentForm) and the views/templates that
render sections A-D from `run_assignment(...)`, add the input validation UI and
error states, wire source citations from `reference.sources`, and extend the test
suite with form/view tests (P10).

---

## Stage 4 - Cost Estimate form, view and results

**Date:** 2026-10-14

### Files created or modified
- `costtool/forms.py` (new) - `AssignmentForm` (Django `Form`) and
  `supplied_case_initial()`. Fields cover assignment locations/dates, employee
  details and residency flags, home pay (CHF), FX rate and the four assignment
  benefits. `clean()` checks the date order, `clean_fx_gbp_to_home()` enforces a
  positive rate, and `to_inputs()` maps validated data to `AssignmentInputs`.
  No financial logic lives here (spec E01).
- `costtool/views.py` (rewritten) - `cost_estimate(request)` handles GET (form
  pre-filled with the supplied case) and POST (validate -> `run_assignment`;
  `CalculatorError` rendered as a readable banner). Collects the referenced
  source ids in first-use order to build a citation-number map and the numbered
  source list.
- `reference/templatetags/__init__.py`, `reference/templatetags/reference_tags.py`
  (new) - `money`, `pounds`, `chf` filters (two-decimal, half-up, thousands
  separators); `cite_numbers` (source ids -> `[1, 3]`); `source` simple tag;
  `dict_get` (per-year lookup); `classification` (benefit label).
- `templates/includes/form_field.html` (new) - shared field macro with label,
  required marker, widget, help text and inline errors.
- `costtool/templates/costtool/_form.html`, `_results.html` (new) and
  `costtool/templates/costtool/cost_estimate.html` (rewritten) - sectioned form
  plus sections A-D, per-year totals, a whole-assignment summary, an expandable
  audit panel (hypothetical Swiss working + gross-up iteration history),
  assumptions and the numbered source list.
- `static/css/app.css` (extended) - styles for fieldsets/grid, alerts, data
  tables, benefit tags, summary grid, audit panel, assumptions and sources.
- `tests/test_forms_views.py` (new) - 11 tests: form mapping and validation
  (zero FX, negative pay, end-before-start, missing required), GET defaults,
  POST rendering of the supplied case (headline figures, both year labels,
  sections A/B, official source links) and an error-state check.
- `calculator/models.py`, `calculator/assignment.py` (modified) - `YearResult`
  gained a `benefits` list (`YearBenefit` records) so Section B can show native
  and GBP amounts, the UK treatment and the note.

### Important decisions
1. **View holds no finance logic** - it only validates, calls the engine and
   formats; everything numeric is engine output (spec E01).
2. **Traceability rendered from data** - citation numbers and the source list
   are derived from each row's `source_ids`, guaranteeing footnotes match the
   numbered list (gate G3).
3. **Residency flags surfaced, social-security choice not** - the two UK
   residency checkboxes are exposed; no social-security control was added
   because the engine would ignore it (would mislead), so the T13 rule is
   documented in the assumptions list instead.
4. **Audit by default, detail on demand** - the gross-up iteration history and
   the hypothetical Swiss tax working are inside a `<details>` panel so the
   headline figures stay readable while full traceability is one click away.
5. **Rendering-only templates** - `_form.html`/`_results.html` are partials
   included by `cost_estimate.html`, so a future scenario/CSV view can reuse
   the form and results blocks.

### Commands run and actual results
- `.\.venv\Scripts\python.exe manage.py test` -> `Ran 62 tests ... OK`
  (0.110s; 51 engine/source tests + 11 new form/view tests).
- `System check identified no issues (0 silenced).`
- POSTing the supplied case renders year 1 cost GBP 312,139.25 and the
  two-year total GBP 600,410.73, with `2026/27`, `2027/28`, `Section A`,
  `Section B` and `https://www.gov.uk/` source links present in the HTML.

### Unresolved research questions
- None new. The Swiss standard-deduction estimates (A5), final CHF rounding
  rules (A10) and the social-security-jurisdiction option (T13) remain as
  documented assumptions from earlier stages.

### Exact commands for next stage (Stage 5)
```
.\.venv\Scripts\Activate.ps1
python manage.py test
python manage.py runserver
```
Then: build the `reference` immigration tab (routes, ETA, costs, processing
times, official-source citations) with its own views/templates and tests, and
defer the CSV exporter (P12) / scenario comparison (M-items) to a later stage.

---

## Stage 5 - Immigration reference tab

**Date:** 2026-10-14

### Files created or modified
- `reference/sources.py` (extended) - 20 official immigration sources added
  (`category="immigration"`, `last_checked="2026-10-14"`), covering the Skilled
  Worker and GBM Senior/Specialist routes, the Skilled Occupations / Skilled
  Worker / Visitor / ETA Immigration-Rules appendices, sponsor-licence fees and
  the immigration skills charge, the immigration health surcharge, business
  visitor/ETA costs, passport rules, the right-to-work duty and the visa checker.
- `reference/immigration.py` (new) - data-only content module (no Django
  imports): obligation constants (`MANDATORY` / `RECOMMENDED` / `ESTIMATE`) with
  `CLASSIFICATION_LABELS`; dataclasses `Route`, `Requirement`, `CostItem`,
  `Step`, `ChecklistItem`; and the researched `ROUTES` (GBM Senior/Specialist
  marked primary, Skilled Worker, Standard Visitor), `REQUIREMENTS` (10),
  `COSTS` (8; employee-side 2-year subtotal GBP 2,889), `STEPS` (7),
  `CHECKLIST` (9), `PASSPORT_RULE`, `PASSPORT_SOURCE_IDS` and
  `all_source_ids()`.
- `reference/views.py` (rewritten) - the `immigration` view builds the
  citation-number map and numbered source records from `all_source_ids()` and
  passes the content groups to the template.
- `reference/templates/reference/immigration.html` (rewritten) - candidate-route
  cards (primary highlighted), requirements table (responsible party + status
  tag + citations), costs table, ordered application steps, the passport callout,
  the employer/employee readiness checklist and the numbered source list.
- `static/css/app.css` (extended) - route grids/cards, obligation tags
  (`mandatory` / `recommended` / `estimate`), steps, checklist and actor badges.
- `reference/test_immigration.py` (new) - 10 tests: every referenced source id
  resolves, is `category="immigration"`, `https://www.gov.uk/`, dated and has a
  relevance note; every route/requirement/cost/step/checklist item carries a
  source; exactly one primary route; known classifications; and view rendering
  (all sections, obligation types, official source links, the GBP 2,889 and
  GBP 1,035 cost figures, the passport rule and citation numbering in range).

### Important decisions
1. **Content as data, not markup** - routes, requirements, costs, steps and
   checklist items live in `reference/immigration.py` as dataclasses, so the
   template only formats and the same content could feed a CSV or PDF export
   later (spec F11 / M-items).
2. **Obligation types are first-class** - each requirement/cost carries a
   classification rendered as a tag, so mandatory legal requirements are visually
   distinct from recommendations and estimates (spec F12).
3. **Citations derived from `source_ids`** - as on the Cost Estimate tab, the
   footnote numbers and the numbered source list are generated from the content's
   `source_ids` via the existing `cite_numbers` filter, so footnotes and list
   cannot drift (gate G3 / C3).
4. **GBM Senior/Specialist is the flagged route** - for an existing employee on a
   temporary intra-group posting it is the route designed for the case, so it is
   marked "likely route"; the tool states it cannot decide the route alone and
   recommends adviser confirmation.
5. **No new template filters needed** - reused `reference_tags` (`dict_get` for
   the classification label, `cite_numbers` for citations), keeping one citation
   mechanism across both tabs.

### Commands run and actual results
- `.\.venv\Scripts\python.exe manage.py test` -> `Ran 72 tests ... OK`
  (0.106s; 62 prior tests + 10 new immigration tests).
- `System check identified no issues (0 silenced).`
- `GET /immigration/` returns 200 and renders "Candidate routes", the GBM and
  Skilled Worker routes, "Requirements", "Costs", "Application steps",
  "Readiness checklist", "Sources", the obligation labels, the GBP 2,889 and
  GBP 1,035 figures and the official `gov.uk` links.

### Unresolved research questions
- The mixed Skilled Worker threshold wording (GBP 41,700 "general" vs "going
  rate" per occupation code) is captured as a requirement, but the exact going
  rate cannot be applied without the specific SOC code, which this tool does not
  collect - noted as an estimate.
- Priority/expedited decision options (e.g. the GBP 750 sponsor-licence priority
  service) are described but not costed in the headline subtotal because their
  use is optional and case-specific.

### Exact commands for next stage (Stage 6)
```
.\.venv\Scripts\Activate.ps1
python manage.py test
python manage.py runserver
```
Then: add the CSV export (P12) and scenario comparison (M-items), or begin any
remaining spec items from `docs/REQUIREMENTS.md`.

---

## Stage 6 - README and acceptance status

**Date:** 2026-10-14

### Files created or modified
- `README.md` (new) - the submission README, covering: overview; features; tech
  stack (Python 3.14, Django 6.1.2); project structure; prerequisites; install and
  virtual-environment steps; migrate/run commands; how to obtain an estimate
  (including the supplied test case as the form default); test commands;
  methodology (tax equalisation, gross-up, UK rates, employer NIC, Swiss
  hypothetical tax, benefit classification); sources; known limitations; security
  notes; AI usage; and a placeholder for the demo video link.
- `docs/REQUIREMENTS.md` (updated) - statuses set for the gates (G1-G13), checks
  (C1-C14), functional requirements (F01-F13), test case (T01-T14), engine
  (E01-E13), research (R01-R10), tests (P01-P12), security (S01-S06) and
  README/demo (M01-M03) / enhancements (X01-X05) to reflect what is implemented.

### Important decisions
1. **Only real links in the README** - the demo-video section is an explicit
   placeholder ("to be added on submission") rather than a fabricated URL (spec
   M01: only real links).
2. **Honest status reporting** - items not implemented (scenario comparison X02,
   CSV export X04, P11/P12, demo video M03/G12, submission G11/C12) are left as
   TODO; the `>= 2 days` commit condition (G5/C6) is marked BLOCKED because all
   current commits fall on one calendar day and back-dating would be dishonest.
3. **Client validation clarified** - client-side validation is the native HTML5
   constraint set emitted by the Django widgets (`type=number`/`type=date`,
   `step`, `min`, `required`) plus the server `Form.clean_*` rules, so X03 is
   satisfied without bespoke JavaScript validation.

### Commands run and actual results
- `.\.venv\Scripts\python.exe manage.py test` -> `Ran 72 tests ... OK`
  (no code changed in this stage; suite re-run to confirm).
- Source registry confirmed: 34 sources (14 tax + 20 immigration).
- `git log --pretty=format:"%h %ad %s" --date=short` -> all commits dated
  2026-10-14 (G5/C6 blocker confirmed).

### Unresolved research questions
- None new.

### Exact commands for next stage (Stage 7)
```
.\.venv\Scripts\Activate.ps1
python manage.py test
python manage.py runserver
```
Then: implement the optional enhancements CSV export (X04/P12) and side-by-side
scenario comparison (X02/P11), add their tests, and commit on a later day to
satisfy the `>= 2 days` commit condition (G5/C6).

---

## Stage 7 - CSV export and scenario comparison

**Date:** 2026-10-14

### Files created or modified
- `costtool/exporters.py` (new) - `build_csv(result, source_numbers,
  source_records)` renders the estimate as a CSV document: a header, a per-year
  row per Section A/B/C/D line (year, section, item, currency, amount,
  classification and the bracketed citation numbers), a per-year total row, a
  whole-assignment summary block (home pay, total cost, cost multiple) and a
  numbered source block (id, title, publisher, URL, effective, checked). Amounts
  are fixed two-decimal strings so no exponential notation can appear.
- `costtool/views.py` (extended) - `csv_export(request)` (same form fields as the
  Cost Estimate tab; POST exports the submitted scenario, GET exports the
  supplied case; invalid input re-renders the estimate page with errors; returns
  a `text/csv` attachment) and `scenario_compare(request)` (two prefixed
  `AssignmentForm`s, both run through `run_assignment`, plus
  `_comparison_rows()` / `_changed_fields()` helpers). Added
  `_initial_as_post_data()` to bind the form from the supplied-case initial
  values.
- `costtool/forms.py` (extended) - `alternative_case_initial()` seeds the
  alternative column with a higher salary/housing variant so the comparison
  demonstrates a real difference.
- `costtool/urls.py` (extended) - `/compare/` and `/export/csv/` routes.
- `templates/base.html` (modified) - added a **Compare** primary tab.
- `costtool/templates/costtool/_form.html` (modified) - a **Download CSV**
  submit button that posts the same inputs to `costtool:csv_export` via
  `formaction`.
- `costtool/templates/costtool/scenario_compare.html` (new) - baseline and
  alternative forms side by side, then a metrics table (home pay, per-year
  employer cost, total, cost multiple) with base/alternative/difference columns
  and a note listing which fields differ.
- `static/css/app.css` (extended) - secondary button, two-column compare grid,
  up/down delta colours.
- `tests/test_csv_scenario.py` (new) - 7 tests: CSV content (annual rows, both
  years, both headline totals, sources/URLs), POST/GET attachment responses, an
  invalid-input HTML fallback, and scenario rendering, zero-difference for
  identical inputs, and reuse of the engine with a visible difference.
- `tests/test_forms_views.py` (extended) - `Html5JsCoverageTests` (4 tests)
  covering F13/X03 client-side behaviour: native HTML5 constraints
  (`type=number`, `step`, `min`, `type=date`, `required`), stylesheet/script and
  label markup, and readable error output (`class="error"`, `role="alert"`).
- `static/js/app.js` (fixed) - the tab-highlight fallback matched `href="/"`
  against every path (empty-string `indexOf`), which could mark the Cost tab
  active on all pages; it now matches `/` exactly and strips trailing slashes.

### Important decisions
1. **One code path** - the exporter consumes the same `AssignmentResult` as the
   on-screen tables and the comparison runs `run_assignment` once per scenario,
   so CSV and comparison figures are identical to the main tab (P11/P12).
2. **CSV via `formaction`** - the Download button reuses the existing Cost
   Estimate form's inputs, so no duplicate form or hidden fields are needed and
   the export always matches what the user just calculated.
3. **Invalid export shows errors, not a broken file** - a failed validation
   re-renders the estimate page rather than returning a partial or empty CSV.
4. **Difference colours** - the comparison marks higher alternative cost red and
   lower cost green for quick scanning, while the exact figures stay in GBP.

### Commands run and actual results
- `.\.venv\Scripts\python.exe manage.py test` -> `Ran 83 tests ... OK`
  (0.178s; 72 prior + 7 CSV/compare + 4 HTML5/JS).
- `System check identified no issues (0 silenced).`
- `GET /export/csv/` -> `200 text/csv`, 52 lines, containing the header row,
  Section A rows (e.g. `2026/27,A,Base salary,GBP,136363.64`) and
  `Summary,,Total employer cost (both years),GBP,600410.73`.
- `GET /compare/` and `POST /compare/` -> 200 with both columns and a
  comparison table showing baseline `600,410.73`.

### Unresolved research questions
- None new.

### Exact commands for next stage (Stage 8)
```
.\.venv\Scripts\Activate.ps1
python manage.py test
python manage.py runserver
```
Then: remaining work is the non-code submission tasks (G11/C12 repo+video,
G12/C13 Loom walkthrough, M03) plus the `>= 2 days` commit condition (G5/C6),
which requires committing on a later calendar day.

---

## Stage 8 - Download CSV user-experience fix

**Date:** 2026-10-14

### Problem
The **Download CSV** and **Calculate cost** buttons sat side by side in the same
action row. This was ambiguous: it was not clear that the download acts on the
calculated estimate, and pressing download before calculating used whatever was
in the form.

### Files modified
- `costtool/templates/costtool/_form.html` - the form now has a stable id
  (`estimate-form`) and the action row contains only the **Calculate cost**
  button.
- `costtool/templates/costtool/_results.html` - the **Download this estimate
  (CSV)** button now lives in the results summary panel and submits the estimate
  form via the HTML5 `form="estimate-form"` + `formaction` attributes, with a
  caption stating the CSV contains exactly the figures shown.
- `tests/test_csv_scenario.py` - added `test_download_button_lives_with_the_results`
  (form id present; no download button before calculating; button wired to the
  export URL after calculating).

### Outcome
The flow is now unambiguous: press **Calculate cost** to see the estimate, then
press **Download this estimate (CSV)** to download exactly those figures. Server
behaviour was already correct (verified by exporting a modified salary of
CHF 200,000 -> 181,818.18 and total 716,817.82).

### Commands run and actual results
- `.\.venv\Scripts\python.exe manage.py test` -> `Ran 84 tests ... OK`
  (0.212s).

---

## Stage 9 - Fix: "Calculate cost" must calculate, not download

**Date:** 2026-10-14

### Problem
The Stage 8 change placed the download button **outside** the form and linked it
with the HTML5 `form="estimate-form"` attribute. That cross-form submit-button
association is unreliable and let the download action interfere with the main
submit, so clicking **Calculate cost** could trigger a download instead of
calculation.

### Fix
- `costtool/templates/costtool/_form.html` - both buttons are back inside the
  single form, each with an **explicit** `formaction`:
  - **Calculate cost** -> `{% url 'costtool:cost_estimate' %}` (the form's own
    page, so it always calculates and renders the tables).
  - **Download CSV** -> `{% url 'costtool:csv_export' %}`.
  No `form="..."` cross-references are used any more.
- `costtool/templates/costtool/_results.html` - removed the external download
  button from the summary panel.
- `tests/test_csv_scenario.py` - replaced the old wiring test with
  `test_calculate_and_download_buttons_have_distinct_actions`, asserting both
  buttons live in the form and target the correct URLs.

### Outcome
Clicking **Calculate cost** always posts to the calculate view and shows the two
annual cost tables; clicking **Download CSV** downloads the CSV. No other
behaviour changed.

### Commands run and actual results
- `.\.venv\Scripts\python.exe manage.py test` -> `Ran 84 tests ... OK`
  (0.188s).
