def format_receipt(order):
    lines = [f"Order {order.id}"]
    for item in order.items:
        lines.append(f"{item.name:20} {item.qty:>3} {item.price:>8.2f}")
    lines.append(f"{'TOTAL':20}     {order.total:>8.2f}")
    return "\n".join(lines)
