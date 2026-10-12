import pandas as pd

from pipeline.compute.degradation import FUEL_GAIN, compute_degradation
from pipeline.compute.events import compute_events
from pipeline.compute.gaps import compute_gaps
from pipeline.compute.laps import compute_lap_matrix, compute_race_trace
from pipeline.compute.laptimes import compute_laptimes
from pipeline.compute.overtakes import compute_overtakes
from pipeline.compute.pitstops import compute_pitstops
from pipeline.compute.positions import compute_positions
from pipeline.compute.radios import compute_radios, session_to_utc
from pipeline.compute.results import compute_results
from pipeline.compute.speeds import compute_speeds
from pipeline.compute.standings import compute_standings
from pipeline.compute.strategy import compute_strategy
from pipeline.compute.summary import fastest_lap
from pipeline.compute.track import neutral_kind, neutral_spans, neutralized_laps
from pipeline.compute.weather import compute_weather
from pipeline.fetch.logos import team_id
from pipeline.fetch.youtube import match_highlights


def test_results_order_and_gain(results):
    rows = compute_results(results)
    assert [r["drv"] for r in rows] == ["RUS", "ANT", "NOR"]
    ant = rows[1]
    assert (ant["grid"], ant["pos"], ant["gain"], ant["color"]) == (16, 5, 11, "#00D7B6")
    assert rows[2]["cls"] == "R"


def test_results_pit_lane_start_has_no_gain(results):
    results.loc[results["Abbreviation"] == "RUS", "GridPosition"] = 0.0
    rus = compute_results(results)[0]
    assert rus["grid"] is None and rus["gain"] is None


def test_positions(laps, results):
    out = compute_positions(laps, results)
    assert out["laps"] == 51
    rus = out["pos"]["RUS"]
    assert len(rus) == 52 and rus[0] == 1 and rus[51] == 1
    nor = out["pos"]["NOR"]
    assert nor[0] == 5 and nor[35] == 9
    assert nor[36] is None and nor[51] is None  # retired, no position


def test_strategy(laps):
    stints = {(s["drv"], s["stint"]): s for s in compute_strategy(laps)}
    assert len(stints) == 8
    assert stints[("RUS", 1)] == {
        "drv": "RUS",
        "stint": 1,
        "cmp": "MEDIUM",
        "from": 1,
        "to": 31,
        "age": 2,
        "new": False,
    }
    ant3 = stints[("ANT", 3)]
    assert (ant3["cmp"], ant3["from"], ant3["to"], ant3["age"]) == ("SOFT", 37, 51, 6)


def test_strategy_unknown_tyre_age(laps):
    """Singapore 2026: no TyreLife on some stints, and FreshTyre False by default."""
    rus2 = (laps["Driver"] == "RUS") & (laps["Stint"] == 2)
    laps = laps.assign(
        TyreLife=laps["TyreLife"].mask(rus2), FreshTyre=laps["FreshTyre"].mask(rus2, False)
    )
    stint = next(s for s in compute_strategy(laps) if (s["drv"], s["stint"]) == ("RUS", 2))
    assert stint["age"] is None and stint["new"] is None


def test_team_id_matches_cdn_slug():
    assert team_id("Red Bull Racing") == "redbullracing"
    assert team_id("Haas F1 Team") == "haasf1team"


def test_neutralized_laps_two_safety_cars(laps):
    # Two back-to-back safety cars (deployed on laps 31 and 36) merge into one span per lap.
    assert neutral_spans(neutralized_laps(laps)) == [{"kind": "sc", "from": 31, "to": 38}]
    assert neutral_kind("124") == "sc" and neutral_kind("12") is None and neutral_kind(None) is None
    assert neutral_spans({3: "vsc", 4: "vsc", 7: "sc"}) == [
        {"kind": "vsc", "from": 3, "to": 4},
        {"kind": "sc", "from": 7, "to": 7},
    ]


def test_gaps(laps):
    out = compute_gaps(laps)
    assert out["gap"]["RUS"][51] == 0.0  # winner
    assert out["gap"]["ANT"][51] > 0
    assert out["gap"]["NOR"][51] is None  # retired
    assert out["gap"]["RUS"][0] is None


def test_pitstops(laps, results, live_feeds):
    stops = compute_pitstops(laps, live_feeds["PitStopSeries"], compute_results(results))
    ant = [s for s in stops if s["drv"] == "ANT"]
    assert ant[0] == {
        "drv": "ANT",
        "lap": 30,
        "lane": 20.9,
        "stop": 2.6,  # official stationary time
        "before": 9,
        "after": 8,
        "under": "sc",
    }
    # Lap 36: tyres changed while all cars went through the pit lane, no official stop time.
    assert ant[1]["lap"] == 36 and ant[1]["stop"] is None


def test_pitstops_without_feed(laps, results):
    stops = compute_pitstops(laps, {}, compute_results(results))
    assert stops and all(s["stop"] is None for s in stops)


def test_overtakes(results, live_feeds):
    out = compute_overtakes(live_feeds["OvertakeSeries"], compute_results(results))
    assert out == {"RUS": 0, "ANT": 14, "NOR": 4}  # RUS led every lap
    assert compute_overtakes({}, compute_results(results)) == {"RUS": 0, "ANT": 0, "NOR": 0}


def test_overtakes_noisy_feed(results):
    # Round 1 2026 archive: events repeated a few ms apart, and artifacts counting 21.
    feed = {
        "Overtakes": {
            "12": [
                {"Timestamp": "2026-03-08T04:05:57.047Z", "count": 1},
                {"Timestamp": "2026-03-08T04:05:57.048Z", "count": 1},
                {"Timestamp": "2026-03-08T04:06:00.301Z", "count": 21},
                {"Timestamp": "2026-03-08T04:14:56.186Z", "count": 2},
            ]
        }
    }
    assert compute_overtakes(feed, compute_results(results))["ANT"] == 3


def test_fastest_lap(laps):
    assert fastest_lap(laps) == {"drv": "RUS", "lap": 49, "t": 104.916}
    deleted = laps.assign(Deleted=(laps["Driver"] == "RUS") & (laps["LapNumber"] == 49))
    assert fastest_lap(deleted)["t"] > 104.916


def test_laptimes_exclude_neutralized_and_pit_laps(laps):
    times = compute_laptimes(laps)
    ant_laps = {lap for lap, _ in times["ANT"]}
    assert 1 not in ant_laps and 30 not in ant_laps  # first lap, pit in under safety car
    assert not ant_laps & set(range(31, 39))  # safety car laps
    assert all(90 < t < 130 for _, t in times["ANT"])


def test_events(messages):
    out = compute_events(messages, {31: "sc", 32: "sc"})
    kinds = [m["kind"] for m in out["msgs"]]
    assert kinds.count("sc") == 4 and kinds.count("finish") == 1
    penalty = next(m for m in out["msgs"] if m["kind"] == "penalty")
    assert penalty["drv"] == ["COL"]
    assert out["neutral"] == [{"kind": "sc", "from": 31, "to": 32}]


def test_standings(standings, results):
    out = compute_standings(**standings, results=compute_results(results))
    rus = next(d for d in out["drivers"] if d["drv"] == "RUS")
    assert (rus["pos"], rus["prev"], rus["gain"], rus["tid"]) == (2, 2, 25.0, "mercedes")
    merc = out["teams"][0]
    assert (merc["team"], merc["gain"], merc["tid"]) == ("Mercedes", 35.0, "mercedes")


def test_standings_mid_season_switch_does_not_rename_team(standings, results):
    # NOR listed with two constructors (like LAW in 2026): he must not drag McLaren onto
    # another team's name, and he keeps his FastF1 team.
    drivers = standings["drivers_now"]
    drivers["constructorNames"] = [
        ["Racing Bulls", "McLaren"] if code == "NOR" else names
        for code, names in zip(drivers["driverCode"], drivers["constructorNames"], strict=True)
    ]
    out = compute_standings(**standings, results=compute_results(results))
    nor = next(d for d in out["drivers"] if d["drv"] == "NOR")
    assert (nor["team"], nor["tid"]) == ("McLaren", "mclaren")
    assert "Racing Bulls" not in {t["team"] for t in out["teams"]}


def test_standings_driver_without_position(standings):
    # Round 1 2026: STR had no position yet ("-" in Jolpica), in the current or previous round.
    for tag in ("now", "prev"):
        standings[f"drivers_{tag}"].loc[2, "position"] = float("nan")
    out = compute_standings(**standings, results=[])
    nor = out["drivers"][-1]
    assert (nor["drv"], nor["pos"], nor["prev"]) == ("NOR", None, None)


def test_standings_first_round_has_no_previous(standings):
    empty = {k: v.iloc[0:0] if k.endswith("prev") else v for k, v in standings.items()}
    out = compute_standings(**empty, results=[])
    assert out["drivers"][0]["prev"] is None
    assert out["drivers"][0]["gain"] == out["drivers"][0]["pts"]


RACE_START = pd.Timestamp("2026-09-26 11:03:51")  # "RACE START" message, UTC
CHEQUERED = pd.Timestamp("2026-09-26 12:41:52")


def _clock_messages(messages, start, finish):
    """The fixture messages have no time: set the two anchors."""
    m = messages.assign(Time=pd.NaT)
    m.loc[m["Message"] == "RACE START", "Time"] = start
    m.loc[m["Flag"] == "CHEQUERED", "Time"] = finish
    return m


def test_session_to_utc_anchors_agree(messages, laps, lapstarts):
    laps = laps.merge(lapstarts, on=["Driver", "LapNumber"])
    from_start = session_to_utc(_clock_messages(messages, RACE_START, pd.NaT), laps)
    from_finish = session_to_utc(_clock_messages(messages, pd.NaT, CHEQUERED), laps)
    assert abs((from_start - from_finish).total_seconds()) < 3
    assert session_to_utc(_clock_messages(messages, pd.NaT, pd.NaT), laps) is None


def test_radios_placed_on_driver_lap(radios, laps, lapstarts, results):
    laps = laps.merge(lapstarts, on=["Driver", "LapNumber"])
    offset = RACE_START - laps.loc[laps["LapNumber"] == 1, "LapStartTime"].min()
    out = compute_radios(radios, laps, compute_results(results), offset)
    # Only the fixture drivers are known: other drivers' radios are dropped.
    assert {r["drv"] for r in out} == {"RUS", "NOR"}
    rus = [r for r in out if r["drv"] == "RUS"]
    assert [r["at"] for r in rus] == ["11:48:35", "12:30:46", "12:43:28", "12:45:31"]
    assert 20 <= rus[0]["lap"] <= 30  # about 45 minutes after the start
    assert rus[-1]["lap"] == 51  # after the chequered flag, still on his last lap
    assert rus[0]["url"].endswith(".mp3")


def test_radios_without_lap_start_times(radios, laps, lapstarts, results):
    # Canada 2026: no LapStartTime at all. Lap end times give the same laps.
    laps = laps.merge(lapstarts, on=["Driver", "LapNumber"])
    offset = RACE_START - laps.loc[laps["LapNumber"] == 1, "LapStartTime"].min()
    expected = compute_radios(radios, laps, compute_results(results), offset)
    blank = laps.assign(LapStartTime=pd.NaT)
    assert compute_radios(radios, blank, compute_results(results), offset) == expected


def test_radios_without_clock_have_no_lap(radios, laps, lapstarts, results):
    laps = laps.merge(lapstarts, on=["Driver", "LapNumber"])
    out = compute_radios(radios, laps, compute_results(results), None)
    assert out and all(r["lap"] is None for r in out)


def test_match_highlights():
    titles = {
        "AAA": "Top 10 Onboards | 2026 Bahrain Grand Prix",
        "BBB": "Race Highlights | 2026 Bahrain Grand Prix in Malaysia",
        "CCC": "Race Highlights | 2025 Bahrain Grand Prix",
    }
    feed = "".join(
        f"<entry><yt:videoId>{v}</yt:videoId><title>{t}</title></entry>" for v, t in titles.items()
    )
    assert match_highlights(feed, 2026, "Bahrain Grand Prix") == "BBB"
    assert match_highlights(feed, 2026, "Monaco Grand Prix") is None


def test_lap_matrix(laps):
    out = compute_lap_matrix(laps)
    assert out["laps"] == 51 and len(out["t"]["ANT"]) == 52
    assert out["f"]["ANT"][30] == "p" and out["f"]["ANT"][31] == "p"  # in-lap, out-lap
    assert out["f"]["ANT"][33] == "n" and out["f"]["ANT"][45] == ""  # safety car, clean
    assert 100 < out["t"]["ANT"][45] < 115


def test_race_trace(laps, lapstarts):
    laps = laps.merge(lapstarts, on=["Driver", "LapNumber"])
    out = compute_race_trace(laps)
    rus, ant = out["trace"]["RUS"], out["trace"]["ANT"]
    assert rus[0] == 0 and ant[0] == 0
    assert rus[51] > ant[51]  # the winner ends above the others
    # The safety car (laps 31-38) bunches the field up: the leader's margin shrinks.
    assert rus[38] - ant[38] < rus[30] - ant[30]
    # Missing lap start times: same trace from line crossings.
    blank = compute_race_trace(laps.assign(LapStartTime=pd.NaT))
    assert abs(blank["trace"]["RUS"][51] - rus[51]) < 2


def test_weather_on_lap_axis(weather, full_laps):
    out = compute_weather(weather, full_laps)
    assert len(out["lap"]) == len(out["air"]) == len(out["rain"]) > 50
    assert out["lap"][0] >= 0 and out["lap"][-1] <= 51
    assert out["lap"] == sorted(out["lap"])  # time goes forward
    assert not any(out["rain"])  # dry race in Baku
    assert 20 < out["air"][0] < 35 and out["track"][0] > out["air"][0]


def test_degradation(full_laps):
    stints = {(s["drv"], s["stint"]): s for s in compute_degradation(full_laps)}
    ant = stints[("ANT", 1)]  # 30 laps on mediums
    assert (ant["cmp"], ant["from"], ant["to"]) == ("MEDIUM", 1, 30)
    assert ant["n"] >= 20 and -0.2 < ant["deg"] < 0.3  # tenths of a second per lap at most
    # NOR stint 2 (laps 31-36) is all safety car: no clean laps, no slope.
    assert ("NOR", 2) not in stints
    assert FUEL_GAIN > 0


def test_degradation_fuel_correction(full_laps):
    # Lap times getting faster by exactly the fuel effect: no tyre wear at all.
    flat = full_laps[(full_laps["Driver"] == "ANT") & (full_laps["Stint"] == 1)].copy()
    flat["LapTime"] = pd.to_timedelta(100 - FUEL_GAIN * flat["LapNumber"], unit="s")
    flat["TyreLife"] = flat["LapNumber"] + 2
    assert abs(compute_degradation(flat)[0]["deg"]) < 1e-6


def test_speeds(full_laps):
    out = compute_speeds(full_laps)
    rus = out["RUS"]
    assert rus["best"] == 104.916 and rus["top"] > 300
    assert rus["ideal"] <= rus["best"]  # best sectors never add up to more than the best lap
    assert len(rus["s"]) == 3 and abs(sum(rus["s"]) - rus["ideal"]) < 0.002
