# Assignment Cost Tool

A Django web application that estimates the **true employer cost** of sending a
Swiss employee from Zurich to London for a two-year assignment, and documents the
**UK immigration requirements** that go with it. It was built to the supplied
assignment brief ("Assignment Cost Tool — Full-Stack Django Application") and the
exact test case in that brief must be accepted without any source-code changes.

The tool has two tabs:

- **Cost Estimate** — enter the assignment inputs and get per-tax-year cost tables
  (sections A–D), totals, the cost as a multiple of home pay, the full calculation
  working and numbered official source citations.
- **Immigration** — the candidate visa route, requirements, costs, application
  steps, passport rules and a readiness checklist, each marked as a **mandatory**,
  **recommended** or **estimated** item and linked to an official source.

---

## Overview

An international assignment is not just the employee's salary. This tool models the
economics the way a truly "tax-equalised" assignment works:

- The employee's **net home pay** is preserved (after *hypothetical* Swiss income
  tax and social security), so the employee is no worse off for moving.
- The employer **grosses up** UK pay so that, after UK income tax is paid on it, the
  employee still receives that net amount. This requires solving
  `T = UKTax(I + T)` iteratively (tax on tax on tax …).
- The employer also pays **UK employer National Insurance** (Class 1 on earnings,
  Class 1A on benefits in kind) and the **cost of the assignment benefits**
  (housing, relocation, moving, temporary accommodation).
- Assignment benefits are classified as **taxable cash**, **benefit in kind** or
  **not taxable** and treated accordingly.

The result is the total employer cost and the "cost as a multiple of home pay".

## Features

- **Per-tax-year cost tables** for 2026/27 and 2027/28 (the two UK tax years in the
  supplied case), each split into:
  - **Section A — Home Pay**: gross salary/bonus, FX conversion, hypothetical Swiss
    income tax and social security, net home pay.
  - **Section B — Assignment Benefits**: each benefit with amount, currency, year and
    UK tax classification.
  - **Section C — Host Tax & Employer Charges**: employer-paid UK income tax,
    the tax-on-tax gross-up and employer National Insurance.
  - **Section D — Deductions**: the hypothetical Swiss deductions restated so the
    sections reconcile to the headline total.
- **Totals** for year one, year two, the whole assignment and the multiple of home
  pay.
- **Audit trail**: every figure carries its derivation, and the gross-up iteration
  history and hypothetical Swiss tax working are available in an expandable panel.
- **Assumptions** are listed explicitly, and any unverified figure is flagged.
- **Official source citations**: every tax rule and immigration requirement links to
  a numbered official source (title, publisher, effective date, last-checked date).
- **Immigration tab** built from researched, structured content (routes, fees,
  processing times, employer/employee responsibilities, checklist).
- **CSV export** — download the current estimate as a `.csv` file containing the
  annual rows, totals and the numbered sources that justify them.
- **Scenario comparison** — a **Compare** tab that works a baseline and an
  alternative assignment side by side and shows the cost difference, reusing the
  same calculation engine.
- **Server-side validation** with readable error messages; calculation failures
  never produce misleading results.

## Tech stack

- **Python 3.14**
- **Django 6.1.2** (only runtime dependency — no third-party libraries in the
  calculation engine)
- SQLite (Django's default; the tool stores no user data) and Django's static-file
  handling for the demo
- Plain HTML templates + hand-written CSS/JS in `static/`
- `decimal.Decimal` throughout the calculation engine for deterministic money maths

## Project structure

```
costtool/        Django app — Cost Estimate tab (form, view, templates)
reference/       Django app — Immigration tab + official source registry
  sources.py       registry of 34 official sources (tax + immigration)
  immigration.py   structured immigration research content
  templatetags/    presentation filters (money, citations)
calculator/      pure-Python calculation engine (no Django imports)
config/          Django project (settings, urls, wsgi)
templates/       base layout + shared partials
static/          app.css, app.js
tests/           engine + form/view tests
docs/            REQUIREMENTS.md, ARCHITECTURE.md, RESEARCH.md, STAGE_REPORTS.md
manage.py
requirements.txt
```

All financial logic lives in the `calculator/` package, which has **no Django
dependency**. Views validate input, call the engine, catch typed exceptions and
render. Templates present only.

## Prerequisites

- Python 3.11 or newer (developed on 3.14; anything Django 6.1 supports will work)
- `pip`
- Git (only to clone the repository)

## Installation

1. Clone the repository and enter it:

   ```powershell
   git clone <your-repo-url> Cost-Tool
   cd Cost-Tool
   ```

2. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   (On macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`)

3. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

## Database and static files

The app uses SQLite. Apply the migrations once (this creates `db.sqlite3`):

```powershell
python manage.py migrate
```

Static files are served automatically while `DEBUG=1`, so no `collectstatic` step is
needed for local running.

## Running the app

```powershell
python manage.py runserver
```

Then open <http://127.0.0.1:8000/>.

## How to obtain an estimate

1. Open the **Cost Estimate** tab (`/`). The form is pre-filled with the supplied
   test case, so you can press **Calculate** immediately, or edit any field.
2. Set the assignment countries/cities and dates, the employee details (nationality,
   marital status, children, UK residency for each year), the home salary and bonus
   (CHF), the exchange rate (CHF per GBP) and the four assignment benefits.
3. Press **Calculate**. The two annual cost tables (sections A–D), the totals, the
   assumptions, the calculation working and the numbered sources are rendered below.
4. Press **Download CSV** to save the same estimate (annual rows, totals and the
   numbered sources) as a `.csv` file.
5. Open the **Compare** tab (`/compare/`) to work out a baseline and an alternative
   side by side, and open the **Immigration** tab (`/immigration/`) for the visa
   route, requirements, costs, steps and readiness checklist, each linked to an
   official source.

### Supplied test case

Zurich → London, 6 April 2026 to 5 April 2028; Swiss single employee, no children,
UK tax resident both years; salary CHF 150,000/yr plus bonus CHF 20,000/yr; housing
GBP 3,000/month (both years); relocation allowance CHF 5,000 cash and moving costs
GBP 6,000 and temporary accommodation GBP 4,000 (year one only); exchange rate
GBP 1 = CHF 1.10; 2026/27 UK rates used for both years. This is the default in the
form and is asserted by the test suite.

## Running the tests

```powershell
python manage.py test
```

The suite covers the progressive UK tax bands and personal-allowance taper, the
gross-up solver (convergence, tolerance, iteration history and non-convergence
handling), Swiss hypothetical tax/social security, employer charges, the full
supplied test case, currency conversion, form validation, view behaviour, source
integrity and the immigration content.

## Methodology

- **Tax equalisation**: gross home pay → minus hypothetical Swiss income tax and
  social security → **net home pay `I_base`**. `I = I_base + taxable benefits`.
- **Gross-up (employer-paid UK tax `T`)**: solve `T = UKTax(I + T)` by fixed-point
  iteration with a tolerance of GBP 0.01 and a maximum of 100 iterations (raising a
  `NonConvergenceError` otherwise). The iteration history is exposed as an audit
  trail (spec E03/E07/E10).
- **UK tax**: 2026/27 bands (basic/ higher/ additional) including the personal
  allowance withdrawal above GBP 100,000. **Employer National Insurance**: Class 1 at
  15% above the secondary threshold on Class 1 earnings, and Class 1A at 15% on
  benefits in kind. Employment Allowance and the Apprenticeship Levy are **not**
  applied (a conservative, documented choice).
- **Hypothetical Swiss tax**: federal (DBG) + Zurich cantonal/communal (at the 2026
  Steuerfuss) + AHV/IV/EO and ALV, for a single, non-church member, excluding BVG.
  Estimated standard deductions are documented as assumptions.
- **Benefits**: housing → benefit in kind; relocation cash → taxable cash; moving
  costs → not taxable (within the GBP 8,000 exemption); temporary accommodation →
  benefit in kind (documented assumption).

Full derivations, assumptions (A1–A10) and the research log live in
`docs/RESEARCH.md`; the calculation flow and design are in `docs/ARCHITECTURE.md`.

## Sources

Every rate, fee, threshold and requirement is backed by an official source, stored
in `reference/sources.py` (34 sources, each with title, URL, publisher, relevance,
effective date and last-checked date) and rendered as a numbered citation next to
the figure it justifies. The registry covers HMRC/GOV.UK tax guidance, the Swiss
Federal Tax Administration and Zurich cantonal tax data, and official UK
immigration guidance. See `docs/RESEARCH.md` for the research log.

## Known limitations

- The engine uses **2026/27 UK rates for both years** as instructed by the brief.
- **Employment Allowance and the Apprenticeship Levy are not modelled**; other
  employer costs (pension, payroll software, etc.) are out of scope.
- Hypothetical Swiss tax uses **estimated standard deductions** and does not apply
  final centime/franc rounding rules; these are flagged as assumptions.
- The **social-security jurisdiction option** (e.g. an A1 / certificate of coverage
  for a ≤24-month posting) is documented but not surfaced as an input, because a
  control that the engine ignores would mislead.
- The immigration tab is **researched guidance, not legal advice**; it cannot pick
  the exact visa route or SOC code for a specific case.

## Security notes

- No secrets are stored in the repository. `SECRET_KEY` and host/debug settings are
  read from environment variables (`DJANGO_SECRET_KEY`, `DJANGO_DEBUG`,
  `DJANGO_ALLOWED_HOSTS`) with a clearly-labelled development-only fallback.
- Django's security middleware and protections are enabled (CSRF, `X_FRAME_OPTIONS
  = DENY`, content-type sniffing protection, referrer policy), with additional
  hardening (HTTPS redirect, secure/HSTS cookies) automatically switched on when
  `DEBUG=0`.
- All input is validated server-side; invalid or non-convergent calculations are
  reported as readable messages, never as stack traces or misleading totals.

## AI usage

This application was developed with the assistance of an AI coding assistant
(opencode). The AI was used to:

- scaffold the Django project and app structure;
- help draft the calculation engine, views, forms, templates and tests;
- research and summarise official tax and immigration sources (which were then
  recorded with their URLs, effective dates and last-checked dates in
  `reference/sources.py` and `docs/RESEARCH.md`).

All financial logic is deterministic Python with an automated test suite, and every
rate/rule/fee is traceable to an official source listed in the app. The human
author reviewed, ran and accepted the code, and is responsible for the final
result. No AI-generated content was committed without being run against the tests.

## Demo video

A short (≤5 minute) walkthrough video is submitted with the repository and is linked
here once available: https://www.loom.com/share/528105f3e4c74cf894e96b8717d5467a

## License / attribution

Built as an assignment submission. Figures are estimates produced from the stated
assumptions and official sources, and must not be treated as tax or immigration
advice.
