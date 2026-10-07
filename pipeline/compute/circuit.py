"""Circuit outline and race replay, in one shared 2D frame.

FastF1 positions are in a raw frame. The circuit info gives the rotation that matches the
official track map. Everything is rotated, then scaled into a box WIDTH wide, as integers.
"""

import math

import numpy as np
import pandas as pd

WIDTH = 1000
PAD = 0.04  # margin around the outline: pit lane and run-offs may go slightly outside


class Frame:
    """Rotation + scale fitted on the outline, applied identically to every car."""

    def __init__(self, x: np.ndarray, y: np.ndarray, rotation_deg: float):
        self.angle = math.radians(rotation_deg)
        rx, ry = self._rotate(x, y)
        span = max(rx.max() - rx.min(), ry.max() - ry.min())
        self.scale = WIDTH / (span * (1 + 2 * PAD))  # the padded longest side is WIDTH
        self.x0 = rx.min() - PAD * span
        self.y_max = ry.max() + PAD * span  # SVG y goes down
        self.height = int(round((ry.max() - ry.min() + 2 * PAD * span) * self.scale))
        self.width = int(round((rx.max() - rx.min() + 2 * PAD * span) * self.scale))

    def _rotate(self, x, y):
        c, s = math.cos(self.angle), math.sin(self.angle)
        return x * c - y * s, x * s + y * c

    def apply(self, x, y) -> tuple[np.ndarray, np.ndarray]:
        rx, ry = self._rotate(np.asarray(x, float), np.asarray(y, float))
        return np.rint((rx - self.x0) * self.scale), np.rint((self.y_max - ry) * self.scale)


def compute_circuit(lap_pos: pd.DataFrame, corners: pd.DataFrame, frame: Frame, points: int = 400):
    """Outline from one lap of position data (X, Y), with the numbered corners."""
    x, y = frame.apply(lap_pos["X"], lap_pos["Y"])
    keep = np.linspace(0, len(x) - 1, min(points, len(x))).round().astype(int)
    return {
        "w": frame.width,
        "h": frame.height,
        "path": [[int(x[i]), int(y[i])] for i in keep],
        "corners": [
            {"n": f"{int(c.Number)}{c.Letter or ''}", "x": int(cx), "y": int(cy)}
            for c, cx, cy in zip(
                corners.itertuples(), *frame.apply(corners["X"], corners["Y"]), strict=True
            )
        ],
    }


def compute_replay(
    pos: dict[str, pd.DataFrame],
    end_times: dict[str, float],
    t_from: float,
    t_to: float,
    frame: Frame,
    step: float = 1.0,
) -> dict:
    """Every car every `step` seconds of session time, from t_from to t_to.

    pos: DRV -> position data (SessionTime, X, Y). end_times: DRV -> session time (s) of the
    last lap: the car disappears a few seconds after it (retired, or parked after the flag).
    Output per car: flat [x0, y0, x1, y1, ...], null where the car is not shown.
    """
    grid = np.arange(t_from, t_to, step)
    cars = {}
    for drv, p in pos.items():
        p = p.dropna(subset=["X", "Y", "SessionTime"])
        if p.empty:
            continue
        t = p["SessionTime"].dt.total_seconds().to_numpy()
        x, y = frame.apply(np.interp(grid, t, p["X"]), np.interp(grid, t, p["Y"]))
        hidden = (grid < t[0]) | (grid > t[-1]) | (grid > end_times.get(drv, t_to) + 5)
        flat: list[int | None] = []
        for xi, yi, h in zip(x, y, hidden, strict=True):
            flat += [None, None] if h else [int(xi), int(yi)]
        cars[drv] = flat
    return {"t0": round(t_from, 1), "dt": step, "n": len(grid), "cars": cars}


def sc_periods(track_status: pd.DataFrame) -> list[tuple[float, float]]:
    """(start, end) in session seconds of each safety car period (track status "4")."""
    periods: list[tuple[float, float]] = []
    start = None
    for t, status in zip(
        track_status["Time"].dt.total_seconds(), track_status["Status"].astype(str), strict=True
    ):
        if status == "4" and start is None:
            start = t
        elif status != "4" and start is not None:
            periods.append((start, t))
            start = None
    if start is not None:
        periods.append((start, math.inf))
    return periods


def leaders_at(laps: pd.DataFrame, grid: np.ndarray) -> list[str | None]:
    """Race leader at each time: the last driver to cross the line in P1."""
    p1 = laps[laps["Position"] == 1].dropna(subset=["Time"]).sort_values("Time")
    times = p1["Time"].dt.total_seconds().to_numpy()
    drivers = p1["Driver"].to_list()
    idx = np.searchsorted(times, grid, side="right") - 1
    return [drivers[i] if i >= 0 else None for i in idx]


def safety_car_track(
    path: list[list[int]],
    cars: dict[str, list[int | None]],
    leaders: list[str | None],
    grid: np.ndarray,
    periods: list[tuple[float, float]],
    ahead: float,
) -> list[int | None]:
    """Simulated safety car, `ahead` frame units in front of the leader along the outline.

    F1 does not publish the safety car position: like most replays, it is placed just ahead
    of the leader while the safety car is out. Flat [x0, y0, ...], null outside the periods.
    """
    pts = np.asarray(path, float)
    seg = np.hypot(*np.diff(np.vstack([pts, pts[:1]]), axis=0).T)  # closed loop
    cum = np.concatenate([[0], np.cumsum(seg)])
    total = cum[-1]
    flat: list[int | None] = []
    for i, (t, drv) in enumerate(zip(grid, leaders, strict=True)):
        xy = cars.get(drv or "", [])[2 * i : 2 * i + 2]
        if not any(a <= t < b for a, b in periods) or len(xy) < 2 or xy[0] is None:
            flat += [None, None]
            continue
        k = int(np.argmin(np.hypot(pts[:, 0] - xy[0], pts[:, 1] - xy[1])))
        d = (cum[k] + ahead) % total
        j = int(np.searchsorted(cum, d, side="right") - 1)
        f = (d - cum[j]) / seg[j] if seg[j] else 0.0
        a, b = pts[j], pts[(j + 1) % len(pts)]
        flat += [int(round(a[0] + (b[0] - a[0]) * f)), int(round(a[1] + (b[1] - a[1]) * f))]
    return flat
