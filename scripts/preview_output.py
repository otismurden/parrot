"""Render the report with fake findings, so output can be built before the finders and Gemma are ready.

    uv run python scripts/preview_output.py [--json]
"""

import sys

from parrot.models import Candidate, Finding, Unit, Verdict
from parrot.report import show, side_by_side, to_json

INVOICE = Unit(
    id="shop/billing.py::compute_invoice_total", path="shop/billing.py", name="compute_invoice_total",
    start=4, end=11, kind="function",
    source='''def compute_invoice_total(invoice):
    subtotal = 0
    for line in invoice.lines:
        subtotal += line.unit_price * line.quantity
    if invoice.customer.is_exempt:
        return round(subtotal, 2)
    return round(subtotal * 1.2, 2)
''',
)

QUOTE = Unit(
    id="shop/billing.py::compute_quote_total", path="shop/billing.py", name="compute_quote_total",
    start=14, end=21, kind="function",
    source='''def compute_quote_total(quote):
    subtotal = 0
    for item in quote.lines:
        subtotal += item.unit_price * item.quantity
    if quote.customer.is_exempt:
        return round(subtotal, 2)
    return round(subtotal * 1.2, 2)
''',
)

LEGACY = Unit(
    id="shop/utils.py::legacy_discount", path="shop/utils.py", name="legacy_discount",
    start=30, end=33, kind="function",
    source='''def legacy_discount(price):
    return price * 0.9
''',
)

FINDINGS = [
    Finding(
        Candidate("duplicate", [INVOICE, QUOTE], 1.0, "same file shop/billing.py"),
        Verdict(is_issue=True, confidence=0.92, reason="Same pricing rule copied with renamed variables.",
                suggestion="Extract compute_total(doc) and call it from both."),
    ),
    Finding(
        Candidate("dead", [LEGACY], 1.0, "no references found"),
        Verdict(is_issue=True, confidence=0.8, reason="Never called and not exported."),
    ),
    Finding(Candidate("duplicate", [QUOTE, INVOICE], 0.7), None),
]

if __name__ == "__main__":
    if "--json" in sys.argv:
        print(to_json(FINDINGS))
    else:
        show(FINDINGS)
        side_by_side(INVOICE, QUOTE)
