# Author: David De Araujo Pereira

import ast
import copy
import difflib
import hashlib
from collections import defaultdict

from parrot.models import Candidate, Unit

MIN_LINES = 3


class Blank(ast.NodeTransformer):

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


def _size(u: Unit) -> int:
    return u.end - u.start + 1


def _contains(outer: Unit, inner: Unit) -> bool:
    """True if inner is outer itself or nested inside it."""
    return (outer.path == inner.path
            and outer.start <= inner.start
            and inner.end <= outer.end)


def shape(unit: Unit) -> str:
    tree = Blank().visit(copy.deepcopy(ast.parse(unit.source)))
    return hashlib.sha1(ast.dump(tree).encode()).hexdigest()


def find_dupes(units: list[Unit], min_lines: int = MIN_LINES) -> list[Candidate]:
    groups = defaultdict(list)
    for u in units:
        if _size(u) >= min_lines:
            groups[shape(u)].append(u)
    dupes = [g for g in groups.values() if len(g) > 1]

    # Methods of duplicated classes match too, so only report the class
    def nested(g):
        return all(any(o is not u and _contains(o, u)
                       for other in dupes if other is not g for o in other)
                   for u in g)

    return [Candidate("duplicate", g, 1.0) for g in dupes if not nested(g)]


def clean_lines(source: str) -> list[str]:
    stripped = (ln.strip() for ln in source.splitlines())
    return [ln for ln in stripped if ln and not ln.startswith("#")]


def find_near_dupes(units: list[Unit],
                    threshold: float = 0.85,
                    min_lines: int = MIN_LINES,
                    exact: list[Candidate] | None = None) -> list[Candidate]:
    exact = exact or []

    kept = [u for u in units if _size(u) >= min_lines]
    tidy = [clean_lines(u.source) for u in kept]

    # Exact groups covering each unit, so pairs already reported as exact
    # duplicates (or nested inside them) aren't reported again
    covered = [{n for n, c in enumerate(exact)
                for o in c.units if _contains(o, u)}
               for u in kept]

    results = []
    for i in range(len(kept)):
        for j in range(i + 1, len(kept)):
            a, b = kept[i], kept[j]
            lines_a, lines_b = tidy[i], tidy[j]

            bigger = max(len(lines_a), len(lines_b))
            smaller = min(len(lines_a), len(lines_b))
            if smaller == 0 or bigger > smaller * 1.25:
                continue
            # A class and its only method look alike but aren't duplicates
            if _contains(a, b) or _contains(b, a):
                continue
            if covered[i] & covered[j]:
                continue

            matcher = difflib.SequenceMatcher(None, lines_a, lines_b,
                                              autojunk=False)
            score = matcher.ratio()  # 0.0 to 1.0
            if score >= threshold:
                results.append(Candidate(
                    "near-duplicate", [a, b], round(score, 2),
                    context=f"{score:.0%} of lines match"))

    return results
