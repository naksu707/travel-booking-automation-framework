from playwright.sync_api import Page

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

    def send_message(self, message: dict):
        self.name.fill(message["name"])
        self.email.fill(message["email"])
        self.phone.fill(message["phone"])
        self.subject.fill(message["subject"])
        self.description.fill(message["description"])
        self.submit_button.click()
        return self
