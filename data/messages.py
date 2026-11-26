"""Builders for contact form messages. Every subject is unique, so a test can find its own message."""
import random
import string


def unique_subject() -> str:
    return "QA enquiry " + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


def a_message(**overrides) -> dict:
    """A valid message; pass keyword arguments to change any field."""
    message = {
        "name": "Maria Ospina",
        "email": "maria.ospina@example.com",
        "phone": "01234567890",
        "subject": unique_subject(),
        "description": "Hello, I would like to know if the rooms have a sea view. Thank you!",
    }
    message.update(overrides)
    return message
