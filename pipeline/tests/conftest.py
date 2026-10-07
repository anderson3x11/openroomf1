import json
from pathlib import Path

import pandas as pd
import pytest

FIXTURES = Path(__file__).parent / "fixtures"
PREFIX = "azerbaijan_2026_"
TIME_COLUMNS = ["Time", "LapTime", "PitInTime", "PitOutTime"]


def _read(name: str, **kwargs) -> pd.DataFrame:
    return pd.read_csv(FIXTURES / f"{PREFIX}{name}.csv", **kwargs)


@pytest.fixture
def laps() -> pd.DataFrame:
    """Azerbaijan 2026 race, reduced to RUS (winner), ANT (16th to 5th) and NOR (retired).

    Times are stored in seconds and turned back into Timedelta, as FastF1 provides them.
    """
    df = _read("laps", dtype={"TrackStatus": str})
    for col in TIME_COLUMNS:
        df[col] = pd.to_timedelta(df[col], unit="s")
    return df


@pytest.fixture
def lapstarts() -> pd.DataFrame:
    """Lap start session times of the fixture drivers (LapStartTime, in seconds in the CSV)."""
    df = _read("lapstarts")
    df["LapStartTime"] = pd.to_timedelta(df["LapStartTime"], unit="s")
    return df


@pytest.fixture
def radios() -> pd.DataFrame:
    """OpenF1 team radio metadata of the full race (all drivers)."""
    df = _read("radios")
    df["date"] = pd.to_datetime(df["date"], utc=True, format="ISO8601")
    return df


@pytest.fixture
def results() -> pd.DataFrame:
    return _read("results", dtype={"TeamColor": str})


@pytest.fixture
def messages() -> pd.DataFrame:
    """Race control messages of the full race, blue flags removed."""
    return _read("messages")


@pytest.fixture
def standings() -> dict[str, pd.DataFrame]:
    """Standings after round 15 and round 14, reduced to the fixture drivers and their teams."""
    out = {f"{k}_{t}": _read(f"{k}_{t}") for k in ("drivers", "teams") for t in ("now", "prev")}
    for tag in ("now", "prev"):
        # Jolpica gives a list of constructors per driver, stored pipe-separated in the CSV.
        drivers = out[f"drivers_{tag}"]
        drivers["constructorNames"] = drivers["constructorNames"].str.split("|")
    return out


@pytest.fixture
def live_feeds() -> dict[str, dict]:
    """Live timing OvertakeSeries and PitStopSeries keyframes of the full race."""
    return {
        feed: json.loads((FIXTURES / f"{PREFIX}{feed}.json").read_text())
        for feed in ("OvertakeSeries", "PitStopSeries")
    }


@pytest.fixture
def full_laps(laps, lapstarts) -> pd.DataFrame:
    """Fixture laps with lap start times, sector times and speed traps."""
    sectors = _read("sectors")
    for col in ("Sector1Time", "Sector2Time", "Sector3Time"):
        sectors[col] = pd.to_timedelta(sectors[col], unit="s")
    return laps.merge(lapstarts, on=["Driver", "LapNumber"]).merge(
        sectors, on=["Driver", "LapNumber"]
    )


@pytest.fixture
def weather() -> pd.DataFrame:
    """FastF1 weather readings of the full race (about one a minute)."""
    df = _read("weather")
    df["Time"] = pd.to_timedelta(df["Time"], unit="s")
    return df
