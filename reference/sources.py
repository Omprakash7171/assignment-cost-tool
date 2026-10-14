"""Registry of official sources cited by the tool.

Every tax rate, threshold and immigration requirement displayed by the
application must resolve to an entry here (gate G3/C3, spec R08). Each entry
records the title, the official URL, its relevance, the effective period and
the date it was last checked.

This module contains data only (no Django imports) so it can be unit-tested and
imported from the engine and the exporter.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Source:
    id: str
    title: str
    url: str
    publisher: str
    relevance: str
    effective: str
    last_checked: str
    category: str  # "tax" or "immigration"


SOURCES = {
    "uk_income_tax_2026_27": Source(
        id="uk_income_tax_2026_27",
        title="Income Tax rates and Personal Allowances",
        url="https://www.gov.uk/income-tax-rates",
        publisher="GOV.UK (HMRC)",
        relevance=(
            "Personal allowance (GBP 12,570), 20/40/45% bands and the GBP "
            "100,000 personal-allowance taper used for the gross-up."
        ),
        effective="6 April 2026 to 5 April 2027",
        last_checked="2026-10-14",
        category="tax",
    ),
    "uk_employer_rates_2026_27": Source(
        id="uk_employer_rates_2026_27",
        title="Rates and thresholds for employers 2026 to 2027",
        url="https://www.gov.uk/guidance/rates-and-thresholds-for-employers-2026-to-2027",
        publisher="GOV.UK (HMRC)",
        relevance=(
            "Employer NIC rate 15%, secondary threshold GBP 5,000, Class 1A "
            "NIC 15%, employee NIC thresholds, Employment Allowance."
        ),
        effective="6 April 2026 to 5 April 2027",
        last_checked="2026-10-14",
        category="tax",
    ),
    "hmrc_hs212": Source(
        id="hmrc_hs212",
        title="Tax equalisation (HS212 helpsheet)",
        url=(
            "https://www.gov.uk/government/publications/tax-equalisation-hs212-"
            "self-assessment-helpsheet/tax-equalisation-2026-hs212"
        ),
        publisher="HMRC",
        relevance=(
            "Definition and treatment of tax equalisation payments borne by "
            "the employer."
        ),
        effective="2026 tax year",
        last_checked="2026-10-14",
        category="tax",
    ),
    "hmrc_paye72028": Source(
        id="hmrc_paye72028",
        title="PAYE manual: PAYE72028 - Grossing up",
        url="https://www.gov.uk/hmrc-internal-manuals/paye-manual/paye72028",
        publisher="HMRC",
        relevance=(
            "Iterative grossing-up of employer-paid tax so that the employee "
            "receives a fixed net amount."
        ),
        effective="current manual",
        last_checked="2026-10-14",
        category="tax",
    ),
    "uk_living_accommodation": Source(
        id="uk_living_accommodation",
        title="Expenses and benefits: accommodation",
        url="https://www.gov.uk/expenses-and-benefits-accommodation",
        publisher="GOV.UK (HMRC)",
        relevance=(
            "Employer-provided accommodation is a benefit in kind reported on "
            "P11D, with Class 1A NIC; value basis and exemption conditions."
        ),
        effective="current",
        last_checked="2026-10-14",
        category="tax",
    ),
    "uk_relocation_exemption": Source(
        id="uk_relocation_exemption",
        title="Expenses and benefits: relocation (what's exempt)",
        url="https://www.gov.uk/expenses-and-benefits-relocation",
        publisher="GOV.UK (HMRC)",
        relevance=(
            "Qualifying relocation expenses are exempt up to GBP 8,000; a cash "
            "relocation allowance is taxable earnings."
        ),
        effective="current",
        last_checked="2026-10-14",
        category="tax",
    ),
    "uk_ss_switzerland": Source(
        id="uk_ss_switzerland",
        title=(
            "Social security contributions for workers coming to the UK from "
            "the EEA or Switzerland"
        ),
        url=(
            "https://www.gov.uk/government/publications/help-with-short-term-"
            "business-visitors-gfc19/national-insurance-contributions-part-3"
        ),
        publisher="GOV.UK (HMRC)",
        relevance=(
            "Social-security jurisdiction where the work is performed; the "
            "UK-Switzerland convention and certificate-of-coverage rules."
        ),
        effective="current",
        last_checked="2026-10-14",
        category="tax",
    ),
    "estv_58c_2026": Source(
        id="estv_58c_2026",
        title="Form 58c 2026 - Direct federal tax tariffs, natural persons",
        url="https://www.estv.admin.ch/de/steuertarife-zur-direkten-bundessteuer",
        publisher="Swiss Federal Tax Administration (ESTV)",
        relevance=(
            "Single-person federal direct tax tariff 2026 used for the "
            "hypothetical home-country tax."
        ),
        effective="tax period 2026",
        last_checked="2026-10-14",
        category="tax",
    ),
    "estv_steuerfuss_2026": Source(
        id="estv_steuerfuss_2026",
        title="Steuersatz und Steuerfuss (E. Steuerbegriffe), January 2026",
        url="https://www.estv2.admin.ch/stp/ds/e-steuersatz-steuerfuss-de.pdf",
        publisher="Swiss Federal Tax Administration (ESTV)",
        relevance=(
            "Steuerfuss of the canton capitals 2026: Zurich canton 95%, city "
            "119% for natural persons."
        ),
        effective="tax period 2026",
        last_checked="2026-10-14",
        category="tax",
    ),
    "zh_stg_35": Source(
        id="zh_stg_35",
        title="Zurich Tax Act (StG 631.1), section 35 - income tax tariffs",
        url=(
            "https://www.notes.zh.ch/appl/zhlex_r.nsf/WebView/"
            "27A2B2527CE30B98C1258D2A0028E439/$File/631.1_8.6.97_131.pdf"
        ),
        publisher="Canton of Zurich",
        relevance=(
            "Cantonal 'Grundtarif' (single persons) used for the cantonal and "
            "communal hypothetical tax."
        ),
        effective="from 1 January 2026",
        last_checked="2026-10-14",
        category="tax",
    ),
    "zh_stgb_34_1": Source(
        id="zh_stgb_34_1",
        title=(
            "ZStB Nr. 34.1 - Directive on social deductions and tax tariffs "
            "(from tax period 2026)"
        ),
        url=(
            "https://www.zh.ch/de/steuern-finanzen/steuern/treuhaender/"
            "steuerbuch/steuerbuch-definition/zstb-34-1.html"
        ),
        publisher="Canton of Zurich, Finance Directorate",
        relevance=(
            "Index-adjusted deductions and tariffs for the 2026 tax period."
        ),
        effective="from 17 March 2026 (tax period 2026)",
        last_checked="2026-10-14",
        category="tax",
    ),
    "ahv_iv_eo_2026": Source(
        id="ahv_iv_eo_2026",
        title="AHV/IV/EO contribution rates",
        url="https://www.ahv-iv.ch/en/Social-insurances/Old-age-and-survivors-insurance/Contributions",
        publisher="Swiss Compensation Offices (AHV/IV)",
        relevance=(
            "Employee AHV/IV/EO contribution of 5.3% with no salary ceiling."
        ),
        effective="2026",
        last_checked="2026-10-14",
        category="tax",
    ),
    "alv_2026": Source(
        id="alv_2026",
        title="Unemployment insurance (ALV) contribution and insured ceiling",
        url="https://www.ahv-iv.ch/en/Social-insurances/Unemployment-insurance",
        publisher="Swiss Compensation Offices (AHV/IV)",
        relevance=(
            "Employee ALV contribution of 1.1% up to the annual insured "
            "ceiling of CHF 148,200."
        ),
        effective="2026",
        last_checked="2026-10-14",
        category="tax",
    ),
    "swiss_fta_calculator": Source(
        id="swiss_fta_calculator",
        title="Swiss federal tax calculator (ESTV)",
        url="https://swisstaxcalculator.estv.admin.ch/",
        publisher="Swiss Federal Tax Administration (ESTV)",
        relevance=(
            "Authoritative reference for the hypothetical Swiss tax; the "
            "engine re-implements the published 2026 tariffs."
        ),
        effective="current",
        last_checked="2026-10-14",
        category="tax",
    ),
    # --- Immigration --------------------------------------------------------
    "uk_skilled_worker_visa": Source(
        id="uk_skilled_worker_visa",
        title="Skilled Worker visa: Overview",
        url="https://www.gov.uk/skilled-worker-visa",
        publisher="GOV.UK (Home Office / UKVI)",
        relevance=(
            "Work route for an eligible job with an approved employer: "
            "certificate of sponsorship, salary rules, duration and settlement."
        ),
        effective="current as at 14 October 2026",
        last_checked="2026-10-14",
        category="immigration",
    ),
    "uk_skilled_worker_job": Source(
        id="uk_skilled_worker_job",
        title="Skilled Worker visa: Your job",
        url="https://www.gov.uk/skilled-worker-visa/your-job",
        publisher="GOV.UK (Home Office / UKVI)",
        relevance=(
            "General salary threshold of GBP 41,700 and the higher going rate "
            "for the occupation code."
        ),
        effective="current as at 14 October 2026",
        last_checked="2026-10-14",
        category="immigration",
    ),
    "uk_skilled_worker_costs": Source(
        id="uk_skilled_worker_costs",
        title="Skilled Worker visa: How much it costs",
        url="https://www.gov.uk/skilled-worker-visa/how-much-it-costs",
        publisher="GOV.UK (Home Office / UKVI)",
        relevance=(
            "Application fee (GBP 819 up to 3 years), immigration health "
            "surcharge and maintenance funds."
        ),
        effective="current as at 14 October 2026",
        last_checked="2026-10-14",
        category="immigration",
    ),
    "uk_skilled_worker_english": Source(
        id="uk_skilled_worker_english",
        title="Skilled Worker visa: Knowledge of English",
        url="https://www.gov.uk/skilled-worker-visa/knowledge-of-english",
        publisher="GOV.UK (Home Office / UKVI)",
        relevance=(
            "English language requirement for the route (B1, rising to B2 for "
            "applications on or after 26 March 2027)."
        ),
        effective="current as at 14 October 2026",
        last_checked="2026-10-14",
        category="immigration",
    ),
    "uk_senior_specialist_worker": Source(
        id="uk_senior_specialist_worker",
        title=(
            "Senior or Specialist Worker visa (Global Business Mobility): "
            "Overview"
        ),
        url="https://www.gov.uk/senior-specialist-worker-visa",
        publisher="GOV.UK (Home Office / UKVI)",
        relevance=(
            "Temporary intra-company transfer route to a UK branch: existing "
            "employee, certificate of sponsorship, minimum salary GBP 52,500, "
            "no route to settlement."
        ),
        effective="current as at 14 October 2026",
        last_checked="2026-10-14",
        category="immigration",
    ),
    "uk_senior_specialist_costs": Source(
        id="uk_senior_specialist_costs",
        title=(
            "Senior or Specialist Worker visa (Global Business Mobility): How "
            "much it costs"
        ),
        url="https://www.gov.uk/senior-specialist-worker-visa/how-much-it-costs",
        publisher="GOV.UK (Home Office / UKVI)",
        relevance=(
            "Application fee (GBP 819 up to 3 years), immigration health "
            "surcharge and maintenance funds for the GBM route."
        ),
        effective="current as at 14 October 2026",
        last_checked="2026-10-14",
        category="immigration",
    ),
    "uk_skilled_occupations": Source(
        id="uk_skilled_occupations",
        title="Immigration Rules Appendix Skilled Occupations",
        url=(
            "https://www.gov.uk/guidance/immigration-rules/"
            "immigration-rules-appendix-skilled-occupations"
        ),
        publisher="GOV.UK (Home Office)",
        relevance=(
            "Eligible SOC 2020 occupation codes and their going rates for the "
            "Skilled Worker and Global Business Mobility routes."
        ),
        effective="updated 8 October 2026",
        last_checked="2026-10-14",
        category="immigration",
    ),
    "uk_skilled_worker_rules": Source(
        id="uk_skilled_worker_rules",
        title="Immigration Rules Appendix Skilled Worker",
        url=(
            "https://www.gov.uk/guidance/immigration-rules/"
            "immigration-rules-appendix-skilled-worker"
        ),
        publisher="GOV.UK (Home Office)",
        relevance=(
            "Detailed eligibility, points and sponsorship rules for the "
            "Skilled Worker route."
        ),
        effective="updated 8 October 2026",
        last_checked="2026-10-14",
        category="immigration",
    ),
    "uk_eta": Source(
        id="uk_eta",
        title="Get an electronic travel authorisation (ETA) to visit the UK",
        url="https://www.gov.uk/eta",
        publisher="GOV.UK (Home Office / UKVI)",
        relevance=(
            "ETA requirement and fee (GBP 20) for visa-free visitors; permits "
            "stays of up to 6 months and does not allow work."
        ),
        effective="current as at 14 October 2026",
        last_checked="2026-10-14",
        category="immigration",
    ),
    "uk_eta_national_list": Source(
        id="uk_eta_national_list",
        title="Immigration Rules Appendix ETA National List",
        url=(
            "https://www.gov.uk/guidance/immigration-rules/"
            "immigration-rules-appendix-eta-national-list"
        ),
        publisher="GOV.UK (Home Office)",
        relevance=(
            "Lists Switzerland as a nationality that requires an ETA for "
            "visa-free travel to the UK (from 2 April 2025)."
        ),
        effective="updated 8 October 2026",
        last_checked="2026-10-14",
        category="immigration",
    ),
    "uk_standard_visitor": Source(
        id="uk_standard_visitor",
        title="Visit the UK as a Standard Visitor: Overview",
        url="https://www.gov.uk/standard-visitor",
        publisher="GOV.UK (Home Office / UKVI)",
        relevance=(
            "Standard Visitor route: permitted activities, fee (GBP 135 for up "
            "to 6 months) and the prohibition on working for a UK company."
        ),
        effective="current as at 14 October 2026",
        last_checked="2026-10-14",
        category="immigration",
    ),
    "uk_visit_business": Source(
        id="uk_visit_business",
        title="Visit the UK on a business trip",
        url="https://www.gov.uk/visit-uk-business-trip",
        publisher="GOV.UK (Home Office / UKVI)",
        relevance=(
            "Business-visit pathway: permitted business activities, visa/ETA "
            "choice and costs."
        ),
        effective="current as at 14 October 2026",
        last_checked="2026-10-14",
        category="immigration",
    ),
    "uk_visitor_permitted_activities": Source(
        id="uk_visitor_permitted_activities",
        title="Immigration Rules Appendix Visitor: Permitted Activities",
        url=(
            "https://www.gov.uk/guidance/immigration-rules/"
            "immigration-rules-appendix-visitor-permitted-activities"
        ),
        publisher="GOV.UK (Home Office)",
        relevance=(
            "The exhaustive list of business activities a visitor may "
            "undertake (and the boundaries of 'work')."
        ),
        effective="updated 8 October 2026",
        last_checked="2026-10-14",
        category="immigration",
    ),
    "uk_sponsor_licence": Source(
        id="uk_sponsor_licence",
        title="UK visa sponsorship for employers: Overview",
        url="https://www.gov.uk/uk-visa-sponsorship-employers",
        publisher="GOV.UK (Home Office / UKVI)",
        relevance=(
            "Sponsor licence requirement for employing Swiss citizens who "
            "arrived in the UK after 31 December 2020."
        ),
        effective="current as at 14 October 2026",
        last_checked="2026-10-14",
        category="immigration",
    ),
    "uk_sponsor_licence_fees": Source(
        id="uk_sponsor_licence_fees",
        title="UK visa sponsorship for employers: Apply for your licence",
        url="https://www.gov.uk/uk-visa-sponsorship-employers/apply-for-your-licence",
        publisher="GOV.UK (Home Office / UKVI)",
        relevance=(
            "Worker sponsor-licence fees (GBP 611 small/charitable, GBP 1,682 "
            "medium/large) and decision timeline (usually under 8 weeks)."
        ),
        effective="current as at 14 October 2026",
        last_checked="2026-10-14",
        category="immigration",
    ),
    "uk_immigration_skills_charge": Source(
        id="uk_immigration_skills_charge",
        title="UK visa sponsorship for employers: Immigration skills charge",
        url=(
            "https://www.gov.uk/uk-visa-sponsorship-employers/"
            "immigration-skills-charge"
        ),
        publisher="GOV.UK (Home Office / UKVI)",
        relevance=(
            "Immigration skills charge payable when assigning a certificate of "
            "sponsorship (GBP 480/240 or GBP 1,320/660 per period) and its "
            "exemptions."
        ),
        effective="current as at 14 October 2026",
        last_checked="2026-10-14",
        category="immigration",
    ),
    "uk_ihs": Source(
        id="uk_ihs",
        title=(
            "Pay for UK healthcare as part of your immigration application: "
            "How much you have to pay"
        ),
        url="https://www.gov.uk/healthcare-immigration-application/how-much-pay",
        publisher="GOV.UK (Home Office / UKVI)",
        relevance=(
            "Immigration health surcharge of GBP 1,035 per year for a work "
            "visa (GBP 2,070 for a 2-year visa)."
        ),
        effective="current as at 14 October 2026",
        last_checked="2026-10-14",
        category="immigration",
    ),
    "uk_border_control": Source(
        id="uk_border_control",
        title="Entering the UK: Before you leave for the UK",
        url="https://www.gov.uk/uk-border-control/before-you-leave-for-the-uk",
        publisher="GOV.UK (Home Office / Border Force)",
        relevance=(
            "Identity and passport requirement: a valid passport is needed and "
            "should be valid for the whole of the stay."
        ),
        effective="current as at 14 October 2026",
        last_checked="2026-10-14",
        category="immigration",
    ),
    "uk_check_visa": Source(
        id="uk_check_visa",
        title="Check if you need a UK visa",
        url="https://www.gov.uk/check-uk-visa",
        publisher="GOV.UK (Home Office / UKVI)",
        relevance=(
            "Interactive checker to confirm the visa or ETA required for a "
            "given nationality and purpose of travel."
        ),
        effective="current as at 14 October 2026",
        last_checked="2026-10-14",
        category="immigration",
    ),
    "uk_right_to_work": Source(
        id="uk_right_to_work",
        title="Checking a job applicant's right to work",
        url="https://www.gov.uk/check-job-applicant-right-to-work",
        publisher="GOV.UK (Home Office)",
        relevance=(
            "Employer duty to check right to work before employment and to "
            "keep records; civil penalty for non-compliance."
        ),
        effective="current as at 14 October 2026",
        last_checked="2026-10-14",
        category="immigration",
    ),
}


def get_source(source_id):
    """Return the :class:`Source` for ``source_id`` (raises ``KeyError``)."""
    return SOURCES[source_id]


def all_sources():
    """Return all sources ordered by category then id."""
    return sorted(SOURCES.values(), key=lambda s: (s.category, s.id))
