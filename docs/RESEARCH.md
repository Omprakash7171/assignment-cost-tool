# Research Log (Stage 3)

Source of truth for every rate, threshold, tariff and rule used by the engine.
Each item records the official URL, its relevance, the effective period and the
date it was last checked. The machine-readable equivalent is
`reference/sources.py`; every source id referenced by a rendered money line must
resolve to an entry there (test `tests/test_sources.py`).

Last updated: 2026-10-14.

## 1. United Kingdom

### 1.1 Income tax 2026/27
| id | title | url | relevance | effective |
|----|-------|-----|-----------|-----------|
| uk_income_tax_2026_27 | Income Tax rates and Personal Allowances | https://www.gov.uk/income-tax-rates | Personal allowance £12,570; 20% / 40% / 45% bands; £100,000 taper (£1 per £2) | 6 Apr 2026 – 5 Apr 2027 |

Derived (implemented in `calculator/uk_tax.py`):
- Personal allowance £12,570, withdrawn by £1 for every £2 of income over
  £100,000 (zero at £125,140).
- Bands on **taxable** income: 20% on first £37,700; 40% on £37,700–£125,140;
  45% above £125,140.

### 1.2 Employer/employee NIC and other charges 2026/27
| id | title | url | relevance | effective |
|----|-------|-----|-----------|-----------|
| uk_employer_rates_2026_27 | Rates and thresholds for employers 2026 to 2027 | https://www.gov.uk/guidance/rates-and-thresholds-for-employers-2026-to-2027 | Employer NIC 15%, secondary threshold £5,000, Class 1A 15%, employee thresholds, Employment Allowance | 6 Apr 2026 – 5 Apr 2027 |

Derived (implemented in `calculator/employer_charges.py`,
`calculator/employee_nic.py`):
- Employer Class 1 NIC 15% above £5,000 (no upper cap for employers).
- Employer Class 1A NIC 15% on benefits in kind.
- Employee Class 1 NIC 8% between £12,570 and £50,270, 2% above (memo only).
- Employment Allowance and Apprenticeship Levy **not applied** (documented
  assumptions; conservative).

### 1.3 Tax equalisation and grossing up
| id | title | url | relevance |
|----|-------|-----|-----------|
| hmrc_hs212 | Tax equalisation (HS212) | https://www.gov.uk/government/publications/tax-equalisation-hs212-self-assessment-helpsheet/tax-equalisation-2026-hs212 | Employer-borne equalisation payments |
| hmrc_paye72028 | PAYE manual PAYE72028 (grossing up) | https://www.gov.uk/hmrc-internal-manuals/paye-manual/paye72028 | Iterative gross-up to a fixed net amount |

### 1.4 Benefits
| id | title | url | relevance |
|----|-------|-----|-----------|
| uk_living_accommodation | Expenses and benefits: accommodation | https://www.gov.uk/expenses-and-benefits-accommodation | Employer accommodation = benefit in kind (P11D, Class 1A); value basis |
| uk_relocation_exemption | Expenses and benefits: relocation | https://www.gov.uk/expenses-and-benefits-relocation | Qualifying relocation expenses exempt up to £8,000; cash allowance taxable |

### 1.5 Social security jurisdiction
| id | title | url | relevance |
|----|-------|-----|-----------|
| uk_ss_switzerland | Social security contributions: workers coming to the UK from the EEA or Switzerland | https://www.gov.uk/government/publications/help-with-short-term-business-visitors-gfc19/national-insurance-contributions-part-3 | General rule: contributions where the work is performed; detached-worker / certificate-of-coverage exception up to 24 months |

> The engine defaults to UK NIC (`employer_social_security_uk=True`). The
> assignment is exactly 24 months, so a Swiss A1 / certificate of coverage could
> in principle be sought; this is surfaced in the UI as an option (Stage 4/5).

## 2. Switzerland

### 2.1 Federal direct tax (DBG) single tariff 2026
| id | title | url | relevance | effective |
|----|-------|-----|-----------|-----------|
| estv_58c_2026 | Form 58c 2026 – direct federal tax tariffs, natural persons | https://www.estv.admin.ch/de/steuertarife-zur-direkten-bundessteuer | Single-person federal tariff | tax period 2026 |
| swiss_fta_calculator | Swiss federal tax calculator (ESTV) | https://swisstaxcalculator.estv.admin.ch/ | Authoritative cross-check | current |

Derived from the official Form 58c 2026 (`calculator/swiss_tax.py`,
`FEDERAL_SINGLE_ANCHORS`) — cumulative tax at published points:

| taxable income (CHF) | cumulative tax (CHF) | marginal |
|---------------------:|---------------------:|---------:|
| 0 – 15,200 | 0 | 0% |
| 15,200 | 0 | 0.77% |
| 33,200 | 138.60 | 0.88% |
| 43,400 | 228.36 | 2.64% |
| 58,000 | 612.00 | 2.97% |
| 76,200 | 1,152.50 | 5.94% |
| 82,100 | 1,502.95 | 6.60% |
| 108,900 | 3,271.75 | 8.80% |
| 141,500 | 6,140.55 | 11.00% |
| 185,100 | 10,936.55 | 13.20% |
| 793,900 | 91,298.15 | 11.50% |

Above CHF 793,900 the federal tax is a uniform **11.5% of the whole taxable
income** (Form 58c footnote: "Für höhere steuerbare Einkünfte beträgt die
Jahressteuer einheitlich 11.5 %"). Form 58c also reduces the tax by CHF 263 per
child — not applicable (no children).

### 2.2 Zurich cantonal tariff (section 35 (1), Grundtarif) – from 1 Jan 2026
| id | title | url | relevance | effective |
|----|-------|-----|-----------|-----------|
| zh_stg_35 | Zurich Tax Act (StG 631.1), § 35 income-tax tariffs | https://www.notes.zh.ch/appl/zhlex_r.nsf/WebView/27A2B2527CE30B98C1258D2A0028E439/$File/631.1_8.6.97_131.pdf | Single-person "Grundtarif" | from 1 Jan 2026 |
| zh_stgb_34_1 | ZStB Nr. 34.1 – social deductions and tax tariffs (from 2026) | https://www.zh.ch/de/steuern-finanzen/steuern/treuhaender/steuerbuch/steuerbuch-definition/zstb-34-1.html | Index-adjusted deductions/tariffs | from 17 Mar 2026 |

Brackets (taxable income, CHF): 0% first 7,000; 2% next 5,000; 3% next 4,800;
4% next 8,000; 5% next 9,700; 6% next 11,200; 7% next 13,100; 8% next 17,600;
9% next 34,000; 10% next 33,700; 11% next 53,300; 12% next 69,300; 13% above
266,700.

### 2.3 Zurich Steuerfuss 2026
| id | title | url | relevance | effective |
|----|-------|-----|-----------|-----------|
| estv_steuerfuss_2026 | Steuersatz und Steuerfuss, Jan 2026 | https://www.estv2.admin.ch/stp/ds/e-steuersatz-steuerfuss-de.pdf | Canton capitals 2026: Zurich 95% + 119% | tax period 2026 |

Corroborated by the canton (`https://www.zh.ch/de/steuern-finanzen/steuern/steuerstatistiken/aktuelle-gemeinde-steuerfuesse.html`:
"für die Jahre 2026 und 2027 bei 95 Prozent") and the city
(`https://www.stadt-zuerich.ch/de/lebenslagen/steuern/juristische-personen/steuerberechnung-steuerfuss.html`:
Gemeindesteuerfuss 119%).

**Decision:** the cantonal/communal multiple is **95% + 119% = 214%** of the
simple cantonal tax (the canton reduced the Staatssteuerfuss from 98% to 95% for
2026/2027). Church tax is excluded (no church membership). This supersedes the
earlier working note of 217%.

### 2.4 Social security (AHV/IV/EO + ALV) 2026
| id | title | url | relevance |
|----|-------|-----|-----------|
| ahv_iv_eo_2026 | AHV/IV/EO contribution rates | https://www.ahv-iv.ch/en/Social-insurances/Old-age-and-survivors-insurance/Contributions | Employee 5.3%, **no ceiling** |
| alv_2026 | Unemployment insurance (ALV) | https://www.ahv-iv.ch/en/Social-insurances/Unemployment-insurance | Employee 1.1% up to CHF 148,200 |

BVG / occupational pension is excluded per spec T12.

## 3. Modelling assumptions (spec E13)

| # | Assumption |
|---|------------|
| A1 | UK 2026/27 rates applied to both assignment years (spec T10). |
| A2 | Framework is a **net cost** model: employer pays net home pay + benefits + UK tax (gross-up) + employer NICs. |
| A3 | `I = net home pay + taxable benefits`; gross-up solves `T = UKTax(I + T)`. |
| A4 | Hypothetical Swiss tax is computed on salary + bonus only (the one-off relocation allowance and the moving/temporary-accommodation costs are UK-side assignment benefits). |
| A5 | Hypothetical Swiss standard deductions are **estimates**: professional expenses CHF 4,000 and insurance-premium deduction CHF 2,900; health-insurance premiums and pillar 3a are not modelled. |
| A6 | The employee's own Class 1 NIC is a memo only — not grossed up, not deducted from `I` (the spec grosses up income tax only). |
| A7 | Temporary accommodation is treated as a taxable BIK (a temporary-workplace exemption could apply for up to 24 months). |
| A8 | The employer-provided flat's BIK cash equivalent is taken equal to the rent paid. |
| A9 | Employer NIC/Class 1A computed on grossed-up values; Employment Allowance and Apprenticeship Levy not applied. |
| A10 | Final federal/ cantonal tax rounding rules (round federal tax down to the next 5 centimes, ignore fractions below CHF 100) are not applied; values are shown to the penny. |

## 4. Open / unresolved

- GOV.UK living-accommodation page resolved to
  `https://www.gov.uk/expenses-and-benefits-accommodation` (used).
- Hypothetical Swiss deduction amounts (A5) remain estimates pending a manual
  run of the ESTV/ZH calculators; flagged in the UI.
- Immigration research (routes, fees, processing times, passports, ETA) is
  deferred to Stage 5.
