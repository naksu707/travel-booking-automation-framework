"""Builders for room data. Every room gets a unique name, so tests never clash on the shared demo."""
import random
import string

ROOM_TYPES = ["Single", "Double", "Twin", "Family", "Suite"]


def unique_room_name() -> str:
    suffix = "".join(random.choices(string.digits, k=4))
    return f"QA{suffix}"


def a_room(**overrides) -> dict:
    """A valid room payload; pass keyword arguments to change any field."""
    room = {
        "roomName": unique_room_name(),
        "type": "Double",
        "accessible": True,
        "image": "/images/room2.jpg",
        "description": "Room created by an automated test.",
        "features": ["WiFi", "TV"],
        "roomPrice": 150,
    }
    room.update(overrides)
    return room
