import time

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class HomePage(BasePage):
    """Public website front page, with the contact form at the bottom."""

    path = "/"

    def __init__(self, page: Page):
        super().__init__(page)
        contact = page.locator("#contact")
        self.name = contact.get_by_test_id("ContactName")
        self.email = contact.get_by_test_id("ContactEmail")
        self.phone = contact.get_by_test_id("ContactPhone")
        self.subject = contact.get_by_test_id("ContactSubject")
        self.description = contact.get_by_test_id("ContactDescription")
        self.submit_button = contact.get_by_role("button", name="Submit")
        self.contact_errors = contact.locator(".alert-danger")
        self.contact_thanks = contact.get_by_role("heading", name="Thanks for getting in touch")
        self.contact_section = contact
        self.welcome = page.locator("section.hero h1")
        self.location = page.locator("#location")
        self.footer = page.locator("footer")
        self.room_cards = page.locator("#rooms .room-card")

    def send_message(self, message: dict):
        self.name.fill(message["name"])
        self.email.fill(message["email"])
        self.phone.fill(message["phone"])
        self.subject.fill(message["subject"])
        self.description.fill(message["description"])
        self.submit_button.click()
        return self

    def reload_until_hotel_is(self, name: str, timeout_s: int = 90):
        """The website caches the branding for up to 60 seconds, so a change made through the
        API or the admin panel is not shown at once: reload until the hotel name appears."""
        deadline = time.monotonic() + timeout_s
        while True:
            try:
                expect(self.welcome).to_have_text(f"Welcome to {name}", timeout=5_000)
                return self
            except AssertionError:
                if time.monotonic() > deadline:
                    raise
                self.page.reload()

    def reload_until_visible(self, locator, timeout_s: int = 90):
        """Reloads the page until the element shows, for data the website may show late."""
        deadline = time.monotonic() + timeout_s
        while True:
            try:
                expect(locator).to_be_visible(timeout=5_000)
                return self
            except AssertionError:
                if time.monotonic() > deadline:
                    raise
                self.page.reload()
