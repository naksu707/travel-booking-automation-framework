from playwright.sync_api import Page

from pages.base_page import BasePage


class ReservationPage(BasePage):
    """Room page where a guest picks dates and books: /reservation/{room id}?checkin=...&checkout=..."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.reserve_button = page.locator("#doReservation")
        self.firstname = page.get_by_placeholder("Firstname")
        self.lastname = page.get_by_placeholder("Lastname")
        self.email = page.get_by_placeholder("Email")
        self.phone = page.get_by_placeholder("Phone")
        self.confirm_button = page.get_by_role("button", name="Reserve Now")
        self.cancel_button = page.get_by_role("button", name="Cancel")
        self.errors = page.locator("div.alert-danger[role=alert]")
        self.confirmation = page.locator(".booking-card").filter(has=page.get_by_role("heading", name="Booking Confirmed"))
        self.total = page.locator(".booking-card .fw-bold").filter(has_text="Total")

    def open_for(self, room_id: int, check_in: str, check_out: str):
        """Opens the room with the dates already selected, as the home page link does."""
        self.page.goto(f"/reservation/{room_id}?checkin={check_in}&checkout={check_out}")
        return self

    def start_booking(self):
        self.reserve_button.click()
        return self

    def fill_guest(self, guest: dict):
        self.firstname.fill(guest["firstname"])
        self.lastname.fill(guest["lastname"])
        self.email.fill(guest["email"])
        self.phone.fill(guest["phone"])
        return self

    def confirm(self):
        self.confirm_button.click()
        return self

    def book(self, guest: dict):
        return self.start_booking().fill_guest(guest).confirm()
