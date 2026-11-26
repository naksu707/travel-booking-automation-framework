"""Builders for guest booking data."""
import random
from datetime import date, timedelta

FIRST_NAMES = ["Maria", "Lucas", "Sofia", "Daniel", "Valeria", "Mateo"]
LAST_NAMES = ["Ospina", "Garcia", "Martinez", "Lopez", "Ramirez", "Torres"]


def future_dates(nights: int = 3) -> tuple[str, str]:
    """A check-in far enough ahead to be free, and the check-out `nights` later (YYYY-MM-DD)."""
    check_in = date.today() + timedelta(days=random.randint(60, 700))
    return check_in.isoformat(), (check_in + timedelta(days=nights)).isoformat()


def a_guest() -> dict:
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    return {
        "firstname": first,
        "lastname": last,
        "email": f"{first}.{last}{random.randint(100, 999)}@example.com".lower(),
        "phone": "0" + "".join(random.choices("0123456789", k=10)),
    }


def a_booking(room_id: int, check_in: str, check_out: str, **overrides) -> dict:
    """A valid booking payload; pass keyword arguments to change any field."""
    booking = {
        "roomid": room_id,
        **a_guest(),
        "depositpaid": False,
        "bookingdates": {"checkin": check_in, "checkout": check_out},
    }
    booking.update(overrides)
    return booking


def as_iso_date(value) -> str:
    """The API may send dates as "2027-01-31" or as [2027, 1, 31]; both become "2027-01-31"."""
    if isinstance(value, list):
        return date(*value).isoformat()
    return str(value)
