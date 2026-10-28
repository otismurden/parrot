import ast

from parrot.models import Candidate, Unit


def find_dead(units: list[Unit], trees: list[ast.Module]) -> list[Candidate]:
    used = set()
    for tree in trees:
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used.add(node.id)
            elif isinstance(node, ast.Attribute):
                used.add(node.attr)
            elif (isinstance(node, ast.Constant)
                  and isinstance(node.value, str)):
                used.add(node.value)

    dead = []
    for u in units:
        if u.name not in used and not skip(u):
            dead.append(Candidate("dead", [u], 1.0))
    return dead


def skip(u: Unit) -> bool:
    is_magic = u.name.startswith("__") and u.name.endswith("__")
    is_test = u.name.startswith("test_")
    is_visitor = u.name.startswith("visit_")  # called by ast.NodeVisitor
    return is_magic or is_test or is_visitor or u.decorated
