from playwright.sync_api import Page


class BasePage:
    """Shared behavior of every page object."""

    path = "/"

    def __init__(self, page: Page):
        self.page = page

    def open(self):
        self.page.goto(self.path)
        return self
