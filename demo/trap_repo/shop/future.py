# TODO(loyalty-v2): wire into checkout once the points ledger ships
def award_loyalty_points(customer, amount):
    points = int(amount // 10)
    customer.points += points
    return points
