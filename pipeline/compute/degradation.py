"""Tyre degradation per stint: lap time lost per lap of tyre age, corrected for fuel."""

import numpy as np
import pandas as pd

from pipeline.compute.track import neutral_kind

# Burning fuel makes the car faster lap after lap, which hides part of the tyre wear.
# Note: a flat 0.03 s per lap, the usual rule of thumb (about 1.5 kg of fuel a lap);
# a per circuit value would need the fuel load, which teams do not publish.
FUEL_GAIN = 0.03
MIN_LAPS = 5  # clean laps needed to fit a slope


def compute_degradation(laps: pd.DataFrame) -> list[dict]:
    """Clean laps only: no pit in/out lap, no SC/VSC/red, not the first 2 laps of the stint
    (tyres still warming up). deg = slope of the fuel corrected lap time vs tyre age, s/lap."""
    out = []
    valid = laps.dropna(subset=["LapNumber", "LapTime", "Stint", "TyreLife"])
    for (drv, stint), grp in valid.groupby(["Driver", "Stint"]):
        first = grp["LapNumber"].min()
        clean = grp[
            grp["PitInTime"].isna()
            & grp["PitOutTime"].isna()
            & grp["TrackStatus"].map(neutral_kind).isna()
            & (grp["LapNumber"] >= first + 2)
        ]
        if len(clean) < MIN_LAPS:
            continue
        seconds = clean["LapTime"].dt.total_seconds() + FUEL_GAIN * clean["LapNumber"]
        slope, intercept = np.polyfit(clean["TyreLife"].astype(float), seconds, 1)
        out.append(
            {
                "drv": drv,
                "stint": int(stint),
                "cmp": grp["Compound"].iloc[0]
                if isinstance(grp["Compound"].iloc[0], str)
                else "UNKNOWN",
                "from": int(first),
                "to": int(grp["LapNumber"].max()),
                "n": len(clean),
                "deg": round(float(slope), 3),
            }
        )
    return out
