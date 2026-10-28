def legacy_discount(price):
    """Pre-2023 discount rule, replaced by apply_discount."""
    return price * 0.9


def old_tax_rate():
    return 0.175


def _walk_tree(node):
    if node is None:
        return 0
    return 1 + _walk_tree(node.left) + _walk_tree(node.right)


def send_email(to, body):
    print("legacy smtp", to, body)
