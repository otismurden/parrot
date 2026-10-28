def print_slip(o):
	out = [f"Order {o.id}"]
	for row in o.items:
		out.append(f"{row.name:20} {row.qty:>3} {row.price:>8.2f}")
	out.append(f"{'TOTAL':20}     {o.total:>8.2f}")
	return "\n".join(out)
