def basket_total(items):
    total = 0
    for item in items:
        total = total + item.price * item.qty
    return total


def cart_value(products):
    values = [p.price * p.qty for p in products]
    result = sum(values)
    return result
