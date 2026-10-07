"""Official overtake counts per driver, from the live timing OvertakeSeries feed."""

# Restarts give a handful of overtakes at once at most. The round 1 2026 archive has events
# counting 21 (the whole field minus one): feed artifacts, dropped.
# Note: fixed threshold, revisit if a real event ever counts more.
MAX_PER_EVENT = 10


def compute_overtakes(feed: dict, results: list[dict]) -> dict[str, int]:
    """DRV -> overtakes made. Each feed entry is one event with the overtakes it counted.

    Some archives repeat every event a few milliseconds apart (round 1 of 2026): events are
    unique by timestamp to the second.
    """
    drv_by_number = {r["num"]: r["drv"] for r in results}
    totals = {r["drv"]: 0 for r in results}
    for number, events in feed.get("Overtakes", {}).items():
        drv = drv_by_number.get(number)
        if drv is None:
            continue
        unique = {e.get("Timestamp", "")[:19]: int(e.get("count", 0)) for e in events}
        totals[drv] = sum(c for c in unique.values() if c <= MAX_PER_EVENT)
    return totals
