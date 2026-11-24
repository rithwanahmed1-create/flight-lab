
"""Row validation and flight record creation."""

import re
import math
from datetime import datetime


def load_airports(path: str) -> set[str]:
    airports = set()

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            code = line.strip()
            if code and not code.startswith("#"):
                airports.add(code)

    return airports


def valid_datetime(value: str) -> bool:
    if not re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}", value
    ):
        return False

    try:
        datetime.strptime(value, "%Y-%m-%d %H:%M")
        return True
    except ValueError:
        return False


def validate_row(fields: list[str], airports: set[str]) -> str | None:
    if len(fields) != 6:
        return "WRONG_FIELD_COUNT"

    fields = [field.strip() for field in fields]

    if any(field == "" for field in fields):
        return "MISSING_FIELD"

    flight_id, origin, destination, departure, arrival, price = fields

    if not re.fullmatch(r"[A-Za-z0-9]{2,8}", flight_id):
        return "INVALID_FLIGHT_ID"

    if not re.fullmatch(r"[A-Z]{3}", origin) or origin not in airports:
        return "INVALID_ORIGIN"

    if not re.fullmatch(r"[A-Z]{3}", destination) or destination not in airports:
        return "INVALID_DESTINATION"

    if origin == destination:
        return "SAME_ORIGIN_DESTINATION"

    if not valid_datetime(departure):
        return "INVALID_DEPARTURE"

    if not valid_datetime(arrival):
        return "INVALID_ARRIVAL"

    if arrival <= departure:
        return "ARRIVAL_NOT_AFTER_DEPARTURE"

    try:
        price_value = float(price)
    except ValueError:
        return "INVALID_PRICE"

    if not math.isfinite(price_value):
        return "INVALID_PRICE"

    if price_value <= 0:
        return "NON_POSITIVE_PRICE"

    return None


def to_record(fields: list[str]) -> dict:
    flight_id, origin, destination, departure, arrival, price = [
        field.strip() for field in fields
    ]

    return {
        "flight_id": flight_id,
        "origin": origin,
        "destination": destination,
        "departure_datetime": departure,
        "arrival_datetime": arrival,
        "price": float(price),
    }
