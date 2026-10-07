"""Load sessions from FastF1. The cache directory is temporary and purged after each run."""

import shutil
from pathlib import Path

import fastf1
from fastf1.core import Session


def load_race(season: int, round_: int, cache_dir: Path) -> Session:
    cache_dir.mkdir(parents=True, exist_ok=True)
    fastf1.Cache.enable_cache(str(cache_dir))
    session = fastf1.get_session(season, round_, "R")
    # Telemetry brings car positions (circuit outline, replay): about 120 MB of temporary cache.
    session.load(telemetry=True, weather=True, messages=True)
    return session


def purge_cache(cache_dir: Path) -> None:
    # The requests cache keeps its sqlite file open, which blocks deletion on Windows.
    # Note: relies on a private FastF1 attribute, re-check on FastF1 upgrades.
    session = getattr(fastf1.Cache, "_requests_session_cached", None)
    if session is not None:
        session.close()
    shutil.rmtree(cache_dir)
