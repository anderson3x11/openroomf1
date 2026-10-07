"""Representative lap times per driver: no lap 1, no pit in/out laps, no neutralized laps."""

import pandas as pd

from pipeline.compute.track import neutral_kind


def compute_laptimes(laps: pd.DataFrame) -> dict[str, list[list[float]]]:
    """DRV -> [[lap, seconds], ...]. Keeping the lap number lets the front filter by lap range."""
    clean = laps.dropna(subset=["LapNumber", "LapTime"])
    clean = clean[
        (clean["LapNumber"] > 1)
        & clean["PitInTime"].isna()
        & clean["PitOutTime"].isna()
        & clean["TrackStatus"].map(neutral_kind).isna()
    ]
    return {
        drv: [
            [int(lap), round(t.total_seconds(), 3)]
            for lap, t in zip(g["LapNumber"], g["LapTime"], strict=True)
        ]
        for drv, g in clean.groupby("Driver")
    }
