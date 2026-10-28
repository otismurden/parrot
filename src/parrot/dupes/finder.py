# Author: David De Araujo Pereira

from parrot.models import Candidate, Unit
import ast, copy, hashlib
from collections import defaultdict
import difflib
from parrot.models import Candidate, Unit

def _drop_docstring(node):
    if ast.get_docstring(node, clean=False) is not None:
        node.body = node.body[1:]

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

def shape(unit: Unit) -> str:
    tree = Blank().visit(copy.deepcopy(ast.parse(unit.source)))
    return hashlib.sha1(ast.dump(tree).encode()).hexdigest()

def find_dupes(units, min_lines = 3):
    groups = defaultdict(list)
    for u in units:
        if u.end - u.start + 1 >= min_lines:
            groups[shape(u)].append(u)

    return [Candidate("duplicate", g, 1.0) for g in groups.values() if len(g) > 1]

def clean_lines(source: str) -> list[str]:
    stripped = (ln.strip() for ln in source.splitlines())
    return [ln for ln in stripped if ln and not ln.startswith("#")]

def find_near_dupes(units: list[Unit], threshold: float = 0.85, min_lines = 3, exact: list[Candidate] = None) -> list[Candidate]:
    if exact is None:
        exact = []

    kept = []
    tidy = []
    for unit in units:
        size = unit.end - unit.start + 1
        if size >= min_lines:
            kept.append(unit)
            tidy.append(clean_lines(unit.source))

    group_of = {}
    group_number = 0
    for candidate in exact:
        for unit in candidate.units:
            group_of[id(unit)] = group_number
        group_number = group_number + 1

    results = []

    for i in range(len(kept)):
        for j in range(i + 1, len(kept)):
            lines_a = tidy[i]
            lines_b = tidy[j]
 
            bigger = max(len(lines_a), len(lines_b))
            smaller = min(len(lines_a), len(lines_b))
 
            if smaller > 0 and bigger <= smaller * 1.25:
 
                same_group = False
                id_a = id(kept[i])
                id_b = id(kept[j])
                if id_a in group_of and id_b in group_of:
                    if group_of[id_a] == group_of[id_b]:
                        same_group = True
                if not same_group:
                    matcher = difflib.SequenceMatcher(None, lines_a, lines_b, autojunk=False)
                    score = matcher.ratio()  # 0.0 to 1.0
 
                    if score >= threshold:
                        pair = [kept[i], kept[j]]
                        results.append(Candidate("near-duplicate", pair, round(score, 2)))
 
    return results
