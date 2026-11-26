from datetime import date, timedelta

import pytest

from api.client import RestfulBookerApi
from data.bookings import a_booking, as_iso_date, future_dates

pytestmark = pytest.mark.api


@pytest.fixture
def book(api: RestfulBookerApi, created_bookings):
    """Creates a booking as a guest and registers it for clean-up; returns the response."""
    def _book(payload: dict):
        response = api.create_booking(payload)
        if response.status == 201:
            created_bookings.append(response.json()["bookingid"])
        return response
    return _book


@pytest.mark.smoke
def test_a_guest_books_a_room(book, room):
    check_in, check_out = future_dates(nights=2)
    payload = a_booking(room["roomid"], check_in, check_out)

    response = book(payload)

    assert response.status == 201, response.text()
    created = response.json()
    assert created["bookingid"] > 0
    assert created["booking"]["roomid"] == room["roomid"]
    assert created["booking"]["firstname"] == payload["firstname"]
    assert as_iso_date(created["booking"]["bookingdates"]["checkin"]) == check_in
    assert as_iso_date(created["booking"]["bookingdates"]["checkout"]) == check_out


def test_admin_reads_a_booking_by_id(book, room, admin_api: RestfulBookerApi):
    payload = a_booking(room["roomid"], *future_dates())
    booking_id = book(payload).json()["bookingid"]

    response = admin_api.get_booking(booking_id)

    assert response.status == 200
    assert response.json()["lastname"] == payload["lastname"]


def test_admin_lists_the_bookings_of_a_room(book, room, admin_api: RestfulBookerApi):
    booking_id = book(a_booking(room["roomid"], *future_dates())).json()["bookingid"]

    response = admin_api.list_bookings(room["roomid"])

    assert response.status == 200
    assert booking_id in [b["bookingid"] for b in response.json()["bookings"]]


@pytest.mark.parametrize("token", [None, "not-a-real-token"], ids=["no token", "invalid token"])
def test_guest_details_are_not_readable_without_a_valid_token(book, room, api: RestfulBookerApi, token):
    booking_id = book(a_booking(room["roomid"], *future_dates())).json()["bookingid"]

    assert api.get_booking(booking_id, token=token).status == 403
    assert api.list_bookings(room["roomid"], token=token).status == 403


@pytest.mark.smoke
def test_the_same_dates_cannot_be_booked_twice(book, room):
    check_in, check_out = future_dates(nights=3)
    assert book(a_booking(room["roomid"], check_in, check_out)).status == 201

    response = book(a_booking(room["roomid"], check_in, check_out))

    assert response.status == 409


def test_overlapping_dates_cannot_be_booked(book, room):
    check_in, check_out = future_dates(nights=4)
    assert book(a_booking(room["roomid"], check_in, check_out)).status == 201
    overlap_in = (date.fromisoformat(check_in) + timedelta(days=2)).isoformat()
    overlap_out = (date.fromisoformat(check_out) + timedelta(days=2)).isoformat()

    assert book(a_booking(room["roomid"], overlap_in, overlap_out)).status == 409


def test_a_stay_can_start_the_day_the_previous_one_ends(book, room):
    check_in, check_out = future_dates(nights=2)
    assert book(a_booking(room["roomid"], check_in, check_out)).status == 201
    next_out = (date.fromisoformat(check_out) + timedelta(days=2)).isoformat()

    assert book(a_booking(room["roomid"], check_out, next_out)).status == 201


@pytest.mark.parametrize("nights", [0, -2], ids=["check-out on the check-in day", "check-out before check-in"])
def test_check_out_must_be_after_check_in(book, room, nights):
    check_in, _ = future_dates()
    check_out = (date.fromisoformat(check_in) + timedelta(days=nights)).isoformat()

    assert book(a_booking(room["roomid"], check_in, check_out)).status == 409


@pytest.mark.known_defect
def test_a_booking_in_the_past_is_rejected(book, room):
    """BUG-002: a booking for dates that already went by is accepted with 201."""
    check_in = (date.today() - timedelta(days=10)).isoformat()
    check_out = (date.today() - timedelta(days=7)).isoformat()

    response = book(a_booking(room["roomid"], check_in, check_out))

    assert response.status in (400, 409), f"a booking in the past was accepted with {response.status}"


@pytest.mark.parametrize(
    "field, value",
    [
        ("firstname", ""),
        ("firstname", "Al"),
        ("firstname", "A" * 19),
        ("lastname", ""),
        ("lastname", "Li"),
        ("email", "not-an-email"),
        ("phone", "123"),
        ("phone", "1" * 22),
    ],
    ids=[
        "empty first name", "first name of 2 letters", "first name of 19 letters",
        "empty last name", "last name of 2 letters",
        "invalid email", "phone of 3 digits", "phone of 22 digits",
    ],
)
def test_invalid_guest_details_are_rejected(book, room, field, value):
    response = book(a_booking(room["roomid"], *future_dates(), **{field: value}))

    assert response.status == 400, f"{field}={value!r} was accepted with {response.status}"
    assert response.json()["fieldErrors"], "no message explains what is wrong"


def test_admin_deletes_a_booking(book, room, admin_api: RestfulBookerApi):
    booking_id = book(a_booking(room["roomid"], *future_dates())).json()["bookingid"]

    assert admin_api.delete_booking(booking_id).status == 202
    assert admin_api.get_booking(booking_id).status == 404


def test_deleting_a_booking_frees_its_dates(book, room, admin_api: RestfulBookerApi):
    check_in, check_out = future_dates()
    booking_id = book(a_booking(room["roomid"], check_in, check_out)).json()["bookingid"]
    admin_api.delete_booking(booking_id)

    assert book(a_booking(room["roomid"], check_in, check_out)).status == 201


def test_a_guest_cannot_delete_a_booking(book, room, api: RestfulBookerApi):
    booking_id = book(a_booking(room["roomid"], *future_dates())).json()["bookingid"]

    assert api.delete_booking(booking_id, token=None).status == 403
