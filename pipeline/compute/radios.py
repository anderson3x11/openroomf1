"""Team radios placed on the race timeline: the lap the driver was on when it was sent."""

import pandas as pd


def session_to_utc(messages: pd.DataFrame, laps: pd.DataFrame) -> pd.Timestamp | None:
    """UTC time (naive) of session time zero, or None if no anchor is found.

    LapStartDate is often missing without telemetry. Race control messages carry UTC times:
    "RACE START" matches the start of lap 1, the chequered flag matches the winner's finish,
    both within a couple of seconds. The race start is missing after a safety car start.
    """

    def first(mask) -> pd.Timestamp | None:
        times = messages.loc[mask, "Time"].dropna()
        return None if times.empty else pd.Timestamp(times.iloc[0])

    start = first(messages["Message"] == "RACE START")
    if start is not None:
        return start - laps.loc[laps["LapNumber"] == 1, "LapStartTime"].min()
    finish = first(messages["Flag"] == "CHEQUERED")
    if finish is not None:
        return finish - laps.loc[laps["LapNumber"] == laps["LapNumber"].max(), "Time"].min()
    return None


def compute_radios(
    radios: pd.DataFrame, laps: pd.DataFrame, results: list[dict], offset: pd.Timestamp | None
) -> list[dict]:
    """offset: UTC time of session time zero. The lap is found from lap end times (always
    present) rather than lap start times, which are missing for whole races (Canada 2026)."""
    drv_by_number = {r["num"]: r["drv"] for r in results}
    ends = laps.dropna(subset=["Time", "LapNumber"])
    if offset is not None:
        ends = ends.assign(end=(ends["Time"] + offset).dt.tz_localize("UTC"))
        lap1 = laps.loc[laps["LapNumber"] == 1]
        first = lap1["LapStartTime"].min()
        if pd.isna(first):  # no start time at all: lap 1 began about one lap before its end
            first = lap1["Time"].min() - lap1["LapTime"].median()
        race_start = (first + offset).tz_localize("UTC")
    out = []
    for r in radios.sort_values("date").itertuples():
        drv = drv_by_number.get(str(r.driver_number))
        if drv is None:
            continue
        lap = None
        if offset is not None:
            own = ends[ends["Driver"] == drv]
            done = int((own["end"] < r.date).sum())
            last = int(own["LapNumber"].max()) if len(own) else 0
            lap = 0 if r.date < race_start else max(1, min(done + 1, last))
        out.append(
            {"drv": drv, "lap": lap, "at": r.date.strftime("%H:%M:%S"), "url": r.recording_url}
        )
    return out
