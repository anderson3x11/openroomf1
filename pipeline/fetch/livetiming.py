"""Extra feeds read straight from the F1 live timing archive (the source FastF1 uses):
official overtake counts and pit stop times, which FastF1 does not expose.
"""

import json
import urllib.parse
import urllib.request

BASE = "https://livetiming.formula1.com"


def load_feed(api_path: str, feed: str) -> dict:
    """Keyframe of a feed, e.g. load_feed(session.api_path, "OvertakeSeries"). {} if missing."""
    try:
        # Paths may hold accents ("2025-11-09_São_Paulo_Grand_Prix"): percent-encode them.
        url = f"{BASE}{urllib.parse.quote(api_path)}{feed}.json"
        with urllib.request.urlopen(url, timeout=20) as r:
            return json.loads(r.read().decode("utf-8-sig"))
    except (OSError, ValueError) as e:
        # Optional data: the run goes on without it.
        print(f"WARNING: no {feed}: {e!r}")
        return {}
