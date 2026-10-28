from parrot.models import Finding


def show(findings: list[Finding]) -> None:
    for f in findings:
        print(f)
