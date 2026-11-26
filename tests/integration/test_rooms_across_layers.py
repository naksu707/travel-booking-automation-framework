"""A room added by the admin is offered to guests on the public website."""
import random

import pytest
from playwright.sync_api import Page, expect

from data.rooms import a_room
from pages.home_page import HomePage

pytestmark = pytest.mark.integration


@pytest.mark.known_defect
def test_a_room_created_by_the_admin_is_offered_on_the_website(page: Page, admin_api, created_rooms):
    """BUG-008: the website keeps showing only the three original rooms; a new room is in the
    API (and in the admin panel) but is never offered to guests."""
    description = f"Room with a garden view number {random.randint(1000, 9999)}, created by an automated test."
    room = a_room(type="Family", roomPrice=345, description=description)
    created_rooms.append(admin_api.create_room(room).json()["roomid"])

    home = HomePage(page).open()
    card = home.room_cards.filter(has_text=description)

    # Reload for up to 90 seconds, in case the website shows new rooms late
    home.reload_until_visible(card)
    expect(card).to_contain_text("Family")
    expect(card).to_contain_text("£345")
