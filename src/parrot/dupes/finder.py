from parrot.models import Candidate, Unit
import ast, copy, hashlib
from collections import defaultdict
import difflib

class Blank(ast.NodeTransformer):
    def __init__(self,local):
        self.local = local
        self.ids = {}

    def visit_FunctionDef(self, node):
        node.name = "_"
        node.decorator_list = []
        if (node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant)):
            node.body = node.body[1:]

        self.generic_visit(node)
        return node

    def visit_Name(self, node):
        return ast.Name(id="_", ctx=node.ctx)

    def visit_arg(self, node):
        node.arg = "_"
        node.annotation = None
        return node

    def visit_Constant(self, node):
        return ast.Constant(value = "_")

def shape(unit):
    tree = Blank().visit(copy.deepcopy(ast.parse(unit.source)))
    return hashlib.shal(ast.dump(tree).encode()).hexdigest()

def find_dupes(units, min_lines = 5):
    groups = defaultdict(list)
    for u in units:
        if u.end - u.start + 1 >= min_lines:
            groups[shape(u)].append(u)

    return [Candidate("duplicate", g, 1.0) for g in groups.values() if len(g) > 1]

