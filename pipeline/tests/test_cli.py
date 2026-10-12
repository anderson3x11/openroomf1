from datetime import date

import pandas as pd
import pytest

from pipeline.cli import event_sessions, latest_round, parse_args


def test_run_args():
    args = parse_args(["run", "--season", "2026", "--round", "18"])
    assert (args.command, args.season, args.round, args.latest) == ("run", 2026, 18, False)


def test_run_latest_args():
    args = parse_args(["run", "--season", "2026", "--latest"])
    assert args.latest and args.round is None
    with pytest.raises(SystemExit):  # one or the other, not both
        parse_args(["run", "--season", "2026", "--round", "3", "--latest"])


def test_latest_round():
    schedule = pd.DataFrame(
        {
            "RoundNumber": [1, 2, 3],
            "EventDate": pd.to_datetime(["2026-03-08", "2026-03-15", "2026-03-29"]),
        }
    )
    assert latest_round(schedule, date(2026, 3, 1)) is None
    assert latest_round(schedule, date(2026, 3, 15)) == 2  # race day itself counts
    assert latest_round(schedule, date(2026, 12, 1)) == 3


def test_event_sessions():
    sprint = {"Session1": "Practice 1", "Session2": "Sprint Qualifying", "Session3": "Sprint"}
    sprint |= {"Session4": "Qualifying", "Session5": "Race"}
    assert [f for f, _ in event_sessions(pd.Series(sprint))] == [
        "fp1",
        "sprint-quali",
        "sprint",
        "quali",
        "race",
    ]
    classic = {f"Session{i}": f"Practice {i}" for i in (1, 2, 3)}
    classic |= {"Session4": "Qualifying", "Session5": "Race"}
    assert [f for f, _ in event_sessions(pd.Series(classic))] == [
        "fp1",
        "fp2",
        "fp3",
        "quali",
        "race",
    ]
