from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class AdminBrandingPage(BasePage):
    """Admin form at /admin/branding that changes the hotel details shown on the website."""

    path = "/admin/branding"

    def __init__(self, page: Page):
        super().__init__(page)
        self.name = page.locator("#name")
        self.logo_url = page.locator("#logoUrl")
        self.description = page.locator("#description")
        self.directions = page.locator("#directions")
        self.contact_email = page.locator("#contactEmail")
        self.submit_button = page.locator("#updateBranding")
        self.updated_message = page.get_by_text("Branding updated!")
        self.close_button = page.get_by_role("button", name="Close")
        self.errors = page.locator(".alert-danger")

    def wait_until_loaded(self):
        """The form is filled in after the page loads; typing before that would be overwritten."""
        expect(self.name).not_to_have_value("")
        return self

    def change_name(self, new_name: str, logo_url: str | None = None):
        if logo_url is not None:
            self.logo_url.fill(logo_url)
        self.name.fill(new_name)
        self.submit_button.click()
        return self
