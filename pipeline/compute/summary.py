"""Fastest lap of the race, over every lap that was not deleted."""

import pandas as pd


def fastest_lap(laps: pd.DataFrame) -> dict | None:
    valid = laps.dropna(subset=["LapTime"])
    if "Deleted" in valid:
        valid = valid[valid["Deleted"] != True]  # noqa: E712 (object column with None)
    if valid.empty:
        return None
    best = valid.loc[valid["LapTime"].idxmin()]
    return {
        "drv": best["Driver"],
        "lap": int(best["LapNumber"]),
        "t": round(best["LapTime"].total_seconds(), 3),
    }
