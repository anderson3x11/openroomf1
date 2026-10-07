"""Tyre stints: compound, first and last lap, tyre age at the start."""

import pandas as pd


def compute_strategy(laps: pd.DataFrame) -> list[dict]:
    stints = []
    valid = laps.dropna(subset=["Stint", "LapNumber"])
    for (drv, stint), grp in valid.groupby(["Driver", "Stint"]):
        first = grp.loc[grp["LapNumber"].idxmin()]
        compound = first["Compound"]
        stints.append(
            {
                "drv": drv,
                "stint": int(stint),
                "cmp": compound if isinstance(compound, str) else "UNKNOWN",
                "from": int(grp["LapNumber"].min()),
                "to": int(grp["LapNumber"].max()),
                "age": None if pd.isna(first["TyreLife"]) else int(first["TyreLife"]) - 1,
                "new": bool(first["FreshTyre"]) if pd.notna(first["FreshTyre"]) else None,
            }
        )
    return stints
