import pytest

from api.client import RestfulBookerApi
from data.messages import a_message

pytestmark = pytest.mark.api


@pytest.fixture
def send(api: RestfulBookerApi, created_messages):
    """Sends a message as a guest and registers it for clean-up; returns the response."""
    def _send(message: dict):
        response = api.send_message(message)
        if response.status == 201:
            created_messages.append(response.json()["messageid"])
        return response
    return _send


@pytest.mark.smoke
def test_a_guest_sends_a_message(send):
    message = a_message()

    response = send(message)

    assert response.status == 201, response.text()
    created = response.json()
    assert created["messageid"] > 0
    for field in ["name", "email", "phone", "subject", "description"]:
        assert created[field] == message[field]


def test_a_new_message_is_listed_as_unread(send, admin_api: RestfulBookerApi):
    message = a_message()
    send(message)

    listed = admin_api.find_message(message["subject"])

    assert listed is not None, "the message is not in the list"
    assert listed["name"] == message["name"]
    assert listed["read"] is False


def test_admin_reads_a_message_with_all_its_details(send, admin_api: RestfulBookerApi):
    message = a_message()
    message_id = send(message).json()["messageid"]

    response = admin_api.get_message(message_id)

    assert response.status == 200
    for field in ["name", "email", "phone", "subject", "description"]:
        assert response.json()[field] == message[field]


def test_admin_marks_a_message_as_read(send, admin_api: RestfulBookerApi):
    message = a_message()
    message_id = send(message).json()["messageid"]

    assert admin_api.mark_message_read(message_id).status == 202
    assert admin_api.find_message(message["subject"])["read"] is True


def test_admin_deletes_a_message(send, admin_api: RestfulBookerApi):
    message = a_message()
    message_id = send(message).json()["messageid"]

    assert admin_api.delete_message(message_id).status == 202
    assert admin_api.find_message(message["subject"]) is None


@pytest.mark.parametrize("token", [None, "not-a-real-token"], ids=["no token", "invalid token"])
def test_a_guest_cannot_mark_as_read_or_delete_a_message(send, api: RestfulBookerApi, token):
    message_id = send(a_message()).json()["messageid"]

    assert api.mark_message_read(message_id, token=token).status == 403
    assert api.delete_message(message_id, token=token).status == 403


@pytest.mark.known_defect
@pytest.mark.parametrize("token", [None, "not-a-real-token"], ids=["no token", "invalid token"])
def test_the_list_of_messages_is_private_to_the_admin(send, api: RestfulBookerApi, token):
    """BUG-004: anyone can list the messages (names and subjects) without logging in."""
    send(a_message())

    assert api.list_messages(token=token).status == 403, "the list of messages is public"


@pytest.mark.known_defect
@pytest.mark.parametrize("token", [None, "not-a-real-token"], ids=["no token", "invalid token"])
def test_a_message_with_contact_details_is_private_to_the_admin(send, api: RestfulBookerApi, token):
    """BUG-004: anyone can read a message, with the guest's email and phone, without logging in."""
    message_id = send(a_message()).json()["messageid"]

    response = api.get_message(message_id, token=token)

    assert response.status == 403, f"a message with email and phone is public ({response.status})"


@pytest.mark.known_defect
def test_reading_a_deleted_message_answers_404(send, admin_api: RestfulBookerApi):
    """BUG-005: the API answers 500 Internal Server Error instead of 404 Not Found."""
    message_id = send(a_message()).json()["messageid"]
    admin_api.delete_message(message_id)

    assert admin_api.get_message(message_id).status == 404


@pytest.mark.parametrize(
    "field, value, error",
    [
        ("name", "", "Name may not be blank"),
        ("email", "", "Email may not be blank"),
        ("email", "not-an-email", None),
        ("phone", "0123456789", "Phone must be between 11 and 21 characters."),
        ("phone", "0" * 22, "Phone must be between 11 and 21 characters."),
        ("subject", "Room", "Subject must be between 5 and 100 characters."),
        ("subject", "S" * 101, "Subject must be between 5 and 100 characters."),
        ("description", "Is there parking?", "Message must be between 20 and 2000 characters."),
        ("description", "M" * 2001, "Message must be between 20 and 2000 characters."),
    ],
    ids=[
        "empty name", "empty email", "invalid email", "phone of 10 digits", "phone of 22 digits",
        "subject of 4 letters", "subject of 101 letters", "message of 17 letters", "message of 2001 letters",
    ],
)
def test_invalid_messages_are_rejected_with_an_explanation(send, field, value, error):
    response = send(a_message(**{field: value}))

    assert response.status == 400, f"{field}={value[:30]!r} was accepted with {response.status}"
    errors = response.json()["fieldErrors"]
    assert errors, "no message explains what is wrong"
    if error:
        assert error in errors


@pytest.mark.parametrize("length", [11, 21], ids=["phone of 11 digits", "phone of 21 digits"])
def test_phone_numbers_at_the_limits_are_accepted(send, length):
    assert send(a_message(phone="0" * length)).status == 201
