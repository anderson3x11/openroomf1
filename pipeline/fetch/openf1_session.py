"""A session rebuilt from OpenF1, in the shape FastF1 gave it: the compute modules read the
same columns (laps, results, race control, weather, track status, car positions, telemetry).

Session time is counted from the session start (OpenF1 date_start), in Timedelta like FastF1.
"""

import re

import numpy as np
import pandas as pd

from pipeline.fetch import openf1

# Track status codes, as in the F1 feed: safety car, red flag, virtual safety car.
SC, RED, VSC = "4", "5", "6"
VSC_GREEN_AFTER = pd.to_timedelta(15, unit="s")
# "CAR 12 (ANT) TIME 1:32.818 DELETED - TRACK LIMITS AT TURN 2 LAP 8 21:42:03", or
# "CAR 6 (HAD) LAP DELETED - TRACK LIMITS AT TURN 2 LAP 33 20:57:43". Same for REINSTATED.
LAP_VERDICT = re.compile(
    r"CAR (\d+) \([A-Z]{3}\) (?:TIME (\d+):([\d.]+) |LAP )(DELETED|REINSTATED)\b"
    r"(?:.*?\bLAP (\d+)\b)?"
)


def utc(values) -> pd.Series | pd.Timestamp:
    """OpenF1 ISO dates as naive UTC timestamps (a column or a single date)."""
    t = pd.to_datetime(values, utc=True, format="ISO8601")
    return t.dt.tz_convert(None) if isinstance(t, pd.Series) else t.tz_convert(None)


def seconds(values) -> pd.Series:
    return pd.to_timedelta(pd.to_numeric(values), unit="s")


def neutral_intervals(messages: pd.DataFrame, lap_ends: pd.Series) -> list[tuple]:
    """(start, end, code) in UTC of each safety car, VSC and red flag, from race control.
    lap_ends: UTC end of every lap, any driver: a safety car leaves at the first lap end
    after "SAFETY CAR IN THIS LAP" (the leader crossing the line)."""
    out, open_ = [], {}
    ends = np.sort(lap_ends.dropna().to_numpy())
    for m in messages.sort_values("Date").itertuples():
        msg = m.Message.upper()
        if m.Category == "SafetyCar" and ("VSC" in msg or "VIRTUAL SAFETY CAR" in msg):
            if "DEPLOYED" in msg:
                open_.setdefault(VSC, m.Date)
            elif "ENDING" in msg and VSC in open_:
                # The track turns green 10 to 15 s after "VSC ENDING"; the feed's exact time is
                # not in OpenF1. ponytail: fixed margin, read the track status if OpenF1 adds it.
                out.append((open_.pop(VSC), m.Date + VSC_GREEN_AFTER, VSC))
        elif m.Category == "SafetyCar" and "SAFETY CAR" in msg:
            if "DEPLOYED" in msg:
                open_.setdefault(SC, m.Date)
            elif "IN THIS LAP" in msg and SC in open_:
                later = ends[ends > np.datetime64(m.Date)]
                out.append((open_.pop(SC), pd.Timestamp(later[0]) if len(later) else m.Date, SC))
        elif m.Flag == "RED" and m.Scope == "Track":
            open_.setdefault(RED, m.Date)
        elif RED in open_ and (
            (m.Flag == "GREEN" and m.Scope == "Track") or "RESUMED" in msg or "STARTED" in msg
        ):
            out.append((open_.pop(RED), m.Date, RED))
    last = messages["Date"].max()
    out += [(start, last, code) for code, start in open_.items()]
    return sorted(out)


def laps_frame(
    laps: list[dict],
    drivers: dict[int, dict],
    stints: list[dict],
    pits: list[dict],
    positions: list[dict],
    messages: pd.DataFrame,
    t0: pd.Timestamp,
) -> pd.DataFrame:
    """FastF1 Laps columns from OpenF1 records. Lap end = start of the next lap when known: out
    lap durations include the time spent in the garage. pits: race and sprint only, in
    qualifying and practice OpenF1 puts its pit records on the out lap (garage exit)."""
    df = pd.DataFrame(laps)
    df = df[df["driver_number"].isin(drivers)].sort_values(["driver_number", "lap_number"])
    start = utc(df["date_start"])
    duration = seconds(df["lap_duration"])
    next_start = start.groupby(df["driver_number"]).shift(-1)
    end = next_start.where(next_start.notna(), start + duration)
    out = pd.DataFrame(
        {
            "Driver": df["driver_number"].map(lambda n: drivers[n]["name_acronym"]),
            "DriverNumber": df["driver_number"].astype(str),
            "Team": df["driver_number"].map(lambda n: drivers[n]["team_name"]),
            "LapNumber": df["lap_number"].astype(float),
            "LapStartTime": start - t0,
            "Time": end - t0,
            "LapTime": duration.where(
                ~df["is_pit_out_lap"].fillna(False).astype(bool), end - start
            ),
            "Sector1Time": seconds(df["duration_sector_1"]),
            "Sector2Time": seconds(df["duration_sector_2"]),
            "Sector3Time": seconds(df["duration_sector_3"]),
            "SpeedST": pd.to_numeric(df["st_speed"]),
            "IsPitOut": df["is_pit_out_lap"].fillna(False).astype(bool),
            "_end": end,
        }
    ).reset_index(drop=True)

    # Pit stops: entry time on the in-lap, exit on the next one (entry + time in the pit lane).
    out["PitInTime"] = pd.to_timedelta(pd.Series([pd.NaT] * len(out), dtype="object"))
    out["PitOutTime"] = out["PitInTime"].copy()
    key = {
        (n, lap): i
        for i, (n, lap) in enumerate(zip(out["DriverNumber"], out["LapNumber"], strict=True))
    }
    for p in pits:
        i = key.get((str(p["driver_number"]), float(p["lap_number"])))
        if i is None or not p.get("date"):
            continue
        entry = utc(p["date"]) - t0
        out.loc[i, "PitInTime"] = entry
        j = key.get((str(p["driver_number"]), float(p["lap_number"]) + 1))
        if j is not None and p.get("lane_duration") is not None:
            out.loc[j, "PitOutTime"] = entry + pd.to_timedelta(p["lane_duration"], unit="s")
    # Out laps without a pit record (qualifying, practice): leaving the garage.
    out_laps = out["IsPitOut"] & out["PitOutTime"].isna()
    out.loc[out_laps, "PitOutTime"] = out.loc[out_laps, "LapStartTime"]
    before_out = out["IsPitOut"].groupby(out["DriverNumber"]).shift(-1, fill_value=False)
    in_laps = before_out & out["PitInTime"].isna()
    out.loc[in_laps, "PitInTime"] = out.loc[in_laps, "Time"]

    # Tyres. OpenF1 numbers a new stint at each pit exit but its lap ranges are unreliable
    # (a stint "from lap 1 to 1" for a driver who pitted on lap 35, the last lap often left
    # out): the stint number comes from the pit exits, compound and age from OpenF1.
    # TyreLife counts the current lap, like FastF1.
    by_stint = {(str(s["driver_number"]), s["stint_number"]): s for s in stints}
    out_lap = out["IsPitOut"] | out["PitOutTime"].notna()
    stint_col, compound, life, fresh = [], [], [], []
    for _, grp in out.groupby("DriverNumber", sort=False):
        number, first, record = 0, None, None
        for i, row in grp.iterrows():
            if number == 0 or out_lap[i]:
                nxt = by_stint.get((row["DriverNumber"], number + 1))
                if nxt is not None or number == 0:  # no record: a drive-through, same tyres
                    number, first, record = number + 1, row["LapNumber"], nxt
            age = record.get("tyre_age_at_start") if record else None
            stint_col.append((i, number))
            compound.append((i, (record.get("compound") or "UNKNOWN").upper() if record else None))
            life.append((i, age + row["LapNumber"] - first + 1 if age is not None else np.nan))
            fresh.append((i, age == 0 if age is not None else None))
    out["Stint"] = pd.Series(dict(stint_col), dtype=float)
    out["Compound"] = pd.Series(dict(compound), dtype=object)
    out["TyreLife"] = pd.Series(dict(life), dtype=float)
    out["FreshTyre"] = pd.Series(dict(fresh), dtype=object)

    # Position at the end of each lap: the last change OpenF1 recorded before the line.
    out["Position"] = np.nan
    if positions:
        pos = pd.DataFrame(positions).assign(date=lambda d: utc(d["date"])).sort_values("date")
        for n, grp in pos.groupby("driver_number"):
            rows = out["DriverNumber"] == str(n)
            ends = out.loc[rows, "_end"].to_numpy()
            idx = (
                np.searchsorted(grp["date"].to_numpy(), ends + np.timedelta64(1, "s"), side="right")
                - 1
            )
            values = grp["position"].to_numpy()[np.clip(idx, 0, None)].astype(float)
            out.loc[rows, "Position"] = np.where((idx >= 0) & ~pd.isna(ends), values, np.nan)

    # Track status seen during each lap, like FastF1's TrackStatus string ("1", "16", ...).
    intervals = neutral_intervals(messages, out["_end"]) if not messages.empty else []
    lap_start = out["LapStartTime"] + t0

    def status(a, b):
        codes = [c for s, e, c in intervals if pd.notna(a) and pd.notna(b) and s < b and e > a]
        return "".join(sorted(set(codes))) or "1"

    out["TrackStatus"] = [status(a, b) for a, b in zip(lap_start, out["_end"], strict=True)]

    out["Deleted"] = deleted_laps(out, messages["Message"] if not messages.empty else [])
    return out.drop(columns=["_end", "IsPitOut"])


def deleted_laps(laps: pd.DataFrame, messages) -> pd.Series:
    """Laps deleted for track limits (and not reinstated). Matched on the lap time when the
    message gives it: in qualifying and practice, race control counts laps one apart from
    OpenF1. On the lap number otherwise."""
    deleted = pd.Series(False, index=laps.index)
    seconds = laps["LapTime"].dt.total_seconds()
    for msg in messages:
        m = LAP_VERDICT.search(msg)
        if not m:
            continue
        number, minutes, secs, verdict, lap = m.groups()
        rows = laps["DriverNumber"] == number
        if minutes is not None:
            rows &= (seconds - (int(minutes) * 60 + float(secs))).abs() < 0.0015
        elif lap is not None:
            rows &= laps["LapNumber"] == float(lap)
        else:
            continue
        deleted[rows] = verdict == "DELETED"
    return deleted


def track_status_frame(intervals: list[tuple], t0: pd.Timestamp) -> pd.DataFrame:
    """FastF1 track_status: (Time, Status) changes, "1" for a green track."""
    rows = [(pd.Timedelta(0), "1")]
    for start, end, code in intervals:
        rows += [(start - t0, code), (end - t0, "1")]
    return pd.DataFrame(rows, columns=["Time", "Status"]).sort_values("Time", kind="stable")


def messages_frame(records: list[dict]) -> pd.DataFrame:
    """Race control messages with FastF1 column names (Date in UTC, Lap)."""
    if not records:
        return pd.DataFrame(columns=["Date", "Time", "Category", "Message", "Flag", "Scope", "Lap"])
    df = pd.DataFrame(records)
    return pd.DataFrame(
        {
            "Date": utc(df["date"]),
            "Time": utc(df["date"]),
            "Category": df["category"],
            "Message": df["message"].fillna(""),
            "Flag": df["flag"],
            "Scope": df["scope"],
            "Lap": df["lap_number"].fillna(0).astype(int),
            "Phase": df.get("qualifying_phase"),
        }
    ).sort_values("Date", kind="stable")


def qualifying_parts(laps: pd.DataFrame, messages: pd.DataFrame, t0: pd.Timestamp) -> list:
    """Laps of Q1, Q2 and Q3, split at the start of each phase (race control). A lap belongs
    to the phase running when it ends."""
    starts = messages[
        (messages["Category"] == "SessionStatus") & messages["Message"].str.contains("STARTED")
    ]
    phase_start = starts.dropna(subset=["Phase"]).groupby("Phase")["Date"].min()
    end = laps["Time"] + t0
    phase = pd.Series(1, index=laps.index)
    for p in (2, 3):  # a phase that never started (red flag ending the session) stays empty
        if p in phase_start:
            phase += (end >= phase_start[p]).astype(int)
    return [laps[phase == p] for p in (1, 2, 3)]


def telemetry_frame(car: list[dict], loc: list[dict], lap_start: pd.Timestamp) -> pd.DataFrame:
    """One lap of telemetry like FastF1 Lap.get_telemetry(): car data (about 4 per second),
    distance integrated from the speed, positions interpolated onto the same times."""
    c = pd.DataFrame(car).assign(date=lambda d: utc(d["date"])).sort_values("date")
    t = (c["date"] - lap_start).dt.total_seconds().to_numpy()
    speed = c["speed"].astype(float).to_numpy()
    distance = np.concatenate([[0.0], np.cumsum((speed[1:] + speed[:-1]) / 2 / 3.6 * np.diff(t))])

    def num(col):
        values = c[col] if col in c else pd.Series(0, index=c.index)
        return pd.to_numeric(values, errors="coerce").fillna(0).astype(float).to_numpy()

    out = pd.DataFrame(
        {
            "Time": pd.to_timedelta(t, unit="s"),
            "Distance": distance,
            "Speed": speed,
            "Throttle": num("throttle"),
            "Brake": num("brake") > 0,
            "nGear": num("n_gear"),
            "RPM": num("rpm"),
            "DRS": num("drs"),
        }
    )
    if loc:
        p = pd.DataFrame(loc).assign(date=lambda d: utc(d["date"])).sort_values("date")
        tp = (p["date"] - lap_start).dt.total_seconds().to_numpy()
        out["X"] = np.interp(t, tp, p["x"].astype(float))
        out["Y"] = np.interp(t, tp, p["y"].astype(float))
    return out


class Session:
    """What the pipeline reads from a session, loaded from OpenF1."""

    def __init__(self, season: int, event: pd.Series, name: str):
        day = pd.Timestamp(event[f"Session{session_index(event, name)}DateUtc"]).strftime(
            "%Y-%m-%d"
        )
        info = openf1.find_session(season, name, day)
        self.key = info["session_key"]
        self.season, self.event, self.name = season, event, name
        self.circuit_key = info.get("circuit_key")
        self.t0 = utc(info["date_start"])
        self.date = self.t0
        k = self.key
        self.drivers = {d["driver_number"]: d for d in openf1.get("drivers", session_key=k)}
        self.race_control_messages = messages_frame(openf1.get("race_control", session_key=k))
        self.pits = openf1.get("pit", session_key=k)
        self.laps = laps_frame(
            openf1.get("laps", session_key=k),
            self.drivers,
            openf1.get("stints", session_key=k),
            self.pits if name in ("Race", "Sprint") else [],
            openf1.get("position", session_key=k),
            self.race_control_messages,
            self.t0,
        )
        lap_ends = self.laps["Time"] + self.t0
        intervals = (
            neutral_intervals(self.race_control_messages, lap_ends)
            if len(self.race_control_messages)
            else []
        )
        self.track_status = track_status_frame(intervals, self.t0)
        self.session_result = openf1.get("session_result", session_key=k)
        self.results = results_frame(
            self.drivers, self.session_result, jolpica_results(season, event, name)
        )
        self.overtakes = (
            openf1.get("overtakes", session_key=k) if name in ("Race", "Sprint") else []
        )
        radios = pd.DataFrame(openf1.get("team_radio", session_key=k))
        if radios.empty:
            radios = pd.DataFrame(columns=["driver_number", "date", "recording_url"])
        radios["date"] = pd.to_datetime(radios["date"], utc=True, format="ISO8601")
        self.radios = radios
        w = pd.DataFrame(openf1.get("weather", session_key=k))
        self.weather_data = (
            pd.DataFrame(
                {
                    "Time": utc(w["date"]) - self.t0,
                    "AirTemp": w["air_temperature"],
                    "TrackTemp": w["track_temperature"],
                    "Humidity": w["humidity"],
                    "WindSpeed": w["wind_speed"],
                    "Rainfall": w["rainfall"].astype(bool),
                }
            )
            if len(w)
            else pd.DataFrame(
                columns=["Time", "AirTemp", "TrackTemp", "Humidity", "WindSpeed", "Rainfall"]
            )
        )
        self._pos = None
        self._circuit = None

    def circuit(self) -> tuple[float, pd.DataFrame]:
        """Rotation of the official track map, and the numbered corners (X, Y, Number, Letter)."""
        if self._circuit is None:
            self._circuit = self._load_circuit()
        return self._circuit

    def _load_circuit(self) -> tuple[float, pd.DataFrame]:
        info = openf1.circuit_info(self.circuit_key, self.season) if self.circuit_key else None
        if not info:
            return 0.0, pd.DataFrame(columns=["X", "Y", "Number", "Letter"])
        corners = pd.DataFrame(
            [
                {
                    "X": c["trackPosition"]["x"],
                    "Y": c["trackPosition"]["y"],
                    "Number": c["number"],
                    "Letter": c.get("letter") or "",
                }
                for c in info.get("corners", [])
            ]
        )
        return float(info.get("rotation", 0)), corners

    def pos_data(self) -> dict[str, pd.DataFrame]:
        """Every car's positions over the session (SessionTime, X, Y), one request per driver."""
        if self._pos is None:
            until = (self.laps["Time"].max() + self.t0 + pd.Timedelta(minutes=2)).isoformat()
            self._pos = {}
            for n in self.drivers:
                rows = openf1.get(
                    "location", session_key=self.key, driver_number=n, **{"date<": until}
                )
                if rows:
                    p = pd.DataFrame(rows)
                    self._pos[str(n)] = pd.DataFrame(
                        {"SessionTime": utc(p["date"]) - self.t0, "X": p["x"], "Y": p["y"]}
                    ).sort_values("SessionTime")
        return self._pos

    def telemetry(self, lap: pd.Series) -> pd.DataFrame:
        """Telemetry of one lap (a row of self.laps)."""
        start = lap["LapStartTime"] + self.t0
        end = lap["Time"] + self.t0
        window = {"date>": start.isoformat(), "date<": end.isoformat()}
        n = int(lap["DriverNumber"])
        car = openf1.get("car_data", session_key=self.key, driver_number=n, **window)
        loc = openf1.get("location", session_key=self.key, driver_number=n, **window)
        if len(car) < 20:
            raise ValueError(f"no car data for lap {int(lap['LapNumber'])}")
        return telemetry_frame(car, loc, start)

    def qualifying_parts(self) -> list[pd.DataFrame]:
        return qualifying_parts(self.laps, self.race_control_messages, self.t0)


def session_index(event: pd.Series, name: str) -> int:
    return next(i for i in range(1, 6) if event.get(f"Session{i}") == name)


def jolpica_results(season: int, event: pd.Series, name: str) -> pd.DataFrame | None:
    """Official classification with grid and status (race and sprint), None if not out yet."""
    if name not in ("Race", "Sprint"):
        return None
    from fastf1.ergast import Ergast

    ergast = Ergast()
    fetch = ergast.get_race_results if name == "Race" else ergast.get_sprint_results
    try:
        res = fetch(season=season, round=int(event["RoundNumber"]))
    except Exception as e:  # Jolpica can lag behind: OpenF1 alone then
        print(f"WARNING: no Jolpica {name} results: {e!r}")
        return None
    return res.content[0] if res.content and len(res.content[0]) else None


def results_frame(
    drivers: dict[int, dict], result: list[dict], official: pd.DataFrame | None
) -> pd.DataFrame:
    """FastF1 results columns. Names, teams and colors from OpenF1 (the names FastF1 used);
    grid, status and classified position from Jolpica when it has the session."""
    by_number = (
        {int(r["number"]): r for r in official.to_dict("records")} if official is not None else {}
    )
    rows = []
    for r in result:
        n = r["driver_number"]
        d = drivers.get(n)
        if d is None:
            continue
        o = by_number.get(n)
        if o:
            cls, grid, status, points = o["positionText"], o["grid"], o["status"], o["points"]
        else:
            flag = "D" if r.get("dsq") else "W" if r.get("dns") else "R" if r.get("dnf") else None
            cls = flag or (str(r["position"]) if r.get("position") else "N")
            grid, status, points = np.nan, "Retired" if flag else "Finished", r.get("points") or 0
        rows.append(
            {
                "Abbreviation": d["name_acronym"],
                "DriverNumber": str(n),
                "FullName": f"{d.get('first_name', '')} {d.get('last_name', '')}".strip(),
                "TeamName": d.get("team_name"),
                "TeamColor": d.get("team_colour"),
                "Position": r.get("position") if r.get("position") is not None else np.nan,
                "ClassifiedPosition": cls,
                "GridPosition": grid,
                "Status": status,
                "Points": points if points is not None else 0.0,
            }
        )
    return pd.DataFrame(rows)
