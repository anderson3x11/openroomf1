import numpy as np
import pandas as pd

from pipeline.compute.telemetry import STEP, best_laps, compute_telemetry


def _lap(length: float, seconds: float, n: int = 200) -> pd.DataFrame:
    """A lap on a circle, at constant speed, DRS open on the second half."""
    s = np.linspace(0, 1, n)
    return pd.DataFrame(
        {
            "Distance": s * length,
            "Speed": np.full(n, length / seconds * 3.6),
            "Throttle": np.full(n, 104.0),  # FastF1 sometimes goes over 100
            "Brake": s > 0.9,
            "nGear": np.full(n, 7),
            "RPM": np.full(n, 11234.0),
            "DRS": np.where(s > 0.5, 12, 8),
            "Time": pd.to_timedelta(s * seconds, unit="s"),
            "X": np.cos(s * 2 * np.pi) * 1000,
            "Y": np.sin(s * 2 * np.pi) * 1000,
        }
    )


def test_telemetry_on_a_shared_distance_grid():
    tel = {"VER": _lap(5000, 90), "LEC": _lap(5020, 91)}  # a slightly longer racing line
    info = {d: {"lap": 1, "time": 90.0, "cmp": "SOFT"} for d in tel}
    out = compute_telemetry(tel, info, rotation=0)
    n = len(out["x"])
    assert out["step"] == STEP and n == 500 and len(out["y"]) == n
    ver, lec = out["laps"]["VER"], out["laps"]["LEC"]
    assert all(len(ch) == n for ch in (ver["v"], ver["t"], lec["v"], lec["t"]))
    assert ver["v"][0] == 200 and ver["thr"][0] == 100 and ver["rpm"][0] == 11200
    assert ver["drs"][0] == 0 and ver["drs"][-1] == 1 and ver["brk"][-1] == 1
    # LEC's lap is rescaled onto VER's length: halfway is reached at half his lap time.
    assert abs(lec["t"][250] - 45500) < 100 and abs(lec["t"][250] - ver["t"][250]) < 600


def test_best_laps_skip_deleted():
    laps = pd.DataFrame(
        {
            "Driver": ["VER", "VER", "LEC"],
            "LapTime": pd.to_timedelta([90, 89, 91], unit="s"),
            "Deleted": [False, True, None],
        }
    )
    best = best_laps(laps)
    assert best["Driver"].tolist() == ["VER", "LEC"]
    assert best.iloc[0]["LapTime"].total_seconds() == 90
