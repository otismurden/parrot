def sync_inventory(store):
    items = store.fetch_items()
    for item in items:
        item.stock = store.count(item.sku)
    store.save(items)
    return len(items)


async def sync_inventory_async(store):
    items = store.fetch_items()
    for item in items:
        item.stock = store.count(item.sku)
    store.save(items)
    return len(items)
