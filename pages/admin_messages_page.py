from playwright.sync_api import Locator, Page

from pages.base_page import BasePage


class AdminMessagesPage(BasePage):
    """Admin inbox at /admin/message: one row per message, opened in a pop-up."""

    path = "/admin/message"

    def __init__(self, page: Page):
        super().__init__(page)
        self.rows = page.locator(".messages .row.detail")
        self.opened_message = page.get_by_test_id("message")
        self.close_button = self.opened_message.get_by_role("button", name="Close")

    def row_with_subject(self, subject: str) -> Locator:
        return self.rows.filter(has_text=subject)

    def open_message(self, subject: str):
        self.row_with_subject(subject).get_by_text(subject).click()
        return self

    def delete_message(self, subject: str):
        self.row_with_subject(subject).locator("[data-testid^=DeleteMessage]").click()
        return self
