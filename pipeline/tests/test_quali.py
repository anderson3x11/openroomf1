import numpy as np

from pipeline.compute.quali import compute_quali, compute_quali_laps


def test_quali_official_order(quali_parts, quali_results):
    rows = compute_quali(quali_parts, quali_results)
    assert [r["drv"] for r in rows] == ["VER", "ANT", "LAW", "COL", "PER"]
    assert rows[0]["q"] == [96.477, 95.696, 95.13]  # same as the official Q1, Q2, Q3 times
    assert rows[2]["q"][2] is None
    assert rows[3]["q"][1:] == [None, None]  # COL's 1:48 lap in Q2 was no flying lap


def test_quali_order_without_official_positions(quali_parts, quali_results):
    """Sprint qualifying: FastF1 has no positions. COL reached Q2 without a time: he stays
    behind the Q2 runners, ahead of the drivers out in Q1, like the official result."""
    shuffled = quali_results.assign(Position=float("nan")).sample(frac=1, random_state=1)
    rows = compute_quali(quali_parts, shuffled)
    assert [(r["drv"], r["pos"]) for r in rows] == [
        ("VER", 1),
        ("ANT", 2),
        ("LAW", 3),
        ("COL", 4),
        ("PER", 5),
    ]


def test_quali_ignores_deleted_laps(quali_parts, quali_results):
    q2 = quali_parts[1].copy()
    q2["LapTime"] = q2["LapTime"].mask(q2["Deleted"], np.timedelta64(90, "s"))  # however fast
    rows = compute_quali([quali_parts[0], q2, quali_parts[2]], quali_results)
    assert next(r for r in rows if r["drv"] == "ANT")["q"][1] == 95.959


def test_quali_laps(quali_parts):
    out = compute_quali_laps(quali_parts)
    (_, _, q1_end), (_, q2_start, q2_end), (_, q3_start, _) = out["segs"]
    assert q1_end < q2_start and q2_end < q3_start  # segments in order, no overlap
    ver = out["laps"]["VER"]
    assert min(lap[2] for lap in ver if lap[0] == 3) == 95.13
    assert all(lap[2] < 110 for laps in out["laps"].values() for lap in laps)  # no cool-down lap
    assert [lap[4] for lap in out["laps"]["ANT"]].count(1) == 1  # the deleted lap, flagged
