"""Qualifying and sprint qualifying: classification by segment and the lap timeline.

FastF1 gives no classification for sprint qualifying (Position and Q1-Q3 empty), so both are
built from the laps, split into segments with Laps.split_qualifying_sessions().
"""

import pandas as pd

from pipeline.compute.results import identity

# Laps slower than this ratio of the segment's best are cool-down or aborted laps.
PUSH_RATIO = 1.1


def _push(part: pd.DataFrame | None) -> pd.DataFrame:
    """Flying laps: timed, not out or in laps, within PUSH_RATIO of the segment's best valid
    lap. Deleted laps (track limits) are kept here, flagged in column Deleted."""
    if part is None or part.empty:
        return pd.DataFrame(
            {"Driver": [], "LapTime": pd.to_timedelta([]), "Deleted": pd.Series(dtype=bool)}
        )
    timed = part.dropna(subset=["LapTime"])
    timed = timed[timed["PitInTime"].isna() & timed["PitOutTime"].isna()]
    deleted = timed["Deleted"] == True  # noqa: E712 (object column with None)
    # ponytail: fixed ratio, a wet-to-dry session may hide its early laps; per driver if so.
    return timed[timed["LapTime"] <= timed.loc[~deleted, "LapTime"].min() * PUSH_RATIO].assign(
        Deleted=deleted
    )


def compute_quali(parts: list[pd.DataFrame | None], results: pd.DataFrame) -> list[dict]:
    """One row per driver: best time in each segment reached, in classification order.
    Official positions when the source has them, else furthest segment reached, then time in
    it. Drivers without an official position (retired, "RT") come after the classified ones."""
    pushes = [_push(p) for p in parts]
    best = [p[~p["Deleted"]].groupby("Driver")["LapTime"].min().dt.total_seconds() for p in pushes]
    rows = []
    for r in results.itertuples():
        q = [round(b[r.Abbreviation], 3) if r.Abbreviation in b else None for b in best]
        pos = pd.to_numeric(r.Position, errors="coerce")
        rows.append({**identity(r), "pos": None if pd.isna(pos) else int(pos), "q": q})

    def furthest(row):  # later segment first, then faster in it, no time last
        times = [(i, t) for i, t in enumerate(row["q"]) if t is not None]
        return (-times[-1][0], times[-1][1]) if times else (1, 0)

    official = sorted((r for r in rows if r["pos"] is not None), key=lambda r: r["pos"])
    others = sorted((r for r in rows if r["pos"] is None), key=furthest)
    if not official:  # sprint qualifying before 2026 sources, or no classification yet
        for i, row in enumerate(others, start=1):
            row["pos"] = i
        return others
    for i, row in enumerate(others, start=official[-1]["pos"] + 1):
        row["pos"] = i
    return official + others


def compute_quali_laps(parts: list[pd.DataFrame | None]) -> dict:
    """Flying laps on a session time axis, in seconds of session time.
    segs: [[segment, start, end], ...], from the first flying lap start to the last lap end.
    laps: {DRV: [[segment, lap end, lap time, compound, deleted 0/1], ...]}."""
    segs, laps = [], {}
    for seg, part in enumerate(parts, start=1):
        if part is None or part.empty:
            continue
        push = _push(part)
        if push.empty:
            continue
        # Flying laps only: out laps include garage time, and the in laps of drivers just
        # knocked out end during the next segment.
        segs.append(
            [
                seg,
                round((push["Time"] - push["LapTime"]).min().total_seconds()),
                round(push["Time"].max().total_seconds()),
            ]
        )
        for lap in push.itertuples():
            laps.setdefault(lap.Driver, []).append(
                [
                    seg,
                    round(lap.Time.total_seconds(), 1),
                    round(lap.LapTime.total_seconds(), 3),
                    lap.Compound if isinstance(lap.Compound, str) else "UNKNOWN",
                    int(lap.Deleted),
                ]
            )
    return {"segs": segs, "laps": laps}
