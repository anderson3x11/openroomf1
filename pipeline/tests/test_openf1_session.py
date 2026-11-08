import pandas as pd

from pipeline.fetch.openf1_session import (
    laps_frame,
    messages_frame,
    neutral_intervals,
    qualifying_parts,
    results_frame,
    telemetry_frame,
)

T0 = pd.Timestamp("2026-10-11 12:00:00")
DRIVERS = {
    1: {
        "name_acronym": "NOR",
        "team_name": "McLaren",
        "team_colour": "F47600",
        "first_name": "Lando",
        "last_name": "Norris",
    }
}


def at(seconds: float) -> str:
    return (T0 + pd.to_timedelta(seconds, unit="s")).isoformat() + "+00:00"


def msg(seconds, message, category="Other", flag=None, scope=None, lap=1, phase=None):
    return {
        "date": at(seconds),
        "message": message,
        "category": category,
        "flag": flag,
        "scope": scope,
        "lap_number": lap,
        "qualifying_phase": phase,
    }


def lap(n, start, duration, out=False):
    return {
        "driver_number": 1,
        "lap_number": n,
        "date_start": at(start),
        "lap_duration": duration,
        "duration_sector_1": None,
        "duration_sector_2": None,
        "duration_sector_3": None,
        "st_speed": 300,
        "is_pit_out_lap": out,
    }


def test_neutral_intervals():
    messages = messages_frame(
        [
            msg(100, "VSC DEPLOYED", "SafetyCar"),
            msg(160, "VSC ENDING", "SafetyCar"),
            msg(300, "SAFETY CAR DEPLOYED", "SafetyCar"),
            msg(500, "SAFETY CAR IN THIS LAP", "SafetyCar"),
            msg(700, "RED FLAG", "Flag", flag="RED", scope="Track"),
            msg(900, "GREEN LIGHT - PIT EXIT OPEN", "Flag", flag="GREEN", scope="Track"),
        ]
    )
    lap_ends = T0 + pd.to_timedelta(pd.Series([450, 590, 680]), unit="s")
    spans = [
        ((a - T0).total_seconds(), (b - T0).total_seconds(), c)
        for a, b, c in neutral_intervals(messages, lap_ends)
    ]
    # The safety car leaves when the leader next crosses the line after "IN THIS LAP".
    # The VSC ends 15 s after "VSC ENDING", when the track turns green.
    assert spans == [(100, 175, "6"), (300, 590, "4"), (700, 900, "5")]


def test_laps_frame():
    laps = [
        lap(1, 0, None),
        lap(2, 100, 95),
        lap(3, 195, 120),
        lap(4, 315, 400, out=True),
        lap(5, 410, 94),
    ]
    stints = [
        {
            "driver_number": 1,
            "stint_number": 1,
            "lap_start": 1,
            "lap_end": 3,
            "compound": "MEDIUM",
            "tyre_age_at_start": 2,
        },
        {
            "driver_number": 1,
            "stint_number": 2,
            "lap_start": 4,
            "lap_end": 5,
            "compound": "HARD",
            "tyre_age_at_start": 0,
        },
    ]
    pits = [{"driver_number": 1, "lap_number": 3, "date": at(300), "lane_duration": 21.5}]
    positions = [
        {"driver_number": 1, "date": at(0), "position": 3},
        {"driver_number": 1, "date": at(250), "position": 5},
    ]
    messages = messages_frame(
        [
            msg(150, "VSC DEPLOYED", "SafetyCar"),
            msg(170, "VSC ENDING", "SafetyCar"),
            msg(400, "CAR 1 (NOR) TIME 1:34.000 DELETED - TRACK LIMITS AT TURN 2 LAP 5 12:08:24"),
        ]
    )
    df = laps_frame(laps, DRIVERS, stints, pits, positions, messages, T0).set_index("LapNumber")

    assert df.loc[1, "Time"] == pd.to_timedelta(100, unit="s")  # lap end = next lap start
    # Out lap: its OpenF1 duration counts the garage, the time to the next lap start is kept.
    assert df.loc[4, "LapTime"] == pd.to_timedelta(95, unit="s")
    assert df.loc[3, "PitInTime"] == pd.to_timedelta(300, unit="s")
    assert df.loc[4, "PitOutTime"] == pd.to_timedelta(321.5, unit="s")  # entry + time in the lane
    assert (df.loc[2, "Compound"], df.loc[2, "TyreLife"], df.loc[2, "FreshTyre"]) == (
        "MEDIUM",
        4,
        False,
    )
    assert (df.loc[4, "Stint"], df.loc[4, "FreshTyre"]) == (2, True)
    assert list(df["Position"]) == [3, 3, 5, 5, 5]
    assert df.loc[2, "TrackStatus"] == "6" and df.loc[3, "TrackStatus"] == "1"
    assert df.loc[5, "Deleted"] and not df.loc[2, "Deleted"]


def test_lap_skipped_by_openf1_comes_back_empty():
    laps = [lap(1, 0, 90), lap(2, 90, 90), lap(4, 270, 90), lap(5, 360, 90)]
    positions = [
        {"driver_number": 1, "date": at(0), "position": 3},
        {"driver_number": 1, "date": at(200), "position": 2},
    ]
    df = laps_frame(laps, DRIVERS, [], [], positions, messages_frame([]), T0).set_index("LapNumber")

    assert list(df.index) == [1, 2, 3, 4, 5]
    assert df.loc[2, "Time"] == pd.to_timedelta(180, unit="s")
    assert df.loc[3, "Time"] == pd.to_timedelta(270, unit="s")
    assert pd.isna(df.loc[3, "LapTime"])  # never invented
    assert df.loc[3, "Position"] == 2


def test_lap_nobody_completes_is_dropped():
    # Brazil 2026: OpenF1 opened lap 72 for the winner, his cool-down lap after the flag.
    laps = [lap(1, 0, 90), lap(2, 90, 90), lap(3, 180, None)]
    df = laps_frame(laps, DRIVERS, [], [], [], messages_frame([]), T0)
    assert list(df["LapNumber"]) == [1, 2]


def test_qualifying_parts():
    laps = pd.DataFrame({"Time": pd.to_timedelta([100, 1200, 1300, 2500], unit="s")})
    messages = messages_frame(
        [
            msg(0, "SESSION STARTED", "SessionStatus", phase=1),
            msg(1080, "SESSION FINISHED", "SessionStatus", phase=1),
            msg(1500, "SESSION STARTED", "SessionStatus", phase=2),
            msg(2400, "SESSION STARTED", "SessionStatus", phase=3),
        ]
    )
    q1, q2, q3 = qualifying_parts(laps, messages, T0)
    # A lap belongs to the phase running when it ends: the in-laps after Q1 stay in Q1.
    assert (len(q1), len(q2), len(q3)) == (3, 0, 1)


def test_telemetry_frame():
    car = [
        {
            "date": at(t),
            "speed": 180,
            "throttle": 100,
            "brake": 0,
            "n_gear": 7,
            "rpm": 11000,
            "drs": None,
        }
        for t in range(0, 11)
    ]
    car[5]["brake"] = 100
    loc = [{"date": at(t), "x": t * 50, "y": 0} for t in range(0, 11)]
    tel = telemetry_frame(car, loc, T0)
    assert round(tel["Distance"].iloc[-1]) == 500  # 180 km/h for 10 s
    assert tel["Brake"].tolist().count(True) == 1 and tel["DRS"].max() == 0
    assert tel["X"].iloc[4] == 200


def test_results_without_jolpica():
    result = [
        {"driver_number": 1, "position": None, "points": 0, "dnf": True, "dns": False, "dsq": False}
    ]
    row = results_frame(DRIVERS, result, None).iloc[0]
    assert (row["Abbreviation"], row["FullName"], row["ClassifiedPosition"]) == (
        "NOR",
        "Lando Norris",
        "R",
    )


def test_stints_follow_pit_exits_not_openf1_ranges():
    """Singapore 2026, ALO: OpenF1 gave "SOFT laps 1-1, MEDIUM laps 2-61", he pitted on 35."""
    laps = [
        lap(1, 0, None),
        lap(2, 100, 95),
        lap(3, 195, 96),
        lap(4, 291, 110, out=True),
        lap(5, 401, 95),
    ]
    stints = [
        {
            "driver_number": 1,
            "stint_number": 1,
            "lap_start": 1,
            "lap_end": 1,
            "compound": "SOFT",
            "tyre_age_at_start": 0,
        },
        {
            "driver_number": 1,
            "stint_number": 2,
            "lap_start": 2,
            "lap_end": 4,
            "compound": "MEDIUM",
            "tyre_age_at_start": 3,
        },
    ]
    pits = [{"driver_number": 1, "lap_number": 3, "date": at(280), "lane_duration": 20}]
    df = laps_frame(laps, DRIVERS, stints, pits, [], messages_frame([]), T0)
    assert df["Compound"].tolist() == ["SOFT", "SOFT", "SOFT", "MEDIUM", "MEDIUM"]
    assert df["Stint"].tolist() == [1, 1, 1, 2, 2]  # the last lap is not left out
    assert df["TyreLife"].tolist() == [1, 2, 3, 4, 5]  # used mediums, 3 laps old


def test_deleted_lap_matched_on_its_time():
    """Singapore 2026 qualifying: "CAR 12 (ANT) TIME 1:32.818 DELETED ... LAP 8" is OpenF1's
    lap 9. The time identifies the lap, not the number."""
    laps = [lap(8, 0, 120.5), lap(9, 120.5, 92.818), lap(10, 213.318, 140)]
    messages = messages_frame(
        [
            msg(300, "CAR 1 (NOR) TIME 1:32.818 DELETED - TRACK LIMITS AT TURN 2 LAP 8 21:42:03"),
        ]
    )
    df = laps_frame(laps, DRIVERS, [], [], [], messages, T0)
    assert df["Deleted"].tolist() == [False, True, False]


def test_red_flag_from_session_aborted():
    """Mexico 2026: safety car, then the race stopped ("SESSION ABORTED", no RED flag), restart,
    and a second safety car later. The first one must end at the red flag."""
    messages = messages_frame(
        [
            msg(100, "SAFETY CAR DEPLOYED", "SafetyCar"),
            msg(200, "SESSION ABORTED", "SessionStatus"),
            msg(2500, "SESSION STARTED", "SessionStatus"),
            msg(3500, "SAFETY CAR DEPLOYED", "SafetyCar"),
            msg(3800, "SAFETY CAR IN THIS LAP", "SafetyCar"),
        ]
    )
    lap_ends = T0 + pd.to_timedelta(pd.Series([3850, 3900]), unit="s")
    spans = [
        ((a - T0).total_seconds(), (b - T0).total_seconds(), c)
        for a, b, c in neutral_intervals(messages, lap_ends)
    ]
    assert spans == [(100, 200, "4"), (200, 2500, "5"), (3500, 3850, "4")]


def test_results_follow_jolpica_order_when_it_has_the_race():
    """Mexico 2026: OpenF1 and Jolpica disagreed after the race, the order must not mix them."""
    drivers = {1: DRIVERS[1], 2: {**DRIVERS[1], "name_acronym": "PIA"}}
    result = [{"driver_number": 1, "position": 1}, {"driver_number": 2, "position": 2}]
    official = pd.DataFrame(
        [
            {
                "number": 1,
                "position": 2,
                "positionText": "2",
                "grid": 1,
                "status": "Finished",
                "points": 18,
            },
            {
                "number": 2,
                "position": 1,
                "positionText": "1",
                "grid": 2,
                "status": "Finished",
                "points": 25,
            },
        ]
    )
    rows = results_frame(drivers, result, official).sort_values("Position")
    assert rows["Abbreviation"].tolist() == ["PIA", "NOR"]
    assert rows["ClassifiedPosition"].tolist() == ["1", "2"]
