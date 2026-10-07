"""Position of each driver at the end of every lap. Lap 0 is the starting grid."""

import pandas as pd


def compute_positions(laps: pd.DataFrame, results: pd.DataFrame) -> dict:
    n_laps = int(laps["LapNumber"].max())
    grid = results.set_index("Abbreviation")["GridPosition"]
    by_driver = {}
    for drv, grp in laps.groupby("Driver"):
        series = [None] * (n_laps + 1)
        g = grid.get(drv)
        series[0] = int(g) if pd.notna(g) and g > 0 else None
        for lap, pos in zip(grp["LapNumber"], grp["Position"], strict=True):
            if pd.notna(lap) and pd.notna(pos):
                series[int(lap)] = int(pos)
        by_driver[drv] = series
    return {"laps": n_laps, "pos": by_driver}
