"""Championship standings from Jolpica (Ergast compatible), through fastf1.ergast.

Four requests per run, well under the 4 req/s and 500 req/h limits.
"""

import pandas as pd
from fastf1.ergast import Ergast

DRIVER_COLS = ["position", "points", "driverCode", "constructorNames"]
TEAM_COLS = ["position", "points", "constructorName"]


def _first(response, cols: list[str]) -> pd.DataFrame:
    if not response.content:
        return pd.DataFrame(columns=cols)
    return response.content[0][cols].copy()


def load_standings(season: int, round_: int) -> dict[str, pd.DataFrame]:
    ergast = Ergast()
    out = {}
    for tag, rnd in (("now", round_), ("prev", round_ - 1)):
        if rnd < 1:
            out[f"drivers_{tag}"] = pd.DataFrame(columns=DRIVER_COLS)
            out[f"teams_{tag}"] = pd.DataFrame(columns=TEAM_COLS)
            continue
        drivers = _first(ergast.get_driver_standings(season=season, round=rnd), DRIVER_COLS)
        out[f"drivers_{tag}"] = drivers  # constructorNames: list, not in chronological order
        out[f"teams_{tag}"] = _first(
            ergast.get_constructor_standings(season=season, round=rnd), TEAM_COLS
        )
    return out


# Country names (FastF1 and Jolpica spellings) -> ISO 3166 alpha-2, for the flags.
# Note: covers the 2018-2026 calendars, add a country when a new venue appears.
FLAGS = {
    "Australia": "au",
    "Austria": "at",
    "Azerbaijan": "az",
    "Bahrain": "bh",
    "Belgium": "be",
    "Brazil": "br",
    "Canada": "ca",
    "China": "cn",
    "France": "fr",
    "Germany": "de",
    "Hungary": "hu",
    "Italy": "it",
    "Japan": "jp",
    "Malaysia": "my",
    "Mexico": "mx",
    "Monaco": "mc",
    "Netherlands": "nl",
    "Portugal": "pt",
    "Qatar": "qa",
    "Russia": "ru",
    "Saudi Arabia": "sa",
    "Singapore": "sg",
    "Spain": "es",
    "Turkey": "tr",
    "UAE": "ae",
    "UK": "gb",
    "USA": "us",
    "Vietnam": "vn",
    "United Kingdom": "gb",
    "United States": "us",
    "United Arab Emirates": "ae",
}


def load_circuit(season: int, round_: int) -> dict:
    """Circuit name and host country: the "Bahrain Grand Prix in Malaysia" is at Sepang.
    The flag is not here: it follows the Grand Prix country, not the host (see cli)."""
    schedule = Ergast().get_race_schedule(season=season, round=round_)
    if schedule.empty:
        return {"circuit": None, "locality": None, "host": None}
    row = schedule.iloc[0]
    return {
        "circuit": row["circuitName"],
        "locality": row["locality"],
        "host": row["country"],
    }
