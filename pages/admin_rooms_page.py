from playwright.sync_api import Locator, Page

from pages.base_page import BasePage


class AdminRoomsPage(BasePage):
    """Admin room list at /admin/rooms, with the form to create a room in its last row."""

    path = "/admin/rooms"

    def __init__(self, page: Page):
        super().__init__(page)
        self.rooms = page.get_by_test_id("roomlisting")
        self.room_name = page.locator("#roomName")
        self.room_type = page.locator("#type")
        self.accessible = page.locator("#accessible")
        self.price = page.locator("#roomPrice")
        self.create_button = page.locator("#createRoom")
        self.errors = page.locator("div.alert-danger")

    def room_named(self, name: str) -> Locator:
        return self.rooms.filter(has=self.page.locator(f"[id='roomName{name}']"))

    def create_room(self, name: str, room_type: str, accessible: bool, price: int, features=("WiFi",)):
        self.room_name.fill(name)
        self.room_type.select_option(room_type)
        self.accessible.select_option(str(accessible).lower())
        self.price.fill(str(price))
        for feature in features:
            self.page.get_by_label(feature, exact=True).check()
        self.create_button.click()
        return self

    def delete_room(self, name: str):
        self.room_named(name).locator(".roomDelete").click()
        return self
