"""Structured immigration research content (spec F11/F12, R07, X05).

This module holds data only (no Django imports) so it can be unit-tested and
reused by an exporter. Every requirement, cost and step carries the ids of the
official sources that justify it (gate G3/C3); a test asserts that each id
resolves in :mod:`reference.sources`.

The scenario modelled is the supplied case: a Swiss national employed by a
Zurich employer, moving to a UK subsidiary/branch in London for a two-year
assignment beginning 6 April 2026.
"""
from dataclasses import dataclass
from typing import Tuple

# --- Obligation classification (spec F12) -----------------------------------
MANDATORY = "mandatory"
RECOMMENDED = "recommended"
ESTIMATE = "estimate"

CLASSIFICATION_LABELS = {
    MANDATORY: "Mandatory (legal requirement)",
    RECOMMENDED: "Recommended",
    ESTIMATE: "Estimate",
}


@dataclass(frozen=True)
class Route:
    id: str
    name: str
    is_primary: bool
    summary: str
    for_whom: str
    min_salary: str
    duration: str
    settlement: str
    key_requirements: Tuple[str, ...]
    source_ids: Tuple[str, ...] = ()


@dataclass(frozen=True)
class Requirement:
    title: str
    actor: str            # "employee" or "employer"
    classification: str   # MANDATORY / RECOMMENDED / ESTIMATE
    detail: str
    source_ids: Tuple[str, ...] = ()


@dataclass(frozen=True)
class CostItem:
    label: str
    amount: str
    payer: str            # "employee" or "employer"
    basis: str
    classification: str
    source_ids: Tuple[str, ...] = ()


@dataclass(frozen=True)
class Step:
    order: int
    title: str
    actor: str
    timing: str
    description: str
    source_ids: Tuple[str, ...] = ()


@dataclass(frozen=True)
class ChecklistItem:
    task: str
    actor: str
    source_ids: Tuple[str, ...] = ()


ROUTES: Tuple[Route, ...] = (
    Route(
        id="gbm_senior_specialist",
        name="Senior or Specialist Worker (Global Business Mobility)",
        is_primary=True,
        summary=(
            "Temporary posting of an existing senior or specialist employee to "
            "the employer's UK branch or subsidiary. This is the route designed "
            "for an intra-group assignment such as this one."
        ),
        for_whom=(
            "An existing employee of the Zurich employer who is being "
            "temporarily transferred to the linked UK entity in a senior or "
            "specialist role."
        ),
        min_salary=(
            "At least GBP 52,500 per year, or the going rate for the occupation "
            "code if that is higher."
        ),
        duration=(
            "Whichever is shorter of the certificate-of-sponsorship period plus "
            "14 days, or 5 years. Maximum total stay is 5 years in any 6 (or 9 "
            "years in any 10 if paid GBP 73,900 or more)."
        ),
        settlement="No route to permanent settlement (indefinite leave to remain).",
        key_requirements=(
            "The UK entity must hold a valid sponsor licence.",
            "The UK entity assigns a certificate of sponsorship for an eligible occupation.",
            "The role must be skilled and paid at or above the salary threshold.",
            "The employee applies for entry clearance before travelling.",
        ),
        source_ids=(
            "uk_senior_specialist_worker",
            "uk_skilled_occupations",
            "uk_sponsor_licence",
        ),
    ),
    Route(
        id="skilled_worker",
        name="Skilled Worker visa",
        is_primary=False,
        summary=(
            "Standard UK work visa for an eligible job with an approved "
            "employer. Appropriate if the employee will be employed by the UK "
            "entity rather than remaining on a temporary intra-group posting."
        ),
        for_whom=(
            "A worker taking up an eligible job with a UK employer that holds a "
            "sponsor licence."
        ),
        min_salary=(
            "At least GBP 41,700 per year, or the going rate for the occupation "
            "code if that is higher (lower thresholds apply to new entrants and "
            "Immigration Salary List roles)."
        ),
        duration="Up to 5 years before extension.",
        settlement=(
            "May lead to settlement after 5 years' continuous permission."
        ),
        key_requirements=(
            "The UK employer must hold a valid sponsor licence.",
            "A certificate of sponsorship for an eligible occupation code.",
            "Salary at or above the general threshold and the going rate.",
            "English language at B1 (B2 for applications on or after 26 March 2027).",
        ),
        source_ids=(
            "uk_skilled_worker_visa",
            "uk_skilled_worker_job",
            "uk_skilled_worker_english",
            "uk_skilled_worker_rules",
            "uk_skilled_occupations",
        ),
    ),
    Route(
        id="standard_visitor_business",
        name="Standard Visitor (business activities only)",
        is_primary=False,
        summary=(
            "For short business trips (meetings, conferences, negotiations) only. "
            "It does not authorise the two-year assignment and cannot be used to "
            "work for a UK company."
        ),
        for_whom=(
            "A visitor attending permitted business activities, not taking up "
            "employment in the UK."
        ),
        min_salary="Not applicable.",
        duration="Up to 6 months per visit; visitor visa fee GBP 135.",
        settlement="No route to settlement.",
        key_requirements=(
            "May only carry out the permitted business activities.",
            "Swiss nationals are visa-free but require an ETA (GBP 20) for visits.",
            "Must not take employment or provide services to a UK company.",
        ),
        source_ids=(
            "uk_standard_visitor",
            "uk_visit_business",
            "uk_visitor_permitted_activities",
            "uk_eta",
            "uk_eta_national_list",
        ),
    ),
)


REQUIREMENTS: Tuple[Requirement, ...] = (
    Requirement(
        title="UK entity must hold a sponsor licence",
        actor="employer",
        classification=MANDATORY,
        detail=(
            "A sponsor licence is required to employ a Swiss citizen who "
            "arrived in the UK to work after 31 December 2020. The licence fee "
            "is paid by the employer and cannot be passed to the worker."
        ),
        source_ids=("uk_sponsor_licence", "uk_sponsor_licence_fees"),
    ),
    Requirement(
        title="Certificate of sponsorship for an eligible occupation",
        actor="employer",
        classification=MANDATORY,
        detail=(
            "The UK entity assigns a certificate of sponsorship and must pay "
            "the immigration skills charge (unless an exemption applies) when "
            "the certificate is assigned."
        ),
        source_ids=(
            "uk_sponsor_licence",
            "uk_immigration_skills_charge",
            "uk_skilled_worker_rules",
        ),
    ),
    Requirement(
        title="Salary must meet the threshold and going rate",
        actor="employer",
        classification=MANDATORY,
        detail=(
            "The salary must meet the higher of the route's general threshold "
            "and the going rate for the occupation code (GBP 52,500 for the "
            "GBM Senior/Specialist route; GBP 41,700 for the Skilled Worker "
            "route)."
        ),
        source_ids=(
            "uk_senior_specialist_worker",
            "uk_skilled_worker_job",
            "uk_skilled_occupations",
        ),
    ),
    Requirement(
        title="Employee must obtain entry clearance before travelling",
        actor="employee",
        classification=MANDATORY,
        detail=(
            "A work visa must be granted before arrival; the employee applies "
            "online up to 3 months before the start date on the certificate of "
            "sponsorship."
        ),
        source_ids=("uk_skilled_worker_visa", "uk_senior_specialist_worker"),
    ),
    Requirement(
        title="Valid passport for the whole stay",
        actor="employee",
        classification=MANDATORY,
        detail=(
            "A valid passport is required to enter the UK and it should be "
            "valid for the whole of the stay."
        ),
        source_ids=("uk_border_control",),
    ),
    Requirement(
        title="Pay the immigration health surcharge",
        actor="employee",
        classification=MANDATORY,
        detail=(
            "The surcharge is GBP 1,035 per year for a work visa (GBP 2,070 for "
            "a two-year visa) and is paid as part of the online application."
        ),
        source_ids=("uk_ihs", "uk_skilled_worker_costs"),
    ),
    Requirement(
        title="Employer right-to-work check",
        actor="employer",
        classification=MANDATORY,
        detail=(
            "The employer must check the right to work before employment "
            "starts and keep records; a civil penalty applies to non-compliance."
        ),
        source_ids=("uk_right_to_work",),
    ),
    Requirement(
        title="English language evidence (Skilled Worker only)",
        actor="employee",
        classification=MANDATORY,
        detail=(
            "The Skilled Worker route requires English at B1, rising to B2 for "
            "applications on or after 26 March 2027. Confirm the requirement "
            "for the route actually used."
        ),
        source_ids=("uk_skilled_worker_english",),
    ),
    Requirement(
        title="Apply well ahead of the start date",
        actor="employee",
        classification=RECOMMENDED,
        detail=(
            "Apply as soon as the certificate of sponsorship is available "
            "(up to 3 months before the start date) and allow for visa "
            "decision times and any appointment."
        ),
        source_ids=("uk_skilled_worker_visa", "uk_senior_specialist_worker"),
    ),
    Requirement(
        title="Confirm the correct route with an adviser",
        actor="employer",
        classification=RECOMMENDED,
        detail=(
            "The right route depends on the employment structure (UK "
            "employment vs a temporary intra-group posting) and cannot be "
            "determined by this tool alone."
        ),
        source_ids=("uk_check_visa", "uk_senior_specialist_worker"),
    ),
    Requirement(
        title="Processing times",
        actor="employee",
        classification=ESTIMATE,
        detail=(
            "A visa applied for from outside the UK is usually decided within "
            "3 weeks (8 weeks if applied for inside the UK). A new sponsor "
            "licence is usually decided within 8 weeks."
        ),
        source_ids=(
            "uk_skilled_worker_visa",
            "uk_senior_specialist_worker",
            "uk_sponsor_licence_fees",
        ),
    ),
)


COSTS: Tuple[CostItem, ...] = (
    CostItem(
        label="Sponsor licence (Worker)",
        amount="GBP 611 (small/charitable) or GBP 1,682 (medium/large)",
        payer="employer",
        basis="One-off, per licence (covers multiple sponsored workers).",
        classification=MANDATORY,
        source_ids=("uk_sponsor_licence_fees",),
    ),
    CostItem(
        label="Immigration skills charge",
        amount=(
            "GBP 960 (small/charitable) or GBP 2,640 (medium/large) for a "
            "2-year certificate of sponsorship"
        ),
        payer="employer",
        basis=(
            "Per sponsored worker. First 12 months plus each additional 6 "
            "months (GBP 480 + 2x GBP 240, or GBP 1,320 + 2x GBP 660); certain "
            "occupation codes are exempt."
        ),
        classification=MANDATORY,
        source_ids=("uk_immigration_skills_charge",),
    ),
    CostItem(
        label="Visa application fee",
        amount="GBP 819 (applying from outside the UK, stay up to 3 years)",
        payer="employee",
        basis="Per person; GBP 628 if the job is on the Immigration Salary List.",
        classification=MANDATORY,
        source_ids=("uk_skilled_worker_costs", "uk_senior_specialist_costs"),
    ),
    CostItem(
        label="Immigration health surcharge",
        amount="GBP 2,070 (GBP 1,035 per year for 2 years)",
        payer="employee",
        basis="Per person; dependants pay the same.",
        classification=MANDATORY,
        source_ids=("uk_ihs",),
    ),
    CostItem(
        label="Maintenance funds (evidence, not a fee)",
        amount="GBP 1,270 held for 28 consecutive days",
        payer="employee",
        basis=(
            "Unless the employer certifies maintenance on the certificate of "
            "sponsorship."
        ),
        classification=MANDATORY,
        source_ids=("uk_skilled_worker_costs", "uk_senior_specialist_costs"),
    ),
    CostItem(
        label="Employee-side visa cost subtotal (2 years, single applicant)",
        amount="GBP 2,889 (GBP 819 fee + GBP 2,070 surcharge)",
        payer="employee",
        basis="Excludes dependants, priority services and travel.",
        classification=ESTIMATE,
        source_ids=("uk_skilled_worker_costs", "uk_ihs"),
    ),
    CostItem(
        label="Electronic travel authorisation (ETA)",
        amount="GBP 20",
        payer="employee",
        basis=(
            "Only for short business or personal visits; not required once the "
            "work visa is granted."
        ),
        classification=RECOMMENDED,
        source_ids=("uk_eta", "uk_visit_business"),
    ),
    CostItem(
        label="Standard Visitor visa (if a visa rather than an ETA is used)",
        amount="GBP 135 for up to 6 months",
        payer="employee",
        basis="Alternative to the ETA for visitors who need a visa.",
        classification=RECOMMENDED,
        source_ids=("uk_standard_visitor",),
    ),
)


STEPS: Tuple[Step, ...] = (
    Step(
        order=1,
        title="Confirm the immigration route",
        actor="employer",
        timing="As early as possible",
        description=(
            "Decide whether the assignment is a temporary intra-group posting "
            "(GBM Senior/Specialist Worker) or UK employment (Skilled Worker), "
            "with a qualified adviser."
        ),
        source_ids=("uk_check_visa", "uk_senior_specialist_worker"),
    ),
    Step(
        order=2,
        title="Obtain or confirm the sponsor licence",
        actor="employer",
        timing="Before assigning a certificate of sponsorship",
        description=(
            "The UK entity applies for a Worker sponsor licence if it does not "
            "already hold one. Most applications are decided within 8 weeks; a "
            "priority service (extra GBP 750) targets 10 working days."
        ),
        source_ids=("uk_sponsor_licence", "uk_sponsor_licence_fees"),
    ),
    Step(
        order=3,
        title="Assign a certificate of sponsorship and pay the charge",
        actor="employer",
        timing="Once the licence is in place",
        description=(
            "Assign a certificate of sponsorship for the eligible occupation "
            "and pay the immigration skills charge when assigning it."
        ),
        source_ids=(
            "uk_sponsor_licence",
            "uk_immigration_skills_charge",
            "uk_skilled_occupations",
        ),
    ),
    Step(
        order=4,
        title="Apply for the visa online",
        actor="employee",
        timing="Up to 3 months before the start date",
        description=(
            "Apply online, pay the application fee and the immigration health "
            "surcharge, and prove identity and provide documents."
        ),
        source_ids=("uk_skilled_worker_visa", "uk_skilled_worker_costs"),
    ),
    Step(
        order=5,
        title="Await the decision",
        actor="employee",
        timing="Usually 3 weeks from outside the UK",
        description=(
            "A decision is usually made within 3 weeks for applications from "
            "outside the UK (8 weeks from inside the UK)."
        ),
        source_ids=("uk_skilled_worker_visa", "uk_senior_specialist_worker"),
    ),
    Step(
        order=6,
        title="Travel to the UK",
        actor="employee",
        timing="Before the start date",
        description=(
            "Travel with a valid passport (valid for the whole stay) and the "
            "granted visa/eVisa."
        ),
        source_ids=("uk_border_control",),
    ),
    Step(
        order=7,
        title="Right-to-work check",
        actor="employer",
        timing="Before employment starts",
        description=(
            "Check the employee's right to work online (share code) or from "
            "original documents, and keep records."
        ),
        source_ids=("uk_right_to_work",),
    ),
)


CHECKLIST: Tuple[ChecklistItem, ...] = (
    ChecklistItem(
        task="Confirm the route (GBM Senior/Specialist vs Skilled Worker) with an adviser.",
        actor="employer",
        source_ids=("uk_check_visa", "uk_senior_specialist_worker"),
    ),
    ChecklistItem(
        task="Hold a valid Worker sponsor licence (apply if not already licensed).",
        actor="employer",
        source_ids=("uk_sponsor_licence", "uk_sponsor_licence_fees"),
    ),
    ChecklistItem(
        task="Confirm the SOC code and that salary meets the higher of the threshold and going rate.",
        actor="employer",
        source_ids=("uk_skilled_worker_job", "uk_skilled_occupations"),
    ),
    ChecklistItem(
        task="Assign the certificate of sponsorship and pay the immigration skills charge.",
        actor="employer",
        source_ids=("uk_immigration_skills_charge",),
    ),
    ChecklistItem(
        task="Ensure the employee holds a valid passport covering the whole stay.",
        actor="employee",
        source_ids=("uk_border_control",),
    ),
    ChecklistItem(
        task="Apply for the visa up to 3 months before the start date and allow 3 weeks for a decision.",
        actor="employee",
        source_ids=("uk_skilled_worker_visa", "uk_senior_specialist_worker"),
    ),
    ChecklistItem(
        task="Budget GBP 819 visa fee plus GBP 2,070 health surcharge for two years.",
        actor="employee",
        source_ids=("uk_skilled_worker_costs", "uk_ihs"),
    ),
    ChecklistItem(
        task="Hold GBP 1,270 for 28 consecutive days unless the employer certifies maintenance.",
        actor="employee",
        source_ids=("uk_skilled_worker_costs",),
    ),
    ChecklistItem(
        task="Complete a right-to-work check before the first day and keep records.",
        actor="employer",
        source_ids=("uk_right_to_work",),
    ),
)

PASSPORT_RULE = (
    "A valid passport is required to enter the UK and it should be valid for "
    "the whole of the stay."
)
PASSPORT_SOURCE_IDS: Tuple[str, ...] = ("uk_border_control",)


def all_source_ids():
    """Return every source id referenced by the immigration content."""
    ids = []

    def add(candidates):
        for sid in candidates:
            if sid not in ids:
                ids.append(sid)

    for route in ROUTES:
        add(route.source_ids)
    for requirement in REQUIREMENTS:
        add(requirement.source_ids)
    for cost in COSTS:
        add(cost.source_ids)
    for step in STEPS:
        add(step.source_ids)
    for item in CHECKLIST:
        add(item.source_ids)
    add(PASSPORT_SOURCE_IDS)
    return ids
