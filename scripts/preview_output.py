"""Render the report with fake findings, so output can be built before the
finders and Gemma are ready.

    uv run python scripts/preview_output.py [--json]
"""

import sys

from parrot.models import Candidate, Finding, Unit, Verdict
from parrot.report import show, to_json

INVOICE = Unit(
    id="shop/billing.py:4", path="shop/billing.py",
    name="compute_invoice_total",
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
    id="shop/billing.py:14", path="shop/billing.py",
    name="compute_quote_total",
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
    id="shop/utils.py:30", path="shop/utils.py",
    name="legacy_discount",
    start=30, end=33, kind="function",
    source='''def legacy_discount(price):
    return price * 0.9
''',
)

EXPORT_ORDERS = Unit(
    id="shop/reports.py:4", path="shop/reports.py",
    name="export_orders",
    start=4, end=9, kind="function",
    source='''def export_orders(orders, path):
    with open(path, "w") as fh:
        for o in orders:
            fh.write(f"{o.id},{o.total}\\n")
''',
)

EXPORT_CUSTOMERS = Unit(
    id="shop/reports.py:12", path="shop/reports.py",
    name="export_customers",
    start=12, end=17, kind="function",
    source='''def export_customers(customers, path):
    with open(path, "w") as fh:
        for c in customers:
            fh.write(f"{c.id},{c.email}\\n")
''',
)

LOYALTY = Unit(
    id="shop/loyalty.py:8", path="shop/loyalty.py",
    name="award_points",
    start=8, end=10, kind="function",
    source='''def award_points(customer, amount):
    customer.points += int(amount // 10)
''',
)

OLD_TAX = Unit(
    id="shop/utils.py:40", path="shop/utils.py",
    name="old_tax_rate",
    start=40, end=41, kind="function",
    source='''def old_tax_rate():
    return 0.175
''',
)

# one finding per label, so every colour and word can be checked
FINDINGS = [
    Finding(
        Candidate("duplicate", [INVOICE, QUOTE], 1.0,
                  "same file shop/billing.py"),
        Verdict(is_issue=True, confidence=0.92,
                reason="Same pricing rule copied with renamed variables.",
                suggestion="Extract compute_total(doc) and call it from "
                           "both."),
    ),
    Finding(
        Candidate("duplicate", [EXPORT_ORDERS, EXPORT_CUSTOMERS], 0.7,
                  "same file shop/reports.py"),
        Verdict(is_issue=True, confidence=0.6,
                reason="Same CSV scaffold; only the columns differ."),
    ),
    Finding(
        Candidate("duplicate", [QUOTE, EXPORT_CUSTOMERS], 0.62),
        Verdict(is_issue=False, confidence=0.85,
                reason="Similar shape, unrelated jobs."),
    ),
    Finding(Candidate("duplicate", [EXPORT_ORDERS, INVOICE], 0.61), None),
    Finding(
        Candidate("dead", [LEGACY], 1.0, "no references found"),
        Verdict(is_issue=True, confidence=0.9,
                reason="Never called and not exported."),
    ),
    Finding(
        Candidate("dead", [OLD_TAX], 1.0, "no references found"),
        Verdict(is_issue=True, confidence=0.55,
                reason="Unreferenced, but may be read by a config "
                       "loader."),
    ),
    Finding(
        Candidate("dead", [LOYALTY], 1.0, "no references found"),
        Verdict(is_issue=False, confidence=0.75,
                reason="Unused today; fits the planned loyalty "
                       "feature."),
    ),
]

if __name__ == "__main__":
    if "--json" in sys.argv:
        print(to_json(FINDINGS))
    else:
        show(FINDINGS)
