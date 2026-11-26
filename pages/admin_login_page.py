from playwright.sync_api import Page

from pages.base_page import BasePage


class AdminLoginPage(BasePage):
    """Admin login form at /admin."""

    path = "/admin"

    def __init__(self, page: Page):
        super().__init__(page)
        self.username = page.locator("#username")
        self.password = page.locator("#password")
        self.login_button = page.locator("#doLogin")
        # The page has a second, empty role="alert" (the Next.js route announcer), so the
        # error is found by its Bootstrap class
        self.error = page.locator("div.alert-danger[role=alert]")

    def login_as(self, username: str, password: str):
        # Empty values are typed as empty strings, so the form is sent with blank fields
        self.username.fill(username)
        self.password.fill(password)
        self.login_button.click()
        return self
