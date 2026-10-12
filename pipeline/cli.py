"""Pipeline entry point: `python -m pipeline run --season 2026 --round 15`."""

import argparse
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from pipeline.compute.circuit import (
    Frame,
    compute_circuit,
    compute_replay,
    leaders_at,
    safety_car_track,
    sc_periods,
)
from pipeline.compute.degradation import compute_degradation
from pipeline.compute.events import compute_events
from pipeline.compute.gaps import compute_gaps
from pipeline.compute.laps import compute_lap_matrix, compute_race_trace
from pipeline.compute.laptimes import compute_laptimes
from pipeline.compute.overtakes import compute_overtakes
from pipeline.compute.pitstops import compute_pitstops
from pipeline.compute.positions import compute_positions
from pipeline.compute.quali import compute_quali, compute_quali_laps
from pipeline.compute.radios import compute_radios, session_to_utc
from pipeline.compute.results import compute_results
from pipeline.compute.speeds import compute_speeds
from pipeline.compute.standings import compute_standings
from pipeline.compute.strategy import compute_strategy
from pipeline.compute.summary import fastest_lap
from pipeline.compute.telemetry import best_laps, compute_telemetry
from pipeline.compute.track import neutralized_laps
from pipeline.compute.weather import compute_weather
from pipeline.export.writer import dir_size, slugify, write_gp

ROOT = Path(__file__).resolve().parent.parent
BUDGET_MB = 30


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="pipeline")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="Fetch, compute and export one Grand Prix")
    run.add_argument("--season", type=int, required=True)
    which = run.add_mutually_exclusive_group(required=True)
    which.add_argument("--round", type=int)
    which.add_argument(
        "--latest", action="store_true", help="Most recent race already held (for the cron job)"
    )
    run.add_argument("--data-dir", type=Path, default=ROOT / "data")
    run.add_argument("--cache-dir", type=Path, default=ROOT / "cache")
    run.add_argument("--keep-cache", action="store_true", help="Do not purge the FastF1 cache")
    return parser.parse_args(argv)


def latest_round(schedule: pd.DataFrame, today: date) -> int | None:
    """Round of the most recent race held on or before `today` (event date = race day)."""
    held = schedule[schedule["EventDate"].dt.date <= today]
    return None if held.empty else int(held["RoundNumber"].max())


# FastF1 session name -> data folder and URL segment, in weekend order.
SESSIONS = {
    "Practice 1": "fp1",
    "Practice 2": "fp2",
    "Practice 3": "fp3",
    "Sprint Qualifying": "sprint-quali",
    "Sprint Shootout": "sprint-quali",  # 2023 name of the sprint qualifying
    "Sprint": "sprint",
    "Qualifying": "quali",
    "Race": "race",
}


def event_sessions(event) -> list[tuple[str, str]]:
    """(folder, FastF1 name) of the sessions we export, in the order they were held."""
    names = [event.get(f"Session{i}") for i in range(1, 6)]
    return [(SESSIONS[n], n) for n in names if n in SESSIONS]


def run(args: argparse.Namespace) -> None:
    # Imported here so the CLI and its tests do not pay for the FastF1 import.
    from pipeline.fetch.fastf1_source import load_session, purge_cache
    from pipeline.fetch.jolpica import FLAGS, load_circuit, load_standings
    from pipeline.fetch.logos import fetch_logos
    from pipeline.fetch.youtube import fetch_thumbnail, find_highlights

    if args.latest:
        import fastf1

        schedule = fastf1.get_event_schedule(args.season, include_testing=False)
        args.round = latest_round(schedule, date.today())
        if args.round is None:
            print(f"No {args.season} race held yet")
            return
        print(f"Latest race: {args.season} round {args.round}")

    # The race is required: without it nothing is written. Other sessions are a bonus.
    race = load_session(args.season, args.round, "Race", args.cache_dir)
    event = race.event
    results = compute_results(race.results)
    fetch_logos(
        args.season, {r["tid"] for r in results}, args.data_dir / str(args.season) / "logos"
    )
    standings = load_standings(args.season, args.round)
    files = race_files(race, "race", args.season, standings)
    done = {"race"}
    for folder, name in event_sessions(event):
        if folder == "race":
            continue
        try:
            session = load_session(args.season, args.round, name, args.cache_dir)
            if folder == "sprint":
                files |= race_files(session, folder, args.season)
            else:
                files |= quali_files(session, folder)
            done.add(folder)
        except Exception as e:  # FastF1 raises many kinds, and the race must not wait on them
            print(f"WARNING: {name} skipped: {e!r}")

    meta = {
        "season": args.season,
        "round": args.round,
        "slug": f"{args.round:02d}-{slugify(event['EventName'])}",
        "name": event["EventName"],
        "official": event["OfficialEventName"],
        "country": event["Country"],
        # Flag of the Grand Prix country: the 2026 Bahrain GP in Malaysia keeps the Bahrain flag.
        "flag": FLAGS.get(event["Country"]),
        "location": event["Location"],
        "date": event["EventDate"].strftime("%Y-%m-%d"),
        "sessions": [f for f, _ in event_sessions(event) if f in done],
        **load_circuit(args.season, args.round),
        "highlights": find_highlights(args.season, args.round, event["EventName"]),
    }
    gp_dir = write_gp(args.data_dir, meta, files)

    if meta["highlights"]:
        fetch_thumbnail(meta["highlights"], gp_dir / "thumb.jpg")

    size_mb = dir_size(gp_dir) / 1e6
    print(f"{gp_dir}: {size_mb:.2f} MB (budget {BUDGET_MB} MB)")
    if size_mb > BUDGET_MB:
        print("WARNING: over budget, review resampling")
    if not args.keep_cache:
        purge_cache(args.cache_dir)


def race_files(session, folder: str, season: int, standings: dict | None = None) -> dict:
    """Files of a race or a sprint, under FOLDER/. Standings only after the race."""
    from pipeline.fetch.livetiming import load_feed
    from pipeline.fetch.openf1 import load_team_radio

    results = compute_results(session.results)
    laps = session.laps
    neutral = neutralized_laps(laps)  # timeline only, read on the leader's laps
    messages = session.race_control_messages
    radios = load_team_radio(season, session.date.date(), session.name)
    overtakes = compute_overtakes(load_feed(session.api_path, "OvertakeSeries"), results)
    pit_feed = load_feed(session.api_path, "PitStopSeries")
    circuit, replay = circuit_and_replay(session, results)
    # t0_date (exact, needs telemetry) turns session time into UTC; race control as a fallback.
    clock = session.t0_date if session.t0_date is not None else session_to_utc(messages, laps)
    files = {
        "results": results,
        "positions": compute_positions(laps, session.results),
        "gaps": compute_gaps(laps),
        "strategy": compute_strategy(laps),
        "pitstops": compute_pitstops(laps, pit_feed, results),
        "summary": {"fastest": fastest_lap(laps), "overtakes": overtakes},
        "circuit": circuit,
        "replay": replay,
        "laptimes": compute_laptimes(laps),
        "laps": compute_lap_matrix(laps),
        "racetrace": compute_race_trace(laps),
        "degradation": compute_degradation(laps),
        "speeds": compute_speeds(laps),
        "weather": compute_weather(session.weather_data, laps),
        "events": compute_events(messages, neutral),
        "radios": compute_radios(radios, laps, results, clock),
    }
    if standings:
        files["standings"] = compute_standings(**standings, results=results)
    files["telemetry"] = telemetry_of(session)
    return {f"{folder}/{name}.json": obj for name, obj in files.items()}


def quali_files(session, folder: str) -> dict:
    """Files of a qualifying, a sprint qualifying or a free practice, under FOLDER/. Practice
    is one segment: its classification is the best lap of each driver."""
    laps = session.laps
    parts = [laps] if folder.startswith("fp") else list(laps.split_qualifying_sessions())
    return {
        f"{folder}/results.json": compute_quali(parts, session.results),
        f"{folder}/laps.json": compute_quali_laps(parts),
        f"{folder}/speeds.json": compute_speeds(laps),
        f"{folder}/telemetry.json": telemetry_of(session),
    }


def rotation_of(session) -> float:
    """Rotation that matches the official track map, 0 when FastF1 does not know the circuit."""
    try:
        return session.get_circuit_info().rotation
    except AttributeError:  # unknown circuit (Madrid 2026): FastF1 fails internally
        return 0.0


def telemetry_of(session) -> dict | None:
    """Best lap telemetry of every driver; None when the session has no car data."""
    tel, info = {}, {}
    for lap in best_laps(session.laps).itertuples():
        try:
            data = session.laps.loc[lap.Index].get_telemetry()
        except (KeyError, ValueError) as e:
            print(f"WARNING: no telemetry for {lap.Driver}: {e!r}")
            continue
        if len(data) < 100:
            continue
        tel[lap.Driver] = data
        info[lap.Driver] = {
            "lap": int(lap.LapNumber),
            "time": round(lap.LapTime.total_seconds(), 3),
            "cmp": lap.Compound if isinstance(lap.Compound, str) else "UNKNOWN",
        }
    return compute_telemetry(tel, info, rotation_of(session)) if tel else None


def outline_lap_pos(laps):
    """Position data of the fastest lap that has some: FastF1 misses it on a few laps."""
    ranked = laps.dropna(subset=["LapTime"]).sort_values("LapTime")
    for i in range(min(20, len(ranked))):
        try:
            pos = ranked.iloc[i].get_pos_data()
        except (KeyError, ValueError):
            continue
        if len(pos) > 100:
            return pos
    raise ValueError("no lap with position data")


def circuit_and_replay(session, results: list[dict]) -> tuple[dict | None, dict | None]:
    """Outline from the fastest lap, replay of every car in the same frame.
    Both None when position data is unusable: the rest of the GP is still exported."""
    try:
        return _circuit_and_replay(session, results)
    except (KeyError, ValueError) as e:
        print(f"WARNING: no circuit outline nor replay: {e!r}")
        return None, None


def _circuit_and_replay(session, results: list[dict]) -> tuple[dict, dict]:
    laps = session.laps
    lap_pos = outline_lap_pos(laps)
    try:
        info = session.get_circuit_info()
    except AttributeError:  # unknown circuit for FastF1 (Madrid 2026): FastF1 fails internally
        info = None
    rotation = rotation_of(session)
    corners = (
        info.corners if info is not None else pd.DataFrame(columns=["X", "Y", "Number", "Letter"])
    )
    frame = Frame(lap_pos["X"].to_numpy(), lap_pos["Y"].to_numpy(), rotation)
    drv_by_number = {r["num"]: r["drv"] for r in results}
    pos = {drv_by_number[n]: p for n, p in session.pos_data.items() if n in drv_by_number}
    end_times = laps.groupby("Driver")["Time"].max().dt.total_seconds().to_dict()
    lap_ends = laps.groupby("LapNumber")["Time"].min().dt.total_seconds()
    lap1 = laps[laps["LapNumber"] == 1]
    start = lap1["LapStartTime"].min()
    if pd.isna(start):  # missing for whole races (Canada 2026): one lap before the first lap end
        start = lap1["Time"].min() - lap1["LapTime"].median()
    t_from = start.total_seconds() - 10
    replay = compute_replay(pos, end_times, t_from, lap_ends.max() + 30, frame)
    replay["laps"] = [round(t, 1) for t in lap_ends]  # session time when the leader ends each lap

    circuit = compute_circuit(lap_pos, corners, frame)
    grid = replay["t0"] + np.arange(replay["n"]) * replay["dt"]
    # FastF1 positions are in tenths of a metre: 300 m ahead of the leader.
    ahead = 300 * 10 * frame.scale
    replay["sc"] = safety_car_track(
        circuit["path"],
        replay["cars"],
        leaders_at(laps, grid),
        grid,
        sc_periods(session.track_status),
        ahead,
    )
    return circuit, replay


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    if args.command == "run":
        run(args)
