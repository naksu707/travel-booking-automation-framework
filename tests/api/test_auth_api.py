import pytest

import config
from api.client import RestfulBookerApi

pytestmark = pytest.mark.api


@pytest.mark.smoke
def test_login_with_valid_credentials_sets_a_token_cookie(api: RestfulBookerApi):
    response = api.login(config.ADMIN_USERNAME, config.ADMIN_PASSWORD)

    assert response.status == 200
    assert api.token, "no token cookie in the login response"


@pytest.mark.parametrize(
    "username, password",
    [("admin", "wrong-password"), ("unknown-user", "password"), ("", "")],
    ids=["wrong password", "unknown username", "empty credentials"],
)
def test_login_with_invalid_credentials_is_forbidden(api: RestfulBookerApi, username, password):
    response = api.login(username, password)

    assert response.status == 403
    assert api.token is None, "a token cookie was set for invalid credentials"


def test_a_valid_token_is_accepted(admin_api: RestfulBookerApi):
    assert admin_api.validate(admin_api.token).status == 200


def test_an_invalid_token_is_rejected(api: RestfulBookerApi):
    assert api.validate("not-a-real-token").status == 403


def test_a_token_is_no_longer_valid_after_logout(api: RestfulBookerApi):
    api.login()
    token = api.token

    assert api.logout(token).status == 200
    assert api.validate(token).status == 403
