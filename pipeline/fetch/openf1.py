"""Team radio metadata from OpenF1. Two requests per run (limit: 3 req/s, 30 req/min).

Audio files stay on the F1 live timing static server: we only keep their URL.
"""

import json
import urllib.error
import urllib.request
from datetime import date

import pandas as pd

API = "https://api.openf1.org/v1"


def _get(path: str) -> list[dict]:
    with urllib.request.urlopen(f"{API}/{path}", timeout=20) as r:
        return json.loads(r.read())


def load_team_radio(season: int, race_day: date) -> pd.DataFrame:
    """Radios of the race held on race_day. OpenF1 and FastF1 may name events differently
    (round 16 of 2026: "Kuala Lumpur" vs "Bahrain"), so the session is matched by date."""
    try:
        sessions = _get(f"sessions?year={season}&session_name=Race")
        key = next(
            s["session_key"]
            for s in sessions
            if s["date_start"][:10] == race_day.isoformat() and not s.get("is_cancelled")
        )
        radios = pd.DataFrame(_get(f"team_radio?session_key={key}"))
    except urllib.error.HTTPError as e:
        if e.code != 404:  # 404 = OpenF1 has no radio for this race (early 2026 rounds)
            print(f"WARNING: no team radio: {e!r}")
        return pd.DataFrame(columns=["driver_number", "date", "recording_url"])
    except (OSError, StopIteration, ValueError) as e:
        # Radios are a bonus: never fail the run for them.
        print(f"WARNING: no team radio: {e!r}")
        return pd.DataFrame(columns=["driver_number", "date", "recording_url"])
    radios["date"] = pd.to_datetime(radios["date"], utc=True, format="ISO8601")
    return radios
