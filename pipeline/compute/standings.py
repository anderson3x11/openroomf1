"""Championship standings after the race, compared with the previous round."""

import pandas as pd

from pipeline.compute.results import int_or_none
from pipeline.fetch.logos import team_id


def _diff(now: pd.DataFrame, prev: pd.DataFrame, key: str) -> list[tuple]:
    prev_by_key = prev.set_index(key)
    rows = []
    # A driver without a single classification has no position ("-"): listed last.
    for r in now.sort_values("position", na_position="last").itertuples():
        k = getattr(r, key)
        before = prev_by_key.loc[k] if k in prev_by_key.index else None
        rows.append(
            (
                k,
                r,
                None if before is None else int_or_none(before["position"]),
                0.0 if before is None else float(before["points"]),
            )
        )
    return rows


def compute_standings(
    drivers_now: pd.DataFrame,
    drivers_prev: pd.DataFrame,
    teams_now: pd.DataFrame,
    teams_prev: pd.DataFrame,
    results: list[dict],
) -> dict:
    """Previous-round frames are empty after round 1. results is the compute_results output."""
    # Jolpica constructor names differ from FastF1 team names ("RB F1 Team" vs "Racing Bulls"):
    # map each constructor to the FastF1 team of its drivers, so names and logos match the race.
    # Only drivers who stayed in one team are used: a mid-season switch lists both constructors.
    fastf1_team = {r["drv"]: (r["team"], r["tid"]) for r in results}
    team_of = {
        r.constructorNames[0]: fastf1_team[r.driverCode]
        for r in drivers_now.itertuples()
        if r.driverCode in fastf1_team and len(r.constructorNames) == 1
    }

    def team(name: str) -> tuple[str, str]:
        return team_of.get(name, (name, team_id(name)))

    def driver_team(code: str, constructors: list[str]) -> tuple[str, str]:
        return fastf1_team.get(code) or team(constructors[-1])

    drivers = [
        {
            "drv": code,
            "team": driver_team(code, r.constructorNames)[0],
            "tid": driver_team(code, r.constructorNames)[1],
            "pos": int_or_none(r.position),
            "pts": float(r.points),
            "prev": prev_pos,
            "gain": float(r.points) - prev_pts,
        }
        for code, r, prev_pos, prev_pts in _diff(drivers_now, drivers_prev, "driverCode")
    ]
    teams = [
        {
            "team": team(name)[0],
            "tid": team(name)[1],
            "pos": int_or_none(r.position),
            "pts": float(r.points),
            "prev": prev_pos,
            "gain": float(r.points) - prev_pts,
        }
        for name, r, prev_pos, prev_pts in _diff(teams_now, teams_prev, "constructorName")
    ]
    return {"drivers": drivers, "teams": teams}
