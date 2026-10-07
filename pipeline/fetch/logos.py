"""Team logos from the formula1.com media CDN, stored once per season in data/SEASON/logos/."""

import re
import urllib.request
from pathlib import Path

LOGO_URL = (
    "https://media.formula1.com/image/upload/c_lfill,w_96/q_auto/v1740000001/"
    "common/f1/{season}/{tid}/{season}{tid}{variant}.webp"
)
# Teams shown with the white logo: color ones too dark for the theme, or chosen for readability.
# Note: hand-picked for 2026, review when a season or a livery changes.
WHITE_LOGOS = {"astonmartin", "audi", "cadillac", "mercedes", "racingbulls", "williams"}


def team_id(team_name: str) -> str:
    """'Red Bull Racing' -> 'redbullracing', the slug used by the F1 media CDN."""
    return re.sub(r"[^a-z0-9]", "", team_name.lower())


def fetch_logos(season: int, team_ids: set[str], dest: Path) -> None:
    """TID.webp for the dark theme, TID-light.webp (color logo) for the light theme."""
    dest.mkdir(parents=True, exist_ok=True)
    for tid in sorted(team_ids):
        dark = "logowhite" if tid in WHITE_LOGOS else "logo"
        for name, variant in ((f"{tid}.webp", dark), (f"{tid}-light.webp", "logo")):
            path = dest / name
            if path.exists():
                continue
            try:
                url = LOGO_URL.format(season=season, tid=tid, variant=variant)
                with urllib.request.urlopen(url, timeout=10) as r:
                    path.write_bytes(r.read())
            except OSError as e:
                # A missing logo must not fail the run: the front falls back to the team color.
                print(f"WARNING: no logo {name}: {e}")
