"""Shared fixtures for UI and API tests."""
import pytest
from playwright.sync_api import Page, Playwright

import config
from api.client import RestfulBookerApi
from data.branding import savable
from data.rooms import a_room


@pytest.fixture(scope="session")
def base_url():
    """Used by pytest-playwright for page.goto("/..."); change it with the BASE_URL environment variable."""
    return config.BASE_URL


def _new_api_context(playwright: Playwright):
    # A fresh context per client: contexts keep cookies, and a login must never leak into
    # a test that expects to be logged out
    return playwright.request.new_context(base_url=config.BASE_URL)


@pytest.fixture
def api(playwright: Playwright):
    """API client that is not logged in."""
    context = _new_api_context(playwright)
    yield RestfulBookerApi(context)
    context.dispose()


@pytest.fixture
def admin_api(playwright: Playwright):
    """API client logged in as admin, with its token ready for create, update and delete."""
    context = _new_api_context(playwright)
    client = RestfulBookerApi(context)
    response = client.login()
    assert response.ok, f"admin login failed with status {response.status}"
    assert client.token, "the login response did not set a token cookie"
    yield client
    context.dispose()


@pytest.fixture
def created_rooms(admin_api):
    """Collects the ids of the rooms a test creates and deletes them afterwards."""
    room_ids: list[int] = []
    yield room_ids
    for room_id in room_ids:
        admin_api.delete_room(room_id)


@pytest.fixture
def room(admin_api, created_rooms) -> dict:
    """A new room only for this test, so its dates are always free; deleted afterwards."""
    response = admin_api.create_room(a_room(type="Double", roomPrice=120))
    assert response.status == 201, f"could not create the test room: {response.status} {response.text()}"
    created = response.json()
    created_rooms.append(created["roomid"])
    return created


@pytest.fixture
def created_bookings(admin_api):
    """Collects the ids of the bookings a test creates and deletes them afterwards."""
    booking_ids: list[int] = []
    yield booking_ids
    for booking_id in booking_ids:
        admin_api.delete_booking(booking_id)


@pytest.fixture
def created_messages(admin_api):
    """Collects the ids of the messages a test creates and deletes them afterwards."""
    message_ids: list[int] = []
    yield message_ids
    for message_id in message_ids:
        admin_api.delete_message(message_id)


@pytest.fixture
def admin_page(page: Page, admin_api, base_url) -> Page:
    """A browser page already logged in as admin: the token from the API login is set as the
    "token" cookie, so UI tests of the admin panel skip the login form."""
    page.context.add_cookies([{"name": "token", "value": admin_api.token, "url": base_url}])
    return page


@pytest.fixture
def original_branding(admin_api) -> dict:
    """The hotel branding before the test. It is shared by every visitor of the demo, so it is
    always put back after the test, even when the test fails. It is restored with an absolute
    logo URL, because the API rejects the demo's own relative one (BUG-006)."""
    original = admin_api.get_branding().json()
    yield original
    response = admin_api.update_branding(savable(original))
    assert response.status == 202, f"could not restore the branding: {response.status} {response.text()}"
