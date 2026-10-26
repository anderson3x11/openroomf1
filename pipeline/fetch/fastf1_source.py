"""Load sessions from FastF1. The cache directory is temporary and purged after each run."""

import shutil
from pathlib import Path

import fastf1

from pipeline.fetch import openf1


def prepare_cache(cache_dir: Path) -> None:
    """FastF1 still serves the calendar and Jolpica; OpenF1 responses go in the same folder."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    fastf1.Cache.enable_cache(str(cache_dir))
    openf1.use_cache(cache_dir)


def purge_cache(cache_dir: Path) -> None:
    # The requests cache keeps its sqlite file open, which blocks deletion on Windows.
    # Note: relies on a private FastF1 attribute, re-check on FastF1 upgrades.
    session = getattr(fastf1.Cache, "_requests_session_cached", None)
    if session is not None:
        session.close()
    shutil.rmtree(cache_dir)
