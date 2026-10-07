"""Official results, starting grid and positions gained."""

import pandas as pd

from pipeline.fetch.logos import team_id


def int_or_none(value) -> int | None:
    return None if pd.isna(value) else int(value)


def compute_results(results: pd.DataFrame) -> list[dict]:
    rows = []
    for r in results.sort_values("Position").itertuples():
        # Grid 0 means a pit lane start: no meaningful "positions gained".
        grid = int_or_none(r.GridPosition) or None
        pos = int_or_none(r.Position)
        rows.append(
            {
                "drv": r.Abbreviation,
                "num": str(r.DriverNumber),
                "name": r.FullName,
                "team": r.TeamName,
                "tid": team_id(r.TeamName),
                "color": f"#{r.TeamColor}" if isinstance(r.TeamColor, str) else None,
                "grid": grid,
                "pos": pos,
                "cls": str(r.ClassifiedPosition),
                "status": r.Status,
                "pts": float(r.Points),
                "gain": grid - pos if grid and pos else None,
            }
        )
    return rows
