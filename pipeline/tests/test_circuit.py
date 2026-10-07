import numpy as np
import pandas as pd

from pipeline.compute.circuit import (
    WIDTH,
    Frame,
    compute_circuit,
    compute_replay,
    leaders_at,
    safety_car_track,
    sc_periods,
)

# A 2000 x 1000 rectangle lap, counter-clockwise, sampled every 10 units.
SIDE = [np.linspace(0, 1, 200, endpoint=False)]
XS = np.concatenate([SIDE[0] * 2000, np.full(100, 2000), (1 - SIDE[0]) * 2000, np.zeros(100)])
YS = np.concatenate(
    [np.zeros(200), np.linspace(0, 1000, 100), np.full(200, 1000), np.linspace(1000, 0, 100)]
)
LAP = pd.DataFrame({"X": XS, "Y": YS})
CORNERS = pd.DataFrame({"X": [2000.0], "Y": [0.0], "Number": [1], "Letter": [""]})


def test_frame_fits_width_and_keeps_aspect():
    frame = Frame(XS, YS, rotation_deg=0)
    out = compute_circuit(LAP, CORNERS, frame)
    xs = [p[0] for p in out["path"]]
    ys = [p[1] for p in out["path"]]
    assert 0 <= min(xs) and max(xs) <= WIDTH and out["w"] == WIDTH
    assert abs((max(xs) - min(xs)) / (max(ys) - min(ys)) - 2) < 0.02  # still twice as wide
    # SVG y goes down: the corner at (2000, 0) is at the bottom right.
    assert out["corners"] == [{"n": "1", "x": max(xs), "y": max(ys)}]


def test_frame_rotation():
    upright = compute_circuit(LAP, CORNERS, Frame(XS, YS, rotation_deg=90))
    xs = [p[0] for p in upright["path"]]
    ys = [p[1] for p in upright["path"]]
    assert (max(ys) - min(ys)) > 1.9 * (max(xs) - min(xs))  # now twice as tall
    assert upright["h"] > upright["w"]


def test_replay_resamples_and_hides_after_last_lap():
    frame = Frame(XS, YS, rotation_deg=0)
    # One car driving the lap in 100 s, then sitting still until t = 200 s.
    t = np.concatenate([np.linspace(0, 100, len(XS)), [200.0]])
    pos = pd.DataFrame({"SessionTime": pd.to_timedelta(t, unit="s"), "X": [*XS, 0], "Y": [*YS, 0]})
    out = compute_replay({"RUS": pos}, {"RUS": 100.0}, t_from=0, t_to=150, frame=frame, step=10)
    cars = out["cars"]["RUS"]
    assert out["n"] == 15 and len(cars) == 30
    assert cars[0:2] == [frame.apply(0, 0)[0], frame.apply(0, 0)[1]]  # start of the lap
    assert cars[22:24] == [None, None]  # t = 110 s: more than 5 s after the last lap


def test_sc_periods():
    status = pd.DataFrame(
        {
            "Time": pd.to_timedelta([0, 100, 160, 300, 400], unit="s"),
            "Status": ["1", "4", "1", "4", "1"],
        }
    )
    assert sc_periods(status) == [(100.0, 160.0), (300.0, 400.0)]
    assert sc_periods(status.iloc[:4])[-1][1] == float("inf")  # still out at the end


def test_leaders_at():
    laps = pd.DataFrame(
        {
            "Driver": ["RUS", "ANT", "RUS", "ANT"],
            "Position": [1, 2, 2, 1],
            "Time": pd.to_timedelta([100, 101, 201, 200], unit="s"),
        }
    )
    assert leaders_at(laps, np.array([50, 150, 250])) == [None, "RUS", "ANT"]


def test_safety_car_ahead_of_leader_only_during_periods():
    square = [[0, 0], [100, 0], [100, 100], [0, 100]]  # 400 units around
    cars = {"RUS": [0, 0, 0, 0]}  # leader parked at the first corner, two frames
    grid = np.array([10.0, 20.0])
    out = safety_car_track(square, cars, ["RUS", "RUS"], grid, [(15, 30)], ahead=150)
    assert out[:2] == [None, None]  # t = 10: no safety car yet
    assert out[2:] == [100, 50]  # 150 units ahead along the loop
