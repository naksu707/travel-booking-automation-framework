"""Branding changed by the admin reaches every part of the public website."""
import pytest
from playwright.sync_api import Page, expect

from data.branding import changed_branding
from pages.home_page import HomePage

pytestmark = pytest.mark.integration


@pytest.mark.smoke
def test_branding_changed_in_the_api_is_shown_on_the_website(page: Page, admin_api, original_branding):
    new_branding = changed_branding(original_branding)
    assert admin_api.update_branding(new_branding).status == 202

    # The website caches the branding, so it can take a few minutes to show the change
    home = HomePage(page).open().reload_until_hotel_is(new_branding["name"])

    expect(home.location).to_contain_text(new_branding["address"]["line1"])
    expect(home.location).to_contain_text(new_branding["contact"]["phone"])
    expect(home.location).to_contain_text(new_branding["contact"]["email"])
    expect(home.location).to_contain_text(new_branding["directions"])
    expect(home.footer).to_contain_text(new_branding["name"])
