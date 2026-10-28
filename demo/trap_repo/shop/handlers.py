EXPORTERS = {}


def register(fmt):
    def wrap(fn):
        EXPORTERS[fmt] = fn
        return fn
    return wrap


@register("csv")
def export_csv(rows):
    return "\n".join(",".join(map(str, r)) for r in rows)


def handle_refund(event):
    return {"refunded": event["amount"]}


def handle_chargeback(event):
    return {"disputed": event["amount"]}


def dispatch(event):
    handler = globals()[f"handle_{event['type']}"]
    return handler(event)
