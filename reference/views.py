"""Views for the Immigration tab."""
from django.shortcuts import render

from reference import immigration as content
from reference.sources import get_source


def _collect_sources():
    ids = content.all_source_ids()
    numbers = {sid: index + 1 for index, sid in enumerate(ids)}
    records = [get_source(sid) for sid in ids]
    return numbers, records


def immigration(request):
    """Render the Immigration tab (researched requirements + sources)."""
    source_numbers, source_records = _collect_sources()
    return render(
        request,
        "reference/immigration.html",
        {
            "tab": "immigration",
            "routes": content.ROUTES,
            "requirements": content.REQUIREMENTS,
            "costs": content.COSTS,
            "steps": content.STEPS,
            "checklist": content.CHECKLIST,
            "passport_rule": content.PASSPORT_RULE,
            "passport_source_ids": content.PASSPORT_SOURCE_IDS,
            "classification_labels": content.CLASSIFICATION_LABELS,
            "source_numbers": source_numbers,
            "source_records": source_records,
        },
    )
