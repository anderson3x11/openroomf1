"""Pit stops: lap, time spent in the pit lane, positions before and after."""

import pandas as pd

from pipeline.compute.track import neutral_kind


def _pos(by_lap: pd.Series, lap: int) -> int | None:
    value = by_lap.get(lap)
    return None if value is None or pd.isna(value) else int(value)


def _stationary_times(feed: dict, drv_by_number: dict[str, str]) -> dict[tuple[str, int], float]:
    """(DRV, lap) -> stationary time in seconds, from the live timing PitStopSeries feed."""
    out = {}
    for number, stops in feed.get("PitTimes", {}).items():
        for s in stops:
            stop = s.get("PitStop", {})
            try:
                out[(drv_by_number[number], int(stop["Lap"]))] = float(stop["PitStopTime"])
            except (KeyError, ValueError):
                continue
    return out


def compute_pitstops(laps: pd.DataFrame, feed: dict, results: list[dict]) -> list[dict]:
    """feed: PitStopSeries keyframe ({} when unavailable), results: compute_results output."""
    stationary = _stationary_times(feed, {r["num"]: r["drv"] for r in results})
    stops = []
    for drv, grp in laps.dropna(subset=["LapNumber"]).groupby("Driver"):
        grp = grp.set_index(grp["LapNumber"].astype(int))
        for lap, row in grp[grp["PitInTime"].notna()].iterrows():
            out_time = grp["PitOutTime"].get(lap + 1)
            if out_time is None or pd.isna(out_time):
                continue  # retired in the pits, or end of race
            stops.append(
                {
                    "drv": drv,
                    "lap": int(lap),
                    "lane": round((out_time - row["PitInTime"]).total_seconds(), 1),
                    "stop": stationary.get((drv, int(lap))),
                    "before": _pos(grp["Position"], lap - 1),
                    "after": _pos(grp["Position"], lap + 1),
                    "under": neutral_kind(row["TrackStatus"]),
                }
            )
    return sorted(stops, key=lambda s: (s["lap"], s["drv"]))
