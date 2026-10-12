"""Best lap telemetry of every driver, resampled by distance, to overlay laps on the site.

Raw telemetry is never stored: each best lap is resampled every STEP metres, as integers.
Distances are rescaled onto the fastest lap's length, so that every lap lines up corner by
corner (laps differ by a few metres: racing lines, GPS noise).
"""

import numpy as np
import pandas as pd

from pipeline.compute.circuit import Frame

STEP = 10  # metres, about 500 points per lap
DRS_OPEN = 10  # FastF1 DRS codes: 10, 12 and 14 mean open


def best_laps(laps: pd.DataFrame) -> pd.DataFrame:
    """Fastest valid lap of each driver (deleted laps do not count), fastest first."""
    valid = laps.dropna(subset=["LapTime"])
    if "Deleted" in valid:
        valid = valid[valid["Deleted"] != True]  # noqa: E712 (object column with None)
    return valid.loc[valid.groupby("Driver")["LapTime"].idxmin()].sort_values("LapTime")


def compute_telemetry(tel: dict[str, pd.DataFrame], info: dict[str, dict], rotation: float) -> dict:
    """tel: DRV -> telemetry of one lap (FastF1 Lap.get_telemetry(): Distance, Speed, Throttle,
    Brake, nGear, RPM, DRS, Time, X, Y), the fastest lap first. info: DRV -> lap number, lap
    time (s) and compound. Output: the track (x, y in a circuit frame) and one entry per driver,
    every channel on the same distance grid."""
    ref = next(iter(tel.values()))
    length = float(ref["Distance"].max())
    grid = np.arange(0, length, STEP)
    frame = Frame(ref["X"].to_numpy(), ref["Y"].to_numpy(), rotation)
    x, y = frame.apply(
        np.interp(grid, ref["Distance"], ref["X"]), np.interp(grid, ref["Distance"], ref["Y"])
    )

    out = {}
    for drv, t in tel.items():
        d = t["Distance"].to_numpy() * length / t["Distance"].max()

        def channel(values, digits=0, d=d):
            return np.round(np.interp(grid, d, np.asarray(values, float)), digits)

        out[drv] = {
            **info[drv],
            "v": channel(t["Speed"]).astype(int).tolist(),
            "thr": channel(t["Throttle"].clip(0, 100)).astype(int).tolist(),
            "brk": channel(t["Brake"].astype(float)).astype(int).tolist(),
            "g": channel(t["nGear"]).astype(int).tolist(),
            "rpm": (channel(t["RPM"], -2)).astype(int).tolist(),
            "drs": channel(t["DRS"] >= DRS_OPEN).astype(int).tolist(),
            # Time since the start of the lap, ms: the delta between two laps comes from it.
            "t": channel(t["Time"].dt.total_seconds() * 1000).astype(int).tolist(),
        }
    return {
        "step": STEP,
        "w": frame.width,
        "h": frame.height,
        "x": x.astype(int).tolist(),
        "y": y.astype(int).tolist(),
        "laps": out,
    }
