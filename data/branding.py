"""Builders for the hotel branding. The branding is shared by everyone who uses the demo, so
tests that change it always put the original back (see the `original_branding` fixture)."""
import copy
import random
import string

import config


def random_letters(length: int = 5) -> str:
    # Hotel and contact names may only contain letters, spaces and "&"
    return "".join(random.choices(string.ascii_uppercase, k=length))


def changed_branding(original: dict, **overrides) -> dict:
    """A copy of the current branding with recognisable test values (and a valid logo URL)."""
    branding = savable(original)
    tag = random_letters()
    branding["name"] = f"QA Hotel {tag}"
    branding["description"] = f"A hotel used by automated tests, edition {tag}."
    branding["directions"] = f"Turn left at the {tag} sign."
    branding["contact"] = {**branding["contact"], "phone": "01987654321", "email": f"qa.{tag.lower()}@example.com"}
    branding["address"] = {**branding["address"], "line1": f"{tag} House", "postTown": "Testville"}
    branding.update(overrides)
    return branding


def with_field(original: dict, path: str, value) -> dict:
    """A copy of the branding with one field changed; nested fields use dots ("contact.email")."""
    branding = copy.deepcopy(original)
    target = branding
    *parents, last = path.split(".")
    for key in parents:
        target = target[key]
    target[last] = value
    return branding


def savable(branding: dict) -> dict:
    """The demo's own branding has a relative logo URL ("/images/rbp-logo.jpg") that the API
    rejects (BUG-006), so it cannot be saved back as it is. This copy points to the same image
    with an absolute URL, which the API accepts and the website shows the same way."""
    branding = copy.deepcopy(branding)
    if branding.get("logoUrl", "").startswith("/"):
        branding["logoUrl"] = config.BASE_URL + branding["logoUrl"]
    return branding
