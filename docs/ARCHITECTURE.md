# Architecture & File Structure — Stage 1

## 1. Design principles

- **Separation of concerns**: all financial logic lives in a pure-Python `calculator/` package with no Django dependency (no ORM, no request objects). Views are thin: validate -> call engine -> render. Templates contain presentation only.
- **Determinism**: the engine is a pure function of an input dataclass. Same inputs -> same outputs. This makes tests, CSV export and scenario comparison trivially reuse one code path.
- **Traceability**: every monetary figure rendered in the UI carries its derivation (formula, source, intermediate values) so the audit trail is first-class data, not reconstructed log text.
- **Research-backed**: tax/immigration rules are stored as data records with official URLs, effective dates and last-checked dates, rendered next to the figures they justify.
- **Fail loud, fail safe**: invalid or non-convergent calculations raise typed exceptions that the view converts into readable messages; partial/misleading totals are never displayed.

## 2. Layer diagram

```
Browser (tabs: Cost Estimate | Immigration)
   |  GET/POST, CSRF
Django views (cost, immigration, export)      -> form validation (Django Form)
   |  calls                                    -> error mapping to readable messages
Calculator engine (pure Python)
   ├── models.py        input/output dataclasses
   ├── uk_tax.py        progressive bands, PA taper, UKTax(income)
   ├── grossup.py       iterative solver T = UKTax(I + T), history, tolerance
   ├── swiss_tax.py     hypothetical federal+cantonal+communal income tax
   ├── swiss_social.py  AHV/IV/EO + ALV (BVG excluded)
   ├── employer_charges.py  employer NIC etc. (documented assumptions)
   ├── assignment.py    per-year orchestration, benefit classification, totals
   └── rounding.py      Decimal policy, display rounding
Reference data (Django app `reference`)
   ├── rules.py / fixtures   official sources + rule records
   └── immigration.py        researched immigration content (structured data)
Templates + static (CSS/JS)
Tests (tests/ package, Django TestCase + unittest)
```

## 3. Proposed file structure

```
Cost-Tool/
├── .gitignore                    # venv, db, __pycache__, .env, media
├── README.md                     # see spec §11
├── requirements.txt              # Django pinned
├── manage.py
├── config/                       # Django project package
│   ├── __init__.py
│   ├── settings.py               # security defaults, sqlite, templates, static
│   ├── urls.py
│   └── wsgi.py / asgi.py
├── calculator/                   # pure engine, NO django imports
│   ├── __init__.py
│   ├── models.py                 # AssignmentInputs, EmployeeDetails, Benefit,
│   │                             #   YearResult, SectionARow... dataclasses
│   ├── rounding.py               # Decimal helpers, quantise policy
│   ├── uk_tax.py                 # TaxYear2026 rates, bands, taper, compute_uk_tax()
│   ├── grossup.py                # solve_gross_up(), GrossUpResult(history, converged)
│   ├── swiss_tax.py              # hypothetical Swiss income tax
│   ├── swiss_social.py           # AHV/IV/EO + ALV
│   ├── employer_charges.py       # employer NIC, documented assumptions
│   ├── benefits.py               # benefit classification (taxable cash/BIK/NTA)
│   ├── assignment.py             # run_assignment(inputs) -> AssignmentResult
│   └── exceptions.py             # CalculationError, NonConvergenceError, ValidationError
├── reference/                    # Django app: official sources + rule citations
│   ├── __init__.py / apps.py / admin.py
│   ├── models.py                 # Source(title, url, relevance, effective, checked)
│   ├── sources.py                # SOURCE registry (data) used by templates/tests
│   ├── immigration.py            # structured immigration research content
│   ├── templatetags/
│   │   └── reference_tags.py     # filters: money, source lookup
│   └── management/commands/      # (optional) verify sources
├── costtool/                     # Django app: cost estimate tab
│   ├── __init__.py / apps.py / admin.py
│   ├── forms.py                  # AssignmentForm (server-side validation)
│   ├── views.py                  # cost_estimate, scenario_compare, csv_export
│   ├── urls.py
│   ├── exporters.py              # CSV building
│   └── templates/costtool/
│       ├── cost_estimate.html    # form + results tabs/sections
│       ├── _results.html         # sections A-D partials
│       ├── audit_trail.html
│       ├── scenario_compare.html
│       └── csv_preview (none)
├── immigrationapp/ (or served by `reference` views)
│   └── views.py -> reference.immigration content
├── templates/
│   ├── base.html                 # nav, tabs, footer, source-citation macro
│   └── includes/
│       ├── source_ref.html       # renders [1] title, relevance, date, checked
│       └── form_field.html       # label + help text + errors
├── static/
│   ├── css/app.css               # restrained palette, tables, responsive grid
│   └── js/app.js                 # tab switching, client-side validation, compare
├── tests/                        # top-level test package (also app tests/)
│   ├── __init__.py
│   ├── test_uk_tax.py            # band boundaries, PA taper (P04, P05)
│   ├── test_grossup.py           # convergence, tolerance, history, non-conv (P06,P07)
│   ├── test_swiss.py             # hypothetical tax/social consistency
│   ├── test_assignment.py        # supplied test case, year-2 exclusion, totals (P01,P02,P09)
│   ├── test_currency.py          # FX conversion (P03)
│   ├── test_employer_charges.py  # P08
│   ├── test_forms_views.py       # validation errors, HTTP flows (P10)
│   ├── test_csv_export.py        # P12
│   └── test_scenario.py          # P11
├── docs/
│   ├── REQUIREMENTS.md           # acceptance checklist (Stage 1)
│   ├── ARCHITECTURE.md           # this file
│   ├── RESEARCH.md               # source log: title/url/relevance/checked
│   └── STAGE_REPORTS.md          # per-stage files, decisions, results, next commands
└── .gitignore
```

> Note: `immigration` content is delivered as its own tab via the `reference` app (data-driven) so the Cost tab stays focused. Final app split will be confirmed at Stage 5.

## 4. Key data models (engine, not ORM)

```python
@dataclass(frozen=True)
class AssignmentInputs:
    home_country, home_city, host_country, host_city: str
    start_date, end_date: date
    nationality, marital_status: str
    children: int
    uk_tax_resident_year1, uk_tax_resident_year2: bool
    base_salary_home: Decimal          # CHF
    bonus_home: Decimal                # CHF
    fx_gbp_to_home: Decimal            # CHF per GBP, editable
    housing_gbp_month: Decimal
    relocation_home: Decimal           # CHF, year 1 only
    moving_gbp: Decimal                # year 1 only
    temp_accom_gbp: Decimal            # year 1 only
    uk_tax_year_label: str = "2026/27"

@dataclass
class MoneyLine:                        # one row in A/B/C/D
    label, section, year, amount, currency, amount_gbp, amount_home
    classification: str                 # TAXABLE_CASH | BIK | NOT_TAXABLE | DEDUCTION
    derivation: str                     # formula text
    source_ids: tuple[str, ...]

@dataclass
class GrossUpResult:
    T: Decimal; I: Decimal
    history: list[IterationRecord]      # n, taxable_income, tax, abs_error
    converged: bool; iterations: int; tolerance: Decimal

@dataclass
class YearResult: year_label, section_a/b/c/d: list[MoneyLine], totals...

@dataclass
class AssignmentResult:
    years: list[YearResult]
    total_employer_cost, total_home_pay, multiple: Decimal
    assumptions: list[Assumption]
    gross_up_history: dict[year, GrossUpResult]
```

## 5. Calculation flow (per tax year)

1. **FX**: convert CHF salary/bonus to GBP with the supplied rate (and GBP benefits to CHF for display).
2. **Section A**: gross home pay (GBP) → minus hypothetical Swiss income tax → minus hypothetical Swiss social security → **net home pay (I_base)**.
3. **Section B**: classify benefits; taxable ones added to `I`; non-taxable ones added to employer cost but **not** to `I`.
4. **Section C**: solve `T = UKTax(I + T)` iteratively (tolerance e.g. GBP 0.01, max 100 iterations, `NonConvergenceError` on failure). Employer charges computed on the derived taxable pay per documented assumption.
5. **Section D**: restate hypothetical Swiss deductions and show their effect (they reduce `I`, which reduces employer-paid UK tax — that is the equalisation benefit).
6. **Totals**: A(gross) + B(taxable & non-taxable) + C(employer tax & charges) − D is expressed as an explicit reconciliation so rows sum to the headline total (test P09).

## 6. Validation & error strategy

- **Client**: `required` attributes, `type=number`/`min`/`step`, date range check, JS messages mirroring server rules (enhancement X03).
- **Server**: Django `Form` with `clean_*` methods: end_date > start_date, fx > 0, non-negative money, marital/nationality in choices, required fields. Errors rendered per-field with help text.
- **Engine**: raises `CalculatorValidationError` / `NonConvergenceError`; views catch and render an error alert with no traceback. DEBUG=False, standard Django security middleware, CSRF on all POSTs.

## 7. Testing strategy

- **Unit (pure)**: `unittest.TestCase` for `uk_tax`, `grossup`, `swiss_*` — band-boundary and property tests (e.g. `UKTax(x)` monotonic; gross-up fixed point `|T - UKTax(I+T)| <= tol`).
- **Integration**: `django.test.TestCase` for forms/views/CSV/export and the full supplied test case.
- **Verified expectations**: at least one figure cross-checked against an official source (e.g. 2026/27 personal allowance/rate bands from GOV.UK) → gate G13/C14. All other numbers tested by internal consistency/properties, per spec.

## 8. Research-first rule

No rate, fee, threshold or immigration claim enters code/content without:
1. an official URL (GOV.UK / HMRC / admin.ch / gov.uk immigration pages),
2. an entry in `docs/RESEARCH.md` + `reference/sources.py` with title, relevance, effective date, last-checked date,
3. a template citation rendered beside the figure.
Unverified items are labelled "unresolved - not verified" in the UI (spec §6).

## 9. Stage 1 deliverables

- `docs/REQUIREMENTS.md` — acceptance checklist (created)
- `docs/ARCHITECTURE.md` — this file (created)
- `docs/STAGE_REPORTS.md` — appended with Stage 1 report (created)
- `git init` + first commit (created)

## 10. Next stage

**Stage 2 — Project setup**: scaffold Django project `config` + apps (`costtool`, `reference`), settings with security defaults, requirements.txt, .gitignore, confirm `python manage.py migrate && python manage.py runserver` serves a placeholder base template with the two tabs, add Stage 2 report and commit.
