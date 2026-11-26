import pytest
from playwright.sync_api import Page, expect

from data.rooms import a_room, unique_room_name
from pages.admin_rooms_page import AdminRoomsPage

pytestmark = pytest.mark.ui


@pytest.mark.smoke
def test_admin_creates_a_room_from_the_rooms_page(admin_page: Page, admin_api, created_rooms):
    name = unique_room_name()

    rooms_page = AdminRoomsPage(admin_page).open().create_room(name, "Suite", accessible=True, price=275)

    row = rooms_page.room_named(name)
    expect(row).to_be_visible()
    expect(row).to_contain_text("Suite")
    expect(row).to_contain_text("275")
    saved = next((r for r in admin_api.list_rooms().json()["rooms"] if r["roomName"] == name), None)
    assert saved is not None, "the room created in the admin panel is not in the API"
    created_rooms.append(saved["roomid"])
    assert (saved["type"], saved["accessible"], saved["roomPrice"]) == ("Suite", True, 275)
    assert "WiFi" in saved["features"]


def test_a_room_without_a_name_is_not_created(admin_page: Page, admin_api):
    rooms_before = len(admin_api.list_rooms().json()["rooms"])

    rooms_page = AdminRoomsPage(admin_page).open().create_room("", "Single", accessible=False, price=90)

    expect(rooms_page.errors).to_contain_text("Room name must be set")
    assert len(admin_api.list_rooms().json()["rooms"]) == rooms_before


def test_admin_deletes_a_room_from_the_rooms_page(admin_page: Page, admin_api):
    room = a_room()
    room_id = admin_api.create_room(room).json()["roomid"]

    rooms_page = AdminRoomsPage(admin_page).open()
    rooms_page.delete_room(room["roomName"])

    expect(rooms_page.room_named(room["roomName"])).to_have_count(0)
    assert room_id not in [r["roomid"] for r in admin_api.list_rooms().json()["rooms"]]
