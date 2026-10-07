"""Write the pipeline output: data/SEASON/index.json and one folder per Grand Prix."""

import json
import shutil
import unicodedata
from pathlib import Path


def slugify(text: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return "-".join(ascii_text.lower().replace("grand prix", "").split())


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")


def dir_size(path: Path) -> int:
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())


def write_gp(data_dir: Path, meta: dict, files: dict[str, object]) -> Path:
    """Replace the GP folder entirely (idempotent) and update the season index."""
    season_dir = data_dir / str(meta["season"])
    gp_dir = season_dir / meta["slug"]
    if gp_dir.exists():
        shutil.rmtree(gp_dir)
    write_json(gp_dir / "meta.json", meta)
    for rel, obj in files.items():
        write_json(gp_dir / rel, obj)

    index_path = season_dir / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8")) if index_path.exists() else []
    index = [e for e in index if e["round"] != meta["round"]] + [
        {
            k: meta.get(k)
            for k in (
                "round",
                "slug",
                "name",
                "official",
                "country",
                "date",
                "circuit",
                "host",
                "flag",
            )
        }
    ]
    write_json(index_path, sorted(index, key=lambda e: e["round"]))
    return gp_dir
