"""OpenF1 API client. Since October 2026 the F1 live timing archive needs an F1 TV login;
OpenF1 records the live feed and serves it freely: it is the timing source of the pipeline.

Free tier: 3 requests per second and 30 per minute, so requests are spaced out. Responses are
cached on disk in the run's cache directory, purged after each successful run.
"""

import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://api.openf1.org/v1"
SPACING = 2.1  # seconds between requests: 30 per minute at most
_cache_dir: Path | None = None
_last = 0.0


def use_cache(cache_dir: Path) -> None:
    global _cache_dir
    _cache_dir = cache_dir / "openf1"
    _cache_dir.mkdir(parents=True, exist_ok=True)


def get(endpoint: str, **params) -> list[dict]:
    """Records of an endpoint. Filters like "date>=" go in the key: get("laps", session_key=1,
    **{"date_start>": "..."}). An empty list when OpenF1 has nothing (it answers 404)."""
    global _last
    url = f"{API}/{endpoint}?{urllib.parse.urlencode(params, safe='<>=:')}"
    cached = _cache_dir / f"{hashlib.sha1(url.encode()).hexdigest()}.json" if _cache_dir else None
    if cached and cached.exists():
        return json.loads(cached.read_text(encoding="utf-8"))
    for attempt in range(5):
        time.sleep(max(0.0, _last + SPACING - time.monotonic()))
        _last = time.monotonic()
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                data = json.loads(r.read())
            break
        except urllib.error.HTTPError as e:
            if e.code == 404:
                data = []
                break
            # Over the limit anyway (429), or a passing server error (500 seen in Mexico 2026).
            if (e.code == 429 or e.code >= 500) and attempt < 4:
                time.sleep(20 * (attempt + 1))
                continue
            raise
    if cached:
        cached.write_text(json.dumps(data), encoding="utf-8")
    return data


def find_session(season: int, name: str, day: str) -> dict:
    """The session of that name held on that UTC day (YYYY-MM-DD). OpenF1 and FastF1 may name
    events differently (round 16 of 2026: "Kuala Lumpur" vs "Bahrain"): matched by date."""
    for s in get("sessions", year=season, session_name=name):
        if s["date_start"][:10] == day and not s.get("is_cancelled"):
            return s
    raise LookupError(f"OpenF1 has no {name} on {day}")


def circuit_info(circuit_key: int, season: int) -> dict | None:
    """Rotation and corners of the track map, from MultiViewer (what FastF1 used)."""
    url = f"https://api.multiviewer.app/api/v1/circuits/{circuit_key}/{season}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "openroomf1"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except (OSError, ValueError) as e:
        print(f"WARNING: no circuit info: {e!r}")
        return None
