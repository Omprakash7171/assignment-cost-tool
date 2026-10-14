"""CSV export for the Cost Estimate tab.

Builds a plain tabular representation of an :class:`AssignmentResult` plus the
numbered official sources it cites. The engine result is passed in untouched, so
the export reuses exactly the same calculation as the on-screen tables (spec
X04/P12). No financial logic lives here.
"""
import csv
import io
from decimal import Decimal

from calculator.models import CLASSIFICATION_LABELS

CSV_HEADER = (
    "Year",
    "Section",
    "Item",
    "Currency",
    "Amount",
    "Classification",
    "Sources",
)


def _amount(value):
    """Render a Decimal as a fixed two-decimal string (no exponent notation)."""
    if value is None:
        return ""
    return "{0:.2f}".format(Decimal(value))


def _citations(source_ids, source_numbers):
    if not source_ids:
        return ""
    return "[{0}]".format(
        ", ".join(str(source_numbers[sid]) for sid in source_ids if sid in source_numbers)
    )


def result_rows(result, source_numbers):
    """Return the annual rows of the export as a list of lists.

    Columns match :data:`CSV_HEADER`. Every row carries the citation numbers of
    the sources that justify it (P12).
    """
    rows = []
    for year in result.years:
        for code, lines in (
            ("A", year.section_a),
            ("B", year.section_b),
            ("C", year.section_c),
            ("D", year.section_d),
        ):
            for line in lines:
                rows.append(
                    [
                        year.year_label,
                        code,
                        line.label,
                        line.currency or "GBP",
                        _amount(line.amount),
                        CLASSIFICATION_LABELS.get(line.classification, ""),
                        _citations(line.source_ids, source_numbers),
                    ]
                )
        rows.append(
            [
                year.year_label,
                "Total",
                "Total employer cost, {0}".format(year.year_label),
                "GBP",
                _amount(year.total_employer_cost_gbp),
                "",
                "",
            ]
        )
    return rows


def summary_rows(result):
    """Whole-assignment summary rows (totals and the cost multiple)."""
    return [
        ["Summary", "", "Total home pay (both years)", "GBP",
         _amount(result.total_home_pay_gbp), "", ""],
        ["Summary", "", "Total employer cost (both years)", "GBP",
         _amount(result.total_employer_cost_gbp), "", ""],
        ["Summary", "", "Cost as a multiple of home pay", "-",
         "{0:.2f}".format(Decimal(result.cost_multiple)), "", ""],
    ]


def source_rows(source_records):
    """Numbered source list with title, URL and metadata (P12)."""
    rows = [["Sources", "", "Title", "Publisher", "URL", "Effective", "Checked"]]
    for index, source in enumerate(source_records, start=1):
        rows.append(
            [
                index,
                source.id,
                source.title,
                source.publisher,
                source.url,
                source.effective,
                source.last_checked,
            ]
        )
    return rows


def build_csv(result, source_numbers, source_records):
    """Return the full CSV document as a string."""
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\r\n")

    writer.writerow(["Assignment cost estimate"])
    writer.writerow([])
    writer.writerow(list(CSV_HEADER))
    writer.writerows(result_rows(result, source_numbers))
    writer.writerows(summary_rows(result))
    writer.writerow([])
    writer.writerows(source_rows(source_records))
    return buffer.getvalue()
