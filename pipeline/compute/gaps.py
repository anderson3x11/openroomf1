"""Gap to the leader at the end of every lap, in seconds."""

import pandas as pd


def compute_gaps(laps: pd.DataFrame) -> dict:
    valid = laps.dropna(subset=["LapNumber", "Time"])
    n_laps = int(laps["LapNumber"].max())
    # The leader of lap L is whoever completed lap L first.
    leader_time = valid.groupby("LapNumber")["Time"].min()
    by_driver = {}
    for drv, grp in valid.groupby("Driver"):
        series: list[float | None] = [None] * (n_laps + 1)
        for lap, t in zip(grp["LapNumber"], grp["Time"], strict=True):
            series[int(lap)] = round((t - leader_time[lap]).total_seconds(), 3)
        by_driver[drv] = series
    return {"laps": n_laps, "gap": by_driver}
