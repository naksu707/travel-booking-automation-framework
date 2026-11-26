import pytest
from playwright.sync_api import Page, expect

from data.bookings import a_booking, a_guest, future_dates
from pages.reservation_page import ReservationPage

pytestmark = pytest.mark.ui


@pytest.mark.smoke
def test_guest_books_a_room_and_sees_the_confirmation(page: Page, room):
    check_in, check_out = future_dates(nights=3)

    reservation = ReservationPage(page).open_for(room["roomid"], check_in, check_out).book(a_guest())

    expect(reservation.confirmation).to_be_visible()
    expect(reservation.confirmation).to_contain_text(f"{check_in} - {check_out}")


def test_the_price_summary_adds_the_nights_and_the_fees(page: Page, room):
    check_in, check_out = future_dates(nights=3)

    reservation = ReservationPage(page).open_for(room["roomid"], check_in, check_out)

    # 3 nights x £120 + £25 cleaning fee + £15 service fee
    expect(reservation.total).to_contain_text("£400")


def test_booking_without_guest_details_shows_the_errors(page: Page, room):
    check_in, check_out = future_dates()

    reservation = ReservationPage(page).open_for(room["roomid"], check_in, check_out).start_booking().confirm()

    expect(reservation.errors).to_contain_text("Firstname should not be blank")
    expect(reservation.errors).to_contain_text("Lastname should not be blank")
    expect(reservation.confirmation).not_to_be_visible()


def test_booking_with_an_invalid_email_is_rejected(page: Page, room):
    check_in, check_out = future_dates()
    guest = {**a_guest(), "email": "not-an-email"}

    reservation = ReservationPage(page).open_for(room["roomid"], check_in, check_out).book(guest)

    expect(reservation.errors).to_be_visible()
    expect(reservation.confirmation).not_to_be_visible()


@pytest.mark.known_defect
def test_booking_dates_that_are_already_taken_shows_an_error(page: Page, room, api, created_bookings):
    """BUG-003: instead of an error message, the page crashes with "This page couldn't load"."""
    check_in, check_out = future_dates()
    first = api.create_booking(a_booking(room["roomid"], check_in, check_out))
    assert first.status == 201, first.text()
    created_bookings.append(first.json()["bookingid"])

    reservation = ReservationPage(page).open_for(room["roomid"], check_in, check_out).book(a_guest())

    expect(reservation.errors).to_be_visible()
    expect(reservation.confirmation).not_to_be_visible()


def test_cancel_returns_to_the_calendar(page: Page, room):
    check_in, check_out = future_dates()

    reservation = ReservationPage(page).open_for(room["roomid"], check_in, check_out).start_booking()
    reservation.cancel_button.click()

    expect(reservation.reserve_button).to_be_visible()
    expect(reservation.firstname).not_to_be_visible()
