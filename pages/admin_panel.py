import re

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class AdminPanel(BasePage):
    """Admin area after logging in: the rooms page with the admin navigation bar."""

    path = "/admin/rooms"

    def __init__(self, page: Page):
        super().__init__(page)
        self.logout_button = page.get_by_role("button", name="Logout")
        self.front_page_link = page.locator("#frontPageLink")

    def wait_until_loaded(self):
        """After login the app redirects to /admin/rooms; acting before that redirect is lost."""
        expect(self.page).to_have_url(re.compile(r"/admin/rooms$"))
        expect(self.logout_button).to_be_visible()
        return self

    def logout(self):
        self.logout_button.click()
        return self
