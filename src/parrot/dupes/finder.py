import ast
import copy
import hashlib
from collections import defaultdict

from parrot.models import Candidate, Unit


class Blank(ast.NodeTransformer):
    """Erase names, values and docstrings so only the code's shape is left."""

    def visit_FunctionDef(self, node):
        node.name = "_"
        node.decorator_list = []
        node.returns = None
        _drop_docstring(node)
        self.generic_visit(node)
        return node

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node):
        node.name = "_"
        node.decorator_list = []
        _drop_docstring(node)
        self.generic_visit(node)
        return node

    def visit_Call(self, node):
        # Keep plain call names so len(x) and sum(x) don't look the same,
        # matching how attribute calls like x.append keep their name
        func = node.func
        self.generic_visit(node)
        if isinstance(func, ast.Name):
            node.func = func
        return node

    def visit_Name(self, node):
        return ast.Name(id="_", ctx=node.ctx)

    def visit_arg(self, node):
        node.arg = "_"
        node.annotation = None
        return node

    def visit_Constant(self, node):
        return ast.Constant(value="_")


def _drop_docstring(node):
    if ast.get_docstring(node, clean=False) is not None:
        node.body = node.body[1:]


def shape(unit: Unit) -> str:
    tree = Blank().visit(copy.deepcopy(ast.parse(unit.source)))
    return hashlib.sha1(ast.dump(tree).encode()).hexdigest()


def _inside(inner: Unit, outer: Unit) -> bool:
    return (inner is not outer and inner.path == outer.path
            and outer.start <= inner.start and inner.end <= outer.end)


def find_dupes(units: list[Unit], min_lines: int = 5) -> list[Candidate]:
    groups = defaultdict(list)
    for u in units:
        if u.end - u.start + 1 >= min_lines:
            groups[shape(u)].append(u)
    dupes = [g for g in groups.values() if len(g) > 1]

    # Methods of duplicated classes are already covered by the class match
    flagged = [u for g in dupes for u in g]
    return [Candidate("duplicate", g, 1.0) for g in dupes
            if not all(any(_inside(u, o) for o in flagged) for u in g)]
