"""Every lap time of every driver (heatmap) and the race trace."""

import pandas as pd

from pipeline.compute.track import neutral_kind


def compute_lap_matrix(laps: pd.DataFrame) -> dict:
    """t[DRV][lap] = lap time in seconds, f[DRV][lap] = flag: "p" pit in/out lap,
    "n" neutralized (SC, VSC, red), "" clean. Index 0 is unused (lap numbers start at 1)."""
    n_laps = int(laps["LapNumber"].max())
    times, flags = {}, {}
    for drv, grp in laps.dropna(subset=["LapNumber"]).groupby("Driver"):
        t: list[float | None] = [None] * (n_laps + 1)
        f: list[str] = [""] * (n_laps + 1)
        for row in grp.itertuples():
            lap = int(row.LapNumber)
            if pd.notna(row.LapTime):
                t[lap] = round(row.LapTime.total_seconds(), 3)
            if pd.notna(row.PitInTime) or pd.notna(row.PitOutTime):
                f[lap] = "p"
            elif neutral_kind(row.TrackStatus):
                f[lap] = "n"
        times[drv], flags[drv] = t, f
    return {"laps": n_laps, "t": times, "f": flags}


def compute_race_trace(laps: pd.DataFrame) -> dict:
    """trace[DRV][lap] = seconds ahead (+) or behind (-) a reference car. Lap 0 = start line.

    The reference laps, every lap, in the median lap time of the cars that completed it: rain,
    safety cars and VSC slow it down as much as the field, so the trace only shows relative
    performance. Lap durations come from line crossing times, present even when LapTime is not.
    """
    valid = laps.dropna(subset=["LapNumber", "Time"]).sort_values(["Driver", "LapNumber"])
    n_laps = int(laps["LapNumber"].max())
    start = laps.loc[laps["LapNumber"] == 1, "LapStartTime"].min()
    if pd.isna(start):  # missing for whole races: one lap before the first lap end
        lap1 = laps[laps["LapNumber"] == 1]
        start = lap1["Time"].min() - lap1["LapTime"].median()
    elapsed = (valid["Time"] - start).dt.total_seconds()
    valid = valid.assign(
        lap=valid["LapNumber"].astype(int),
        elapsed=elapsed,
        # Duration of each lap: difference of consecutive crossings (lap 1: from the start).
        duration=elapsed.groupby(valid["Driver"]).diff().fillna(elapsed),
    )
    median = valid.groupby("lap")["duration"].median()
    reference = [0.0] * (n_laps + 1)
    for lap in range(1, n_laps + 1):
        reference[lap] = reference[lap - 1] + float(median.get(lap, median.median()))
    trace = {}
    for drv, grp in valid.groupby("Driver"):
        series: list[float | None] = [None] * (n_laps + 1)
        series[0] = 0.0
        for lap, t in zip(grp["lap"], grp["elapsed"], strict=True):
            series[lap] = round(reference[lap] - t, 3)
        trace[drv] = series
    return {"laps": n_laps, "trace": trace}
