"""Weather during the race, placed on the race timeline in laps."""

import numpy as np
import pandas as pd


def compute_weather(weather: pd.DataFrame, laps: pd.DataFrame) -> dict:
    """One sample per FastF1 reading (about every minute) between the start and the flag.

    lap: fractional race lap of the leader at that time (2.5 = halfway through lap 3), so the
    front can draw weather on the same lap axis as every other chart.
    """
    lap_ends = laps.dropna(subset=["Time"]).groupby("LapNumber")["Time"].min().dt.total_seconds()
    lap1 = laps[laps["LapNumber"] == 1]
    start = lap1["LapStartTime"].min()
    if pd.isna(start):  # missing for whole races: one lap before the first lap end
        start = lap1["Time"].min() - lap1["LapTime"].median()
    marks = np.concatenate([[start.total_seconds()], lap_ends.to_numpy()])
    t = weather["Time"].dt.total_seconds().to_numpy()
    inside = (t >= marks[0]) & (t <= marks[-1])
    w = weather[inside]
    lap = np.interp(t[inside], marks, np.arange(len(marks)))
    return {
        "lap": [round(float(x), 2) for x in lap],
        "air": w["AirTemp"].round(1).tolist(),
        "track": w["TrackTemp"].round(1).tolist(),
        "humidity": w["Humidity"].round(0).astype(int).tolist(),
        "wind": w["WindSpeed"].round(1).tolist(),
        "rain": [bool(r) for r in w["Rainfall"]],
    }
