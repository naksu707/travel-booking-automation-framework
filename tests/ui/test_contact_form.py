import pytest
from playwright.sync_api import Page, expect

from data.messages import a_message
from pages.home_page import HomePage

pytestmark = pytest.mark.ui


@pytest.mark.smoke
def test_guest_sends_a_message_and_is_thanked_by_name(page: Page, admin_api, created_messages):
    message = a_message()

    home = HomePage(page).open().send_message(message)

    expect(home.contact_thanks).to_have_text(f"Thanks for getting in touch {message['name']}!")
    expect(home.contact_section).to_contain_text(message["subject"])
    saved = admin_api.find_message(message["subject"])
    if saved:
        created_messages.append(saved["id"])


def test_an_empty_contact_form_shows_every_missing_field(page: Page):
    home = HomePage(page).open()

    home.submit_button.click()

    for error in ["Name may not be blank", "Email may not be blank", "Phone may not be blank",
                  "Subject may not be blank", "Message may not be blank"]:
        expect(home.contact_errors).to_contain_text(error)
    expect(home.contact_thanks).not_to_be_visible()


@pytest.mark.parametrize(
    "field, value, error",
    [
        ("phone", "0123456789", "Phone must be between 11 and 21 characters."),
        ("subject", "Room", "Subject must be between 5 and 100 characters."),
        ("description", "Is there parking?", "Message must be between 20 and 2000 characters."),
    ],
    ids=["phone of 10 digits", "subject of 4 letters", "message of 17 letters"],
)
def test_contact_fields_that_are_too_short_are_explained(page: Page, field, value, error):
    home = HomePage(page).open().send_message(a_message(**{field: value}))

    expect(home.contact_errors).to_contain_text(error)
    expect(home.contact_thanks).not_to_be_visible()
