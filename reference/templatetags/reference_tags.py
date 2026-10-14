"""Template filters/tags used by the Cost Estimate and Immigration tabs."""
from django import template

from calculator.rounding import money as _money
from reference.sources import get_source

register = template.Library()


@register.filter
def money(value):
    """Format a Decimal as ``1,234.56`` (empty for None/blank)."""
    if value is None or value == "":
        return ""
    return "{:,.2f}".format(_money(value))


@register.filter
def pounds(value):
    """Format a Decimal as ``£1,234.56`` (empty for None/blank)."""
    if value is None or value == "":
        return ""
    return "\u00a3" + "{:,.2f}".format(_money(value))


@register.filter
def chf(value):
    """Format a Decimal as ``CHF 1,234.56`` (empty for None/blank)."""
    if value is None or value == "":
        return ""
    return "CHF " + "{:,.2f}".format(_money(value))


@register.filter
def cite_numbers(source_ids, mapping):
    """Render source ids as their assigned citation numbers, e.g. ``1, 3``."""
    if not source_ids:
        return ""
    numbers = [str(mapping.get(sid)) for sid in source_ids if mapping.get(sid)]
    return ", ".join(numbers)


@register.simple_tag
def source(source_id):
    """Return the :class:`Source` record for ``source_id``."""
    return get_source(source_id)


@register.filter
def dict_get(mapping, key):
    """Look up ``key`` in ``mapping`` (for per-year dictionaries)."""
    if not mapping:
        return None
    return mapping.get(key)


@register.filter
def classification(value):
    """Human-readable label for a benefit classification constant."""
    from calculator.models import CLASSIFICATION_LABELS

    return CLASSIFICATION_LABELS.get(value, value)
