import ast

from parrot.models import Candidate, Unit


def find_dead(units: list[Unit], trees: list[ast.Module]) -> list[Candidate]:
    return []
