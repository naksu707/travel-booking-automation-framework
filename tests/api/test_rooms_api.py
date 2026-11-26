import pytest

from api.client import RestfulBookerApi
from data.rooms import a_room

pytestmark = pytest.mark.api


@pytest.mark.smoke
def test_the_room_list_is_public(api: RestfulBookerApi):
    response = api.list_rooms()

    assert response.status == 200
    assert isinstance(response.json()["rooms"], list)


@pytest.mark.smoke
def test_admin_creates_a_room(admin_api: RestfulBookerApi, created_rooms):
    room = a_room(type="Suite", roomPrice=275)

    response = admin_api.create_room(room)

    assert response.status == 201, response.text()
    created = response.json()
    created_rooms.append(created["roomid"])
    assert created["roomName"] == room["roomName"]
    assert created["type"] == "Suite"
    assert created["roomPrice"] == 275


@pytest.mark.known_defect
def test_reading_a_room_that_never_existed_answers_404(api: RestfulBookerApi):
    """BUG-001: the API answers 500 Internal Server Error instead of 404 Not Found."""
    assert api.get_room(999999).status == 404


def test_a_created_room_can_be_read_by_id(admin_api: RestfulBookerApi, api: RestfulBookerApi, created_rooms):
    room = a_room()
    room_id = admin_api.create_room(room).json()["roomid"]
    created_rooms.append(room_id)

    response = api.get_room(room_id)

    assert response.status == 200
    assert response.json()["roomName"] == room["roomName"]


def test_admin_updates_a_room(admin_api: RestfulBookerApi, created_rooms):
    room = a_room()
    room_id = admin_api.create_room(room).json()["roomid"]
    created_rooms.append(room_id)

    response = admin_api.update_room(room_id, {**room, "roomPrice": 199, "type": "Family"})

    assert response.status == 202, response.text()
    updated = admin_api.get_room(room_id).json()
    assert updated["roomPrice"] == 199
    assert updated["type"] == "Family"


def test_admin_deletes_a_room(admin_api: RestfulBookerApi):
    room_id = admin_api.create_room(a_room()).json()["roomid"]

    assert admin_api.delete_room(room_id).status == 202
    assert room_id not in [room["roomid"] for room in admin_api.list_rooms().json()["rooms"]]


@pytest.mark.known_defect
def test_reading_a_deleted_room_answers_404(admin_api: RestfulBookerApi):
    """BUG-001: the API answers 500 Internal Server Error instead of 404 Not Found."""
    room_id = admin_api.create_room(a_room()).json()["roomid"]
    admin_api.delete_room(room_id)

    assert admin_api.get_room(room_id).status == 404


@pytest.mark.parametrize("token", [None, "not-a-real-token"], ids=["no token", "invalid token"])
def test_a_room_cannot_be_created_without_a_valid_token(api: RestfulBookerApi, token):
    response = api.create_room(a_room(), token=token)

    assert response.status == 403


@pytest.mark.parametrize(
    "field, value, message",
    [
        ("type", "Penthouse", "Type can only contain the room options Single, Double, Twin, Family or Suite"),
        ("roomName", "", "Room name must be set"),
    ],
    ids=["unknown room type", "empty room name"],
)
def test_invalid_rooms_are_rejected_with_a_message(admin_api: RestfulBookerApi, field, value, message):
    response = admin_api.create_room(a_room(**{field: value}))

    assert response.status == 400
    assert message in response.json()["fieldErrors"]


@pytest.mark.parametrize("price", [0, 1000], ids=["price 0", "price 1000"])
def test_room_prices_outside_1_to_999_are_rejected(admin_api: RestfulBookerApi, price):
    response = admin_api.create_room(a_room(roomPrice=price))

    assert response.status == 400
