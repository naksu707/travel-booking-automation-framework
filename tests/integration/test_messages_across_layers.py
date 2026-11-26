"""What a guest sends in the website reaches the admin through the API."""
import pytest
from playwright.sync_api import Page, expect

from api.client import RestfulBookerApi
from data.bookings import a_guest, future_dates
from data.messages import a_message
from pages.home_page import HomePage
from pages.reservation_page import ReservationPage

pytestmark = pytest.mark.integration


@pytest.mark.smoke
def test_a_message_sent_in_the_website_reaches_the_admin(
        page: Page, admin_api: RestfulBookerApi, created_messages):
    message = a_message()

    home = HomePage(page).open().send_message(message)
    expect(home.contact_thanks).to_be_visible()

    listed = admin_api.find_message(message["subject"])
    assert listed is not None, "the message sent in the website is not in the admin inbox"
    created_messages.append(listed["id"])
    saved = admin_api.get_message(listed["id"]).json()
    for field in ["name", "email", "phone", "description"]:
        assert saved[field] == message[field]


def test_a_booking_made_in_the_website_notifies_the_admin(
        page: Page, room, admin_api: RestfulBookerApi, created_bookings, created_messages):
    check_in, check_out = future_dates()
    guest = a_guest()

    reservation = ReservationPage(page).open_for(room["roomid"], check_in, check_out).book(guest)
    expect(reservation.confirmation).to_be_visible()
    created_bookings.extend(b["bookingid"] for b in admin_api.list_bookings(room["roomid"]).json()["bookings"])

    # The guest's name could repeat on the shared demo, so the notification is the one that
    # also names this booking's dates
    guest_name = f"{guest['firstname']} {guest['lastname']}"
    candidates = [m for m in admin_api.list_messages().json()["messages"]
                  if m["name"] == guest_name and m["subject"] == "You have a new booking!"]
    details = next((d for d in (admin_api.get_message(m["id"]).json() for m in reversed(candidates))
                    if check_in in d["description"] and check_out in d["description"]), None)
    assert details is not None, f"no 'You have a new booking!' message from {guest_name} for {check_in} to {check_out}"
    created_messages.append(details["messageid"])
    assert details["email"] == guest["email"]
    assert details["phone"] == guest["phone"]
