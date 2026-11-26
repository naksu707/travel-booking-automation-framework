import pytest

from api.client import RestfulBookerApi
from data.branding import changed_branding, savable, with_field

pytestmark = pytest.mark.api


@pytest.mark.smoke
def test_the_branding_is_public_and_complete(api: RestfulBookerApi):
    response = api.get_branding()

    assert response.status == 200
    branding = response.json()
    for section in ["name", "description", "logoUrl", "directions", "map", "contact", "address"]:
        assert section in branding, f"'{section}' is missing from the branding"
    assert set(branding["contact"]) >= {"name", "phone", "email"}
    assert set(branding["address"]) >= {"line1", "line2", "postTown", "county", "postCode"}
    assert set(branding["map"]) >= {"latitude", "longitude"}


@pytest.mark.smoke
def test_admin_updates_the_branding(admin_api: RestfulBookerApi, original_branding):
    new_branding = changed_branding(original_branding)

    response = admin_api.update_branding(new_branding)

    # The answer of the update is checked, not a second read: the branding is shared, so
    # anyone else using the demo could change it again between the two requests
    assert response.status == 202, response.text()
    saved = response.json()
    assert saved["name"] == new_branding["name"]
    assert saved["directions"] == new_branding["directions"]
    assert saved["contact"]["email"] == new_branding["contact"]["email"]
    assert saved["address"]["line1"] == new_branding["address"]["line1"]


@pytest.mark.parametrize("token", [None, "not-a-real-token"], ids=["no token", "invalid token"])
def test_a_guest_cannot_change_the_branding(api: RestfulBookerApi, admin_api: RestfulBookerApi,
                                            original_branding, token):
    # A valid branding, so the answer depends only on the token
    response = api.update_branding(changed_branding(original_branding), token=token)

    assert response.status == 403
    assert admin_api.get_branding().json()["name"] == original_branding["name"]


@pytest.mark.parametrize(
    "field, value, error",
    [
        ("name", "Hotel 123", "Name can only contain alpha characters and the & sign"),
        ("name", "", "Name should not be blank"),
        ("logoUrl", "not a url", "Url should be a correct url format"),
        ("description", "Rooms from 50 pounds", "Description can only contain alpha characters and basic grammar"),
        ("contact.name", "Agent 007", "Contact name can only contain alpha characters and the & sign"),
        ("contact.email", "not-an-email", "Email should be a valid email format"),
        ("address.line1", "", "Line1 should not be blank"),
        ("address.postCode", "", "Post code should not be blank"),
    ],
    ids=[
        "name with numbers", "empty name", "invalid logo url", "description with numbers",
        "contact name with numbers", "invalid contact email", "empty address line 1", "empty post code",
    ],
)
def test_invalid_branding_is_rejected_with_an_explanation(admin_api: RestfulBookerApi, original_branding,
                                                          field, value, error):
    response = admin_api.update_branding(with_field(savable(original_branding), field, value))

    assert response.status == 400, f"{field}={value!r} was accepted with {response.status}"
    assert error in response.json()["fieldErrors"]
    assert admin_api.get_branding().json()["name"] == original_branding["name"]


@pytest.mark.known_defect
def test_the_current_branding_can_be_saved_back_unchanged(admin_api: RestfulBookerApi, original_branding):
    """BUG-006: the demo's own logo URL is relative, and the API rejects it, so the branding
    cannot be saved without changing the logo first."""
    response = admin_api.update_branding(original_branding)

    assert response.status == 202, f"{response.status}: {response.json().get('fieldErrors')}"


@pytest.mark.known_defect
def test_empty_directions_are_explained_with_the_right_field(admin_api: RestfulBookerApi, original_branding):
    """BUG-007: the message says "Name should not be blank" instead of naming the directions."""
    response = admin_api.update_branding(with_field(savable(original_branding), "directions", ""))

    assert response.status == 400
    errors = response.json()["fieldErrors"]
    assert any("irection" in e for e in errors), f"the error does not mention the directions: {errors}"
