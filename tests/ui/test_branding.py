import pytest
from playwright.sync_api import Page, expect

from data.branding import random_letters, savable
from pages.admin_branding_page import AdminBrandingPage
from pages.home_page import HomePage

pytestmark = pytest.mark.ui


@pytest.mark.smoke
def test_the_website_shows_the_hotel_branding(page: Page, api):
    branding = api.get_branding().json()

    home = HomePage(page).open().reload_until_hotel_is(branding["name"])

    expect(home.location).to_contain_text(branding["address"]["line1"])
    expect(home.location).to_contain_text(branding["address"]["postCode"])
    expect(home.location).to_contain_text(branding["contact"]["phone"])
    expect(home.location).to_contain_text(branding["contact"]["email"])
    expect(home.footer).to_contain_text(branding["name"])


def test_admin_renames_the_hotel_from_the_branding_page(admin_page: Page, admin_api, original_branding):
    new_name = f"QA Hotel {random_letters()}"
    form = AdminBrandingPage(admin_page).open().wait_until_loaded()

    # The logo URL is made absolute too: the demo's own relative one is rejected (BUG-006)
    form.change_name(new_name, logo_url=savable(original_branding)["logoUrl"])

    expect(form.updated_message).to_be_visible()
    assert admin_api.get_branding().json()["name"] == new_name


@pytest.mark.known_defect
def test_admin_renames_the_hotel_without_touching_the_logo(admin_page: Page, admin_api, original_branding):
    """BUG-006: changing only the name fails with "Url should be a correct url format",
    because the logo URL already in the form is rejected."""
    new_name = f"QA Hotel {random_letters()}"
    form = AdminBrandingPage(admin_page).open().wait_until_loaded()

    form.change_name(new_name)

    expect(form.updated_message).to_be_visible()


def test_the_branding_form_explains_invalid_values(admin_page: Page, admin_api, original_branding):
    form = AdminBrandingPage(admin_page).open().wait_until_loaded()

    form.change_name("Hotel 123")

    expect(form.errors).to_contain_text("Name can only contain alpha characters and the & sign")
    expect(form.updated_message).not_to_be_visible()
    assert admin_api.get_branding().json()["name"] == original_branding["name"]
