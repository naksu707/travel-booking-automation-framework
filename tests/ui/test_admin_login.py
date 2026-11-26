import re

import pytest
from playwright.sync_api import Page, expect

import config
from pages.admin_login_page import AdminLoginPage
from pages.admin_panel import AdminPanel

pytestmark = pytest.mark.ui


@pytest.mark.smoke
def test_admin_logs_in_and_sees_the_rooms_page(page: Page):
    AdminLoginPage(page).open().login_as(config.ADMIN_USERNAME, config.ADMIN_PASSWORD)

    expect(page).to_have_url(re.compile(r"/admin/rooms$"))
    expect(AdminPanel(page).logout_button).to_be_visible()


@pytest.mark.parametrize(
    "username, password",
    [
        ("admin", "wrong-password"),
        ("unknown-user", "password"),
        ("", ""),
    ],
    ids=["wrong password", "unknown username", "empty fields"],
)
def test_invalid_credentials_are_rejected(page: Page, username, password):
    login = AdminLoginPage(page).open().login_as(username, password)

    expect(login.error).to_have_text("Invalid credentials")
    expect(page).not_to_have_url(re.compile(r"/admin/rooms$"))


@pytest.mark.smoke
def test_admin_logs_out_and_returns_to_the_front_page(page: Page, base_url):
    AdminLoginPage(page).open().login_as(config.ADMIN_USERNAME, config.ADMIN_PASSWORD)
    panel = AdminPanel(page).wait_until_loaded()

    panel.logout()

    expect(page).to_have_url(base_url + "/")


def test_admin_pages_require_login(page: Page):
    AdminPanel(page).open()

    expect(page).to_have_url(re.compile(r"/admin$"))
    expect(AdminLoginPage(page).login_button).to_be_visible()
