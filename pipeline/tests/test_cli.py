from datetime import date

import pandas as pd
import pytest

from pipeline.cli import latest_round, parse_args


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
