"""Neutralizations (safety car, virtual safety car, red flag) from FastF1 track status codes."""

import pandas as pd

# A lap's TrackStatus string lists every status seen during that lap. Checked in priority order.
NEUTRAL_CODES = {"5": "red", "4": "sc", "6": "vsc", "7": "vsc"}


def neutral_kind(status) -> str | None:
    """'red' | 'sc' | 'vsc' if the lap was neutralized at some point, else None."""
    if not isinstance(status, str):
        return None
    return next((kind for code, kind in NEUTRAL_CODES.items() if code in status), None)


def neutralized_laps(laps: pd.DataFrame) -> dict[int, str]:
    """Race lap number -> kind, read on the leader's laps (lapped cars would shift it)."""
    valid = laps.dropna(subset=["LapNumber", "Time"])
    leader_laps = valid.loc[valid.groupby("LapNumber")["Time"].idxmin()]
    out = {}
    for lap, status in zip(leader_laps["LapNumber"], leader_laps["TrackStatus"], strict=True):
        if kind := neutral_kind(status):
            out[int(lap)] = kind
    return out


def neutral_spans(neutral: dict[int, str]) -> list[dict]:
    """Group consecutive laps of the same kind: [{"kind": "sc", "from": 31, "to": 35}]."""
    spans: list[dict] = []
    for lap in sorted(neutral):
        kind = neutral[lap]
        if spans and spans[-1]["kind"] == kind and spans[-1]["to"] == lap - 1:
            spans[-1]["to"] = lap
        else:
            spans.append({"kind": kind, "from": lap, "to": lap})
    return spans
