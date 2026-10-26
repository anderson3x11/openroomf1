"""Official overtake counts per driver, from OpenF1 (the F1 feed's overtakes, one per record)."""


def compute_overtakes(overtakes: list[dict], results: list[dict]) -> dict[str, int]:
    """DRV -> overtakes made. A record repeated within the same second counts once: some feeds
    repeat their events a few milliseconds apart."""
    drv_by_number = {r["num"]: r["drv"] for r in results}
    totals = {r["drv"]: 0 for r in results}
    unique = {
        (o["overtaking_driver_number"], o["overtaken_driver_number"], o["date"][:19])
        for o in overtakes
    }
    for number, _, _ in unique:
        drv = drv_by_number.get(str(number))
        if drv is not None:
            totals[drv] += 1
    return totals
