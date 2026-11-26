"""A booking made in the browser is checked through the API, where the admin sees it."""
import pytest
from playwright.sync_api import Page, expect

from api.client import RestfulBookerApi
from data.bookings import a_booking, a_guest, as_iso_date, future_dates
from pages.reservation_page import ReservationPage

pytestmark = pytest.mark.integration


@pytest.mark.smoke
def test_a_booking_made_in_the_website_is_saved_with_the_guest_and_dates(
        page: Page, room, admin_api: RestfulBookerApi, created_bookings):
    check_in, check_out = future_dates(nights=2)
    guest = a_guest()

    reservation = ReservationPage(page).open_for(room["roomid"], check_in, check_out).book(guest)
    expect(reservation.confirmation).to_be_visible()

    bookings = admin_api.list_bookings(room["roomid"]).json()["bookings"]
    created_bookings.extend(b["bookingid"] for b in bookings)
    assert len(bookings) == 1, f"expected 1 booking for the room, found {len(bookings)}"
    saved = bookings[0]
    assert (saved["firstname"], saved["lastname"]) == (guest["firstname"], guest["lastname"])
    assert as_iso_date(saved["bookingdates"]["checkin"]) == check_in
    assert as_iso_date(saved["bookingdates"]["checkout"]) == check_out


def test_dates_booked_in_the_website_are_no_longer_available_in_the_api(
        page: Page, room, api: RestfulBookerApi, admin_api: RestfulBookerApi, created_bookings):
    check_in, check_out = future_dates()

    reservation = ReservationPage(page).open_for(room["roomid"], check_in, check_out).book(a_guest())
    expect(reservation.confirmation).to_be_visible()
    created_bookings.extend(b["bookingid"] for b in admin_api.list_bookings(room["roomid"]).json()["bookings"])

    assert api.create_booking(a_booking(room["roomid"], check_in, check_out)).status == 409
