# Requirements & Acceptance Checklist

Source: assignment specification "Assignment Cost Tool — Full-Stack Django Application".
Every mandatory item is tracked here. Status values: `TODO` / `DONE` / `BLOCKED`.

## 1. Mandatory acceptance gates (all must pass)

| # | Gate | Status |
|---|------|--------|
| G1 | Application runs by following the README on a clean machine | DONE |
| G2 | Immigration tab covers work permission, business visits and passports | DONE |
| G3 | Every displayed tax rule and immigration requirement has an official source link | DONE |
| G4 | No secrets appear in files or Git history | DONE |
| G5 | Repository is original (not a fork), >= 5 commits across >= 2 different days | BLOCKED |
| G6 | README documents AI usage | DONE |
| G7 | Exact supplied test case accepted; produces two annual cost tables with no source-code edits | DONE |
| G8 | Backend uses Python and Django | DONE |
| G9 | >= 1 automated test exists and passes | DONE |
| G10 | Invalid input returns a readable error | DONE |
| G11 | Repository and video submitted within deadline | TODO |
| G12 | Loom walkthrough <= 5 minutes | TODO |
| G13 | >= 1 test-case figure/requirement agrees with its cited official source | DONE |

> **G5/C6 note:** there are 5+ meaningful commits but all are currently dated the
> same day. The ">= 2 different days" condition requires at least one commit on a
> later calendar day; commits must not be back-dated, so this is completed by
> committing follow-up work on a subsequent day.

## 2. Assessment checks 1-14

| # | Check | Status |
|---|-------|--------|
| C1 | Runs from clean install per README | DONE |
| C2 | Immigration: work permission, business visits, passports covered | DONE |
| C3 | Official source link on every tax rule and immigration requirement | DONE |
| C4 | No secrets in files or history | DONE |
| C5 | Original repo, not a fork | DONE |
| C6 | >= 5 commits across >= 2 days | BLOCKED |
| C7 | README documents AI usage | DONE |
| C8 | Supplied test case produces two annual cost tables | DONE |
| C9 | Python + Django backend | DONE |
| C10 | Automated tests exist and pass | DONE |
| C11 | Invalid input -> readable error | DONE |
| C12 | Repo + video submitted on time | TODO |
| C13 | Loom <= 5 minutes | TODO |
| C14 | >= 1 test-case figure agrees with cited official source | DONE |

## 3. Functional requirements

### 3.1 Interface
- [x] F01 Two primary tabs: **Cost Estimate** and **Immigration**
- [x] F02 Cost Estimate form: countries, cities, dates, employee details, salary, bonus, benefits, exchange rate
- [x] F03 Results shown per UK tax year (year one, year two) with sections in order A, B, C, D
- [x] F04 Section A — Home Pay: base salary, bonus, currency conversion, hypothetical Swiss income tax, hypothetical Swiss social security
- [x] F05 Section B — Assignment Benefits: housing, relocation, moving costs, temporary accommodation; each with amount, currency, year, UK tax classification (taxable cash / benefit in kind / not taxable)
- [x] F06 Section C — Host Tax and Employer Charges: employer-paid UK income tax, tax-on-tax gross-up, employer charges, detailed calculation breakdown
- [x] F07 Section D — Deductions: hypothetical Swiss income tax, Swiss social security, effect on employer-cost calculation
- [x] F08 Totals: year one, year two, whole assignment, cost as multiple of home pay
- [x] F09 Assumptions and calculation working displayed
- [x] F10 Official source links displayed for applicable rules
- [x] F11 Immigration tab: route, business visit visa need, passport requirements, employer/subsidiary responsibilities, application steps, fees, processing times, official links
- [x] F12 Immigration distinguishes mandatory legal requirements vs recommendations vs estimates
- [x] F13 Responsive, professional, accessible UI (labels, keyboard, help text, empty/success/error states)

### 3.2 Exact test case (must be accepted without code changes)
- [x] T01 Zurich -> London, 6 Apr 2026 to 5 Apr 2028 (two full UK tax years)
- [x] T02 Employee: Swiss, single, no children, 3 years prior Zurich employment, UK tax resident both years, leaves Swiss tax residence
- [x] T03 Swiss company -> UK subsidiary with UK payroll
- [x] T04 Salary CHF 150,000/yr; bonus CHF 20,000/yr
- [x] T05 Housing GBP 3,000/month paid direct to landlord (both years)
- [x] T06 Relocation allowance CHF 5,000 cash, year one only
- [x] T07 Moving costs GBP 6,000, year one only
- [x] T08 Temporary housing GBP 4,000 (4 weeks), year one only
- [x] T09 Exchange rate GBP 1 = CHF 1.10, editable, applied to both years by default
- [x] T10 2026/27 UK rates used for both years
- [x] T11 Hypothetical Swiss income tax: federal + cantonal + communal, single, Zurich, no church tax
- [x] T12 Hypothetical Swiss social security: AHV/IV/EO + unemployment insurance; **exclude BVG**
- [x] T13 Social security jurisdiction determined and rule explained (EU/EFTA coordination - Switzerland not EU; UK-Switzerland Convention on social security to be researched)
- [x] T14 Year-one-only benefits not charged in year two

### 3.3 Calculation engine
- [x] E01 Engine in dedicated Python modules, separate from views/templates
- [x] E02 Tax equalisation: I = net home pay after hypothetical Swiss deductions + taxable assignment benefits
- [x] E03 Employer-paid UK tax T solves T = UKTax(I + T) by **iterative** solution
- [x] E04 Correct progressive UK bands applied
- [x] E05 Personal allowance withdrawal above GBP 100,000 handled
- [x] E06 Tax-on-tax included in employer-paid tax
- [x] E07 Defined convergence tolerance and maximum iteration count
- [x] E08 Non-convergence handled safely (no misleading results)
- [x] E09 Intermediate precision preserved; consistent display rounding
- [x] E10 Gross-up iteration history exposed (audit trail)
- [x] E11 No double counting of salary, benefits, taxes, deductions
- [x] E12 Treatment of taxable benefits and employer charges documented
- [x] E13 Assumptions stated explicitly for ambiguous calculations; unverified figures flagged

### 3.4 Research and sources
- [x] R01 GOV.UK Income Tax rates and Personal Allowances
- [x] R02 GOV.UK employer rates/thresholds 2026/27
- [x] R03 HMRC HS212 tax equalisation guidance
- [x] R04 HMRC PAYE72028 grossing up guidance
- [x] R05 GOV.UK social security: workers coming to UK from Switzerland
- [x] R06 Swiss Federal Tax Administration tax calculator
- [x] R07 Official UK immigration/passport/visa/employer guidance
- [x] R08 Each source shows title, relevance, effective date/tax year, last-checked date
- [x] R09 No unofficial source as sole authority for legal/tax/immigration conclusion
- [x] R10 Unverifiable official figures flagged as unresolved, never fabricated

### 3.5 Tests (Django TestCase / Python unittest)
- [x] P01 Supplied test case generates results for both years
- [x] P02 Year-one-only benefits absent from year two
- [x] P03 Currency conversion uses supplied rate correctly
- [x] P04 Progressive tax correct at band boundaries
- [x] P05 Personal allowance withdrawal handled correctly
- [x] P06 Gross-up satisfies T = UKTax(I + T) within tolerance
- [x] P07 Non-convergence handled safely
- [x] P08 Employer charges applied per documented assumptions
- [x] P09 Annual totals reconcile with component rows
- [x] P10 Missing/invalid form fields produce readable errors
- [x] P11 Scenario comparisons reuse same calculation logic
- [x] P12 CSV export contains expected annual data and source references

### 3.6 Security and error handling
- [x] S01 Django security protections enabled (CSRF, clickjacking, etc.)
- [x] S02 Server-side validation; reject invalid exchange rates / numeric values
- [x] S03 Assignment dates and required fields validated
- [x] S04 Calculation failures never produce misleading results
- [x] S05 Exceptions handled gracefully; no stack traces to users
- [x] S06 No hard-coded credentials/secrets; secrets never in Git

### 3.7 README / GitHub / demo
- [x] M01 README: overview, features, stack, prerequisites, install, venv, dependencies, migration, run commands, how to obtain an estimate, test commands, methodology, sources, known limitations, AI usage, Loom link (only real links)
- [ ] M02 >= 5 meaningful commits across >= 2 days from candidate account, original repo
- [ ] M03 Loom walkthrough <= 5 min covering tabs, test case, audit trail, gross-up code, sources/tests

### 3.8 Secondary enhancements (only after mandatory work)
- [x] X01 Calculation audit trail UI (bands, deductions, iterations, intermediates)
- [x] X02 Scenario comparison reusing the engine
- [x] X03 Client + server input validation
- [x] X04 CSV export
- [x] X05 Immigration readiness checklist with timelines and links

## 4. Research questions to resolve (Stage 3)

1. UK 2026/27 income tax rates, bands and personal allowance (and withdrawal taper) - verify on GOV.UK.
2. Employer NIC rate/threshold for 2026/27 and any UK apprentice levy applicability - verify on GOV.UK.
3. Correct treatment of foreign-only employment income under PAYE when employer is not a UK tax resident (ET-assessment vs PAYE) - HS212/EMP series.
4. Grossing-up method prescribed by PAYE72028 and interaction with tax code / cumulative basis.
5. Social security coordination: UK-Switzerland bilateral convention - certificate of coverage, which system applies.
6. Swiss hypothetical tax: federal + Zurich cantonal/communal rates for a single non-church member - Swiss Federal Tax Administration calculator.
7. Swiss AHV/IV/EO + ALV contribution rates and ceilings 2026 (exclude BVG).
8. UK immigration route for a Swiss national employed by a UK subsidiary (Skilled Worker sponsorship, salary thresholds, Swiss trade deal exemptions if any).
9. Visa-free business visits for Swiss nationals; permitted activities; ETIAS/ETA requirements for short visits.
10. Passport validity rules for UK entry; Swiss passport requirements.
11. Immigration fees and processing times (Home Office published fee schedule and service standards).
