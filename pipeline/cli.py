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
from pipeline.compute.radios import compute_radios, session_to_utc
from pipeline.compute.results import compute_results
from pipeline.compute.speeds import compute_speeds
from pipeline.compute.standings import compute_standings
from pipeline.compute.strategy import compute_strategy
from pipeline.compute.summary import fastest_lap
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


def run(args: argparse.Namespace) -> None:
    # Imported here so the CLI and its tests do not pay for the FastF1 import.
    from pipeline.fetch.fastf1_source import load_race, purge_cache
    from pipeline.fetch.jolpica import FLAGS, load_circuit, load_standings
    from pipeline.fetch.livetiming import load_feed
    from pipeline.fetch.logos import fetch_logos
    from pipeline.fetch.openf1 import load_team_radio
    from pipeline.fetch.youtube import fetch_thumbnail, find_highlights

    if args.latest:
        import fastf1

        schedule = fastf1.get_event_schedule(args.season, include_testing=False)
        args.round = latest_round(schedule, date.today())
        if args.round is None:
            print(f"No {args.season} race held yet")
            return
        print(f"Latest race: {args.season} round {args.round}")

    session = load_race(args.season, args.round, args.cache_dir)
    event = session.event
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
        "sessions": ["race"],
        **load_circuit(args.season, args.round),
        "highlights": find_highlights(args.season, args.round, event["EventName"]),
    }
    results = compute_results(session.results)
    fetch_logos(
        args.season, {r["tid"] for r in results}, args.data_dir / str(args.season) / "logos"
    )
    laps = session.laps
    neutral = neutralized_laps(laps)  # timeline only, read on the leader's laps
    standings = load_standings(args.season, args.round)
    messages = session.race_control_messages
    radios = load_team_radio(args.season, session.date.date())
    overtakes = compute_overtakes(load_feed(session.api_path, "OvertakeSeries"), results)
    pit_feed = load_feed(session.api_path, "PitStopSeries")
    circuit, replay = circuit_and_replay(session, results)
    # t0_date (exact, needs telemetry) turns session time into UTC; race control as a fallback.
    clock = session.t0_date if session.t0_date is not None else session_to_utc(messages, laps)
    radio_list = compute_radios(radios, laps, results, clock)
    gp_dir = write_gp(
        args.data_dir,
        meta,
        {
            "race/results.json": results,
            "race/positions.json": compute_positions(laps, session.results),
            "race/gaps.json": compute_gaps(laps),
            "race/strategy.json": compute_strategy(laps),
            "race/pitstops.json": compute_pitstops(laps, pit_feed, results),
            "race/summary.json": {"fastest": fastest_lap(laps), "overtakes": overtakes},
            "race/circuit.json": circuit,
            "race/replay.json": replay,
            "race/laptimes.json": compute_laptimes(laps),
            "race/laps.json": compute_lap_matrix(laps),
            "race/racetrace.json": compute_race_trace(laps),
            "race/degradation.json": compute_degradation(laps),
            "race/speeds.json": compute_speeds(laps),
            "race/weather.json": compute_weather(session.weather_data, laps),
            "race/events.json": compute_events(messages, neutral),
            "race/radios.json": radio_list,
            "race/standings.json": compute_standings(**standings, results=results),
        },
    )

    if meta["highlights"]:
        fetch_thumbnail(meta["highlights"], gp_dir / "thumb.jpg")

    size_mb = dir_size(gp_dir) / 1e6
    print(f"{gp_dir}: {size_mb:.2f} MB (budget {BUDGET_MB} MB)")
    if size_mb > BUDGET_MB:
        print("WARNING: over budget, review resampling")
    if not args.keep_cache:
        purge_cache(args.cache_dir)


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
    rotation = info.rotation if info is not None else 0.0
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
