import re

import pytest
from playwright.sync_api import Page, expect

from data.messages import a_message
from pages.admin_messages_page import AdminMessagesPage

pytestmark = pytest.mark.ui


@pytest.fixture
def sent_message(api, admin_api, created_messages) -> dict:
    """A message sent through the API as a guest, deleted after the test."""
    message = a_message()
    response = api.send_message(message)
    assert response.status == 201, response.text()
    message["id"] = response.json()["messageid"]
    created_messages.append(message["id"])
    return message


@pytest.mark.smoke
def test_a_new_message_is_listed_as_unread_in_the_inbox(admin_page: Page, sent_message):
    inbox = AdminMessagesPage(admin_page).open()

    row = inbox.row_with_subject(sent_message["subject"])
    expect(row).to_contain_text(sent_message["name"])
    expect(row).to_have_class(re.compile(r"read-false"))


def test_opening_a_message_shows_all_its_details(admin_page: Page, sent_message):
    inbox = AdminMessagesPage(admin_page).open().open_message(sent_message["subject"])

    for detail in ["name", "phone", "email", "subject", "description"]:
        expect(inbox.opened_message).to_contain_text(sent_message[detail])


def test_an_opened_message_is_marked_as_read(admin_page: Page, sent_message):
    inbox = AdminMessagesPage(admin_page).open().open_message(sent_message["subject"])
    inbox.close_button.click()

    inbox.open()
    expect(inbox.row_with_subject(sent_message["subject"])).to_have_class(re.compile(r"read-true"))


def test_admin_deletes_a_message_from_the_inbox(admin_page: Page, sent_message, admin_api):
    inbox = AdminMessagesPage(admin_page).open()

    inbox.delete_message(sent_message["subject"])

    expect(inbox.row_with_subject(sent_message["subject"])).to_have_count(0)
    assert admin_api.find_message(sent_message["subject"]) is None
