"""Official race highlights video on the Formula 1 YouTube channel.

The channel RSS feed (no API key) only lists the 15 latest videos: enough right after a race.
Older GPs come from pipeline/highlights.json, filled by hand: {"SEASON": {"ROUND": "VIDEO_ID"}}.
"""

import json
import re
import urllib.request
from pathlib import Path

RSS = "https://www.youtube.com/feeds/videos.xml?channel_id=UCB_qr75-ydFVKSF9Dmo6izg"
MANUAL = Path(__file__).resolve().parent.parent / "highlights.json"


def match_highlights(feed_xml: str, season: int, event_name: str) -> str | None:
    """Video id of "Race Highlights | SEASON EVENT" in the feed, if present."""
    short = event_name.removesuffix(" Grand Prix")
    entries = re.findall(r"<yt:videoId>(.*?)</yt:videoId>.*?<title>(.*?)</title>", feed_xml, re.S)
    return next(
        (
            vid
            for vid, title in entries
            if "Race Highlights" in title and str(season) in title and short in title
        ),
        None,
    )


def find_highlights(season: int, round_: int, event_name: str) -> str | None:
    try:
        with urllib.request.urlopen(RSS, timeout=20) as r:
            if vid := match_highlights(r.read().decode("utf-8"), season, event_name):
                return vid
    except OSError as e:
        print(f"WARNING: YouTube feed unavailable: {e!r}")
    manual = json.loads(MANUAL.read_text(encoding="utf-8")) if MANUAL.exists() else {}
    return manual.get(str(season), {}).get(str(round_))


def fetch_thumbnail(video_id: str, path: Path) -> bool:
    """Saves the video thumbnail, so the site serves it instead of linking to YouTube."""
    for name in ("maxresdefault", "hqdefault"):  # maxres is missing on some videos
        try:
            with urllib.request.urlopen(
                f"https://i.ytimg.com/vi/{video_id}/{name}.jpg", timeout=20
            ) as r:
                path.write_bytes(r.read())
            return True
        except OSError:
            continue
    print(f"WARNING: no thumbnail for {video_id}")
    return False
