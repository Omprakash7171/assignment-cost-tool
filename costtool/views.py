"""Views for the Cost Estimate tab.

The views validate input, call the pure engine and render the result. No
financial logic is implemented here (spec E01).
"""
from django.http import HttpResponse
from django.shortcuts import render

from calculator import CalculatorError, run_assignment
from reference.sources import get_source

from .exporters import build_csv
from .forms import (
    AssignmentForm,
    alternative_case_initial,
    supplied_case_initial,
)


def _collect_sources(result):
    """Return referenced source ids in first-use order plus their records."""
    ids = []
    for year in result.years:
        for section in (
            year.section_a,
            year.section_b,
            year.section_c,
            year.section_d,
        ):
            for line in section:
                for sid in line.source_ids:
                    if sid not in ids:
                        ids.append(sid)
    numbers = {sid: index + 1 for index, sid in enumerate(ids)}
    records = [get_source(sid) for sid in ids]
    return numbers, records


def cost_estimate(request):
    """Render the Cost Estimate tab (form plus, on success, the results)."""
    result = None
    error = None
    source_numbers = {}
    source_records = []

    if request.method == "POST":
        form = AssignmentForm(request.POST)
        if form.is_valid():
            try:
                result = run_assignment(form.to_inputs())
            except CalculatorError as exc:
                error = str(exc)
        # else: fall through and re-render bound form with field errors
    else:
        form = AssignmentForm(initial=supplied_case_initial())

    if result is not None:
        source_numbers, source_records = _collect_sources(result)

    return render(
        request,
        "costtool/cost_estimate.html",
        {
            "tab": "cost",
            "form": form,
            "result": result,
            "error": error,
            "source_numbers": source_numbers,
            "source_records": source_records,
        },
    )


def _initial_as_post_data():
    """Turn the supplied-case initial values into bound-form data."""
    data = {}
    for key, value in supplied_case_initial().items():
        if isinstance(value, bool):
            data[key] = "on" if value else ""
        elif hasattr(value, "isoformat"):
            data[key] = value.isoformat()
        else:
            data[key] = str(value)
    return data


def csv_export(request):
    """Download the current estimate as CSV (spec X04/P12).

    Accepts the same form fields as the Cost Estimate tab. A POST (from the
    results page) exports the submitted scenario; a GET exports the supplied
    test case. Returns a ``text/csv`` attachment, or re-renders the estimate page
    with readable errors if the input is invalid.
    """
    error = None
    result = None

    if request.method == "POST":
        form = AssignmentForm(request.POST)
    else:
        form = AssignmentForm(_initial_as_post_data())

    if form.is_valid():
        try:
            result = run_assignment(form.to_inputs())
        except CalculatorError as exc:
            error = str(exc)

    if result is not None:
        source_numbers, source_records = _collect_sources(result)
        body = build_csv(result, source_numbers, source_records)
        response = HttpResponse(body, content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = (
            'attachment; filename="assignment-cost-estimate.csv"'
        )
        return response

    return render(
        request,
        "costtool/cost_estimate.html",
        {
            "tab": "cost",
            "form": form,
            "result": None,
            "error": error,
            "source_numbers": {},
            "source_records": [],
        },
    )


def _comparison_rows(base_result, alt_result):
    """Build the side-by-side comparison rows (base vs alternative)."""

    def row(label, base, alt, money=True):
        return {
            "label": label,
            "base": base,
            "alt": alt,
            "delta": alt - base,
            "money": money,
        }

    base_years = {y.year: y.total_employer_cost_gbp for y in base_result.years}
    alt_years = {y.year: y.total_employer_cost_gbp for y in alt_result.years}

    rows = [
        row(
            "Total home pay (both years)",
            base_result.total_home_pay_gbp,
            alt_result.total_home_pay_gbp,
        )
    ]
    for year in sorted(set(base_years) | set(alt_years)):
        rows.append(
            row(
                "Employer cost, year {0}".format(year),
                base_years.get(year),
                alt_years.get(year),
            )
        )
    rows.append(
        row(
            "Total employer cost",
            base_result.total_employer_cost_gbp,
            alt_result.total_employer_cost_gbp,
        )
    )
    rows.append(
        row(
            "Cost as a multiple of home pay",
            base_result.cost_multiple,
            alt_result.cost_multiple,
            money=False,
        )
    )
    return rows


def _changed_fields(base_form, alt_form):
    """Labels of the input fields whose values differ between the two forms."""
    changed = []
    for name, field in base_form.fields.items():
        if base_form.cleaned_data.get(name) != alt_form.cleaned_data.get(name):
            changed.append(field.label)
    return changed


def scenario_compare(request):
    """Compare two scenarios side by side, reusing the same engine (X02/P11)."""
    comparison = None
    error = None

    if request.method == "POST":
        base_form = AssignmentForm(request.POST, prefix="base")
        alt_form = AssignmentForm(request.POST, prefix="alt")
        valid = base_form.is_valid() & alt_form.is_valid()
        if valid:
            try:
                base_result = run_assignment(base_form.to_inputs())
                alt_result = run_assignment(alt_form.to_inputs())
                comparison = {
                    "rows": _comparison_rows(base_result, alt_result),
                    "changed": _changed_fields(base_form, alt_form),
                }
            except CalculatorError as exc:
                error = str(exc)
    else:
        base_form = AssignmentForm(initial=supplied_case_initial(), prefix="base")
        alt_form = AssignmentForm(initial=alternative_case_initial(), prefix="alt")

    return render(
        request,
        "costtool/scenario_compare.html",
        {
            "tab": "compare",
            "base_form": base_form,
            "alt_form": alt_form,
            "comparison": comparison,
            "error": error,
        },
    )
