"""Top speed through the speed trap, best sectors and ideal lap per driver."""

import pandas as pd


def compute_speeds(laps: pd.DataFrame) -> dict[str, dict]:
    """ideal: sum of the driver's three best sectors, across the race. best: best lap time.
    Deleted laps (track limits) do not count."""
    valid = laps[laps["Deleted"] != True] if "Deleted" in laps else laps  # noqa: E712
    out = {}
    for drv, grp in valid.groupby("Driver"):
        sectors = [grp[f"Sector{i}Time"].min() for i in (1, 2, 3)]
        best = grp["LapTime"].min()
        top = grp["SpeedST"].max()
        out[drv] = {
            "top": None if pd.isna(top) else int(top),
            "s": [None if pd.isna(s) else round(s.total_seconds(), 3) for s in sectors],
            "ideal": None
            if any(pd.isna(s) for s in sectors)
            else round(sum(s.total_seconds() for s in sectors), 3),
            "best": None if pd.isna(best) else round(best.total_seconds(), 3),
        }
    return out
