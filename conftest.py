"""Shared fixtures for UI and API tests."""
import pytest
from playwright.sync_api import Playwright

import config
from api.client import RestfulBookerApi
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
