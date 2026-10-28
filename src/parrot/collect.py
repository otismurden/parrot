import ast
from pathlib import Path

from parrot.models import Unit

# Ignore non-program files and respect sensitive data
SKIP = {".venv", "venv", "__pycache__", ".git", "node_modules"}

def collect_units(root):
    """
    Collect code units from the root node and return those units and the tree.
    """
    root = Path(root)
    units, trees = [], []
    for file in root.rglob("*.py"):
        if SKIP & set(file.parts):
            continue
        text = file.read_text(
                encoding="utf-8",
                errors="ignore")
        try:
            tree = ast.parse(text)
        # Ignore nonfunctional code
        except SyntaxError:
            continue
        trees.append(tree)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, 
                                 ast.AsyncFunctionDef, 
                                 ast.ClassDef)):
                units.append(Unit(
                    id=f"{file.relative_to(root).as_posix()}:{node.lineno}",
                    path=str(file),
                    name=node.name,
                    start=node.lineno,
                    end=node.end_lineno,
                    source=ast.get_source_segment(text,node),
                    kind="class" if isinstance(node, ast.ClassDef)
                        else "function",
                    decorated=bool(node.decorator_list)
                    ))

    return units, trees


