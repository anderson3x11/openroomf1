"""Load sessions from FastF1. The cache directory is temporary and purged after each run."""

import shutil
from pathlib import Path

import fastf1
from fastf1.core import Session


def load_session(season: int, round_: int, name: str, cache_dir: Path) -> Session:
    """name: FastF1 session name ("Race", "Sprint", "Qualifying", "Practice 1", ...)."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    fastf1.Cache.enable_cache(str(cache_dir))
    session = fastf1.get_session(season, round_, name)
    # Telemetry brings car data and positions (best laps, track map, replay): about 120 MB of
    # temporary cache per session. Messages flag deleted laps.
    session.load(telemetry=True, weather=True, messages=True)
    return session


def purge_cache(cache_dir: Path) -> None:
    # The requests cache keeps its sqlite file open, which blocks deletion on Windows.
    # Note: relies on a private FastF1 attribute, re-check on FastF1 upgrades.
    session = getattr(fastf1.Cache, "_requests_session_cached", None)
    if session is not None:
        session.close()
    shutil.rmtree(cache_dir)
