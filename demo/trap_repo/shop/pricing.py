TAX = 0.2


def compute_invoice_total(invoice):
    subtotal = 0
    for line in invoice.lines:
        price = line.unit_price * line.quantity
        if line.discount:
            price -= price * line.discount
        subtotal += price
    if invoice.customer.is_exempt:
        return round(subtotal, 2)
    return round(subtotal * (1 + TAX), 2)


def compute_quote_total(quote):
    running = 0
    for item in quote.lines:
        amount = item.unit_price * item.quantity
        if item.discount:
            amount -= amount * item.discount
        running += amount
    if quote.customer.is_exempt:
        return round(running, 2)
    return round(running * (1 + TAX), 2)


def apply_discount(order, code):
    if not code:
        return order.total
    rate = order.store.codes.get(code, 0)
    discounted = order.total * (1 - rate)
    return max(discounted, 0)


def apply_discount_v2(order, code):
    if not code:
        return order.total
    rate = order.store.codes.get(code, 0)
    if order.customer.is_vip:
        rate += 0.05
    discounted = order.total * (1 - rate)
    return max(discounted, 0)


def late_fee(days):
    if days <= 0:
        return 0
    fee = days * 2.5
    return min(fee, 50)


def loyalty_bonus(points):
    if points <= 0:
        return 0
    bonus = points * 0.01
    return min(bonus, 20)


def public_helper(value):
    return round(value, 2)
