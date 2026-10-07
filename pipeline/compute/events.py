"""Race timeline: neutralizations and the race control messages worth showing."""

import re

import pandas as pd

from pipeline.compute.track import neutral_spans

DRIVER_CODE = re.compile(r"\(([A-Z]{3})\)")


def classify(category: str, flag, message: str) -> str | None:
    if category == "SafetyCar":
        return "vsc" if "VIRTUAL" in message else "sc"
    if flag == "RED":
        return "red"
    if flag == "CHEQUERED":
        return "finish"
    if "PENALTY" in message:
        return "penalty"
    if "UNDER INVESTIGATION" in message or "WILL BE INVESTIGATED" in message:
        return "investigation"
    return None


def compute_events(messages: pd.DataFrame, neutral: dict[int, str]) -> dict:
    msgs = []
    for m in messages.itertuples():
        kind = classify(m.Category, m.Flag, m.Message)
        if kind:
            msgs.append(
                {
                    "lap": int(m.Lap),
                    "kind": kind,
                    "msg": m.Message,
                    "drv": DRIVER_CODE.findall(m.Message),
                }
            )
    return {"neutral": neutral_spans(neutral), "msgs": msgs}
