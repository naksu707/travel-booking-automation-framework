<div align="center">

# 🏨 Travel Booking Automation Framework

**UI and API test automation for a hotel booking platform, with Playwright for Python and Postman collections run by Newman**

[![Tests](https://github.com/naksu707/travel-booking-automation-framework/actions/workflows/tests.yml/badge.svg)](https://github.com/naksu707/travel-booking-automation-framework/actions/workflows/tests.yml)
[![Test report](https://img.shields.io/badge/Live_report-GitHub_Pages-7C3AED?style=flat-square)](https://naksu707.github.io/travel-booking-automation-framework/)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-Python-2EAD33?style=flat-square&logo=playwright&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white)
![Postman](https://img.shields.io/badge/Postman-FF6C37?style=flat-square&logo=postman&logoColor=white)
![Newman](https://img.shields.io/badge/Newman-CLI-FF6C37?style=flat-square)
![Allure](https://img.shields.io/badge/Allure-Report-FF4F00?style=flat-square)

**[📊 See the latest test report](https://naksu707.github.io/travel-booking-automation-framework/)**

</div>

---

## 💡 About

A test automation framework for **[Restful Booker Platform](https://automationintesting.online/)**, a demo bed-and-breakfast booking site built by Automation in Testing for practicing testing. It has a **guest website** (rooms, booking and contact form), an **admin panel** (rooms, messages and branding) and a set of **REST APIs** behind them.

The project tests the platform from three angles:

| Layer | Tool | What it checks |
|---|---|---|
| **UI** | Playwright for Python + pytest | What guests and the admin do and see in the browser |
| **API** | Playwright's `APIRequestContext` + pytest | Business rules, status codes, permissions and data, from Python |
| **API collections** | Postman + Newman | The same APIs as shareable collections with test scripts, run from the command line and in CI |

**Design goals**

- **Two toolsets, one platform:** Playwright covers UI and API in code; Postman documents and checks the APIs in a format that developers, testers and analysts can open and run.
- **UI and API agree:** a booking made in the website must exist in the API, and a change made by the admin must reach the website.
- **Maintainable:** Page Object Model for the UI, a small API client for Python, and Postman environments instead of hard-coded URLs.
- **Independent tests:** each test creates its own data (rooms, bookings, messages) and cleans up what it creates.
- **Fast admin UI tests:** tests of the admin panel log in through the API and pass the token to the browser as a cookie, so only the login tests go through the login form.

---

## 📈 In numbers

| | |
|---|---|
| **100** automated tests in the normal run | 69 API · 26 UI · 5 integration (parametrized cases counted one by one) |
| **13** checks that reproduce open defects | Tagged `known_defect`, run on demand |
| **38** Postman requests | Run 5 times, once per room type: **over 450 assertions** per run |
| **67** documented test cases | [`docs/test-cases.md`](docs/test-cases.md) |
| **8** defects found | [`docs/defects.md`](docs/defects.md), one of them critical |

---

## 🐞 Defects found

| ID | Defect | Severity |
|---|---|---|
| BUG-004 | Guest messages, with **email and phone**, can be read without logging in | 🔴 Critical |
| BUG-002 | A booking for dates in the past is accepted | 🟠 High |
| BUG-003 | Booking dates that are already taken crashes the reservation page | 🟠 High |
| BUG-006 | The branding cannot be saved: the demo's own logo URL is rejected by the API | 🟠 High |
| BUG-008 | Rooms created by the admin are never offered to guests on the website | 🟠 High |
| BUG-001 | Reading a deleted room answers 500 instead of 404 | 🟡 Medium |
| BUG-005 | Reading a deleted message answers 500 instead of 404 | 🟡 Medium |
| BUG-007 | Empty directions are reported as "Name should not be blank" | 🟢 Low |

Each one has steps to reproduce, expected and actual results, impact and evidence in [`docs/defects.md`](docs/defects.md), and an automated check that still reproduces it: `pytest -m known_defect` and the **Known defects** folder of the Postman collection.

---

## 🧪 Test scope

| Area | UI | API | Integration | Postman |
|---|:---:|:---:|:---:|:---:|
| Authentication: admin login, invalid credentials, logout, token validation, login guard | ✅ | ✅ | | ✅ |
| Rooms: list, create, update, delete, validation, permissions | ✅ | ✅ | ✅ | ✅ |
| Guest booking: book a room, price summary, guest details, dates, double and overlapping bookings | ✅ | ✅ | ✅ | ✅ |
| Booking management: admin reads, lists and deletes bookings; guest data is private | | ✅ | | ✅ |
| Contact form and admin inbox: send, validate, list, open, mark as read, delete | ✅ | ✅ | ✅ | ✅ |
| Branding: hotel name, description, contact details, address and directions on the website | ✅ | ✅ | ✅ | ✅ |

**Risk-based priorities**

| Priority | Features |
|---|---|
| **Critical** | Guest booking, double booking, admin authentication, permissions of admin-only actions |
| **High** | Contact form and inbox, room management, booking validation |
| **Medium** | Branding, secondary validation messages |

The full approach is in the [test strategy](docs/test-strategy.md) and the [test plan](docs/test-plan.md).

---

## 🛠️ Tech stack

| Purpose | Tool |
|---|---|
| Language | Python 3.12 |
| UI automation | Playwright for Python (`pytest-playwright`) |
| API automation in code | Playwright `APIRequestContext` |
| Test runner | pytest (markers, fixtures, parametrization) |
| API collections | Postman (collections, environments, pre-request and test scripts, CSV data) |
| Collection runner | Newman, with an HTML report (`newman-reporter-htmlextra`) |
| Reporting | Allure for pytest; htmlextra for Newman; both published on GitHub Pages |
| CI/CD | GitHub Actions |

---

## 🏗️ Architecture

```text
travel-booking-automation-framework
├── tests/
│   ├── api/             Auth, rooms, bookings, messages and branding through the REST APIs
│   ├── ui/              Admin login, admin rooms, inbox and branding; guest booking and contact form
│   └── integration/     UI and API together: what happens in one layer is checked in the other
├── pages/               Page Objects: HomePage, ReservationPage, AdminLoginPage, AdminPanel,
│                        AdminRoomsPage, AdminMessagesPage, AdminBrandingPage
├── api/client.py        API client: one method per endpoint, token cookie, retry of gateway errors
├── data/                Test data builders: rooms, bookings and dates, messages, branding
├── postman/
│   ├── collections/     Auth · Rooms · Booking · Messages · Branding · Known defects
│   ├── environments/    public-demo.postman_environment.json
│   └── data/            room-types.csv for the data-driven run
├── docs/                Test strategy, test plan, test cases, defects and evidence
├── report/              Landing page of the published reports
├── conftest.py          Fixtures: API clients, admin token, logged-in browser, test data clean-up
├── config.py            Base URL and admin credentials, from environment variables
├── pytest.ini           Markers (smoke, ui, api, integration, known_defect) and settings
└── requirements.txt
```

**How the layers work together:**

```text
                 ┌──────────────────────────────┐
                 │  Restful Booker Platform     │
                 │  website · admin · REST APIs │
                 └──────────────┬───────────────┘
            ┌───────────────────┼────────────────────┐
            ▼                   ▼                    ▼
   Playwright (browser)   Playwright (API)    Postman collection
   Page Objects           API client          test scripts + environment
            │                   │                    │
            └──────── pytest ───┘                 Newman
                    │                                │
              Allure report                    HTML report
                    └──── GitHub Actions → GitHub Pages ──┘
```

---

## ✍️ Examples

**Integration test: a booking made in the website is saved in the API**

```python
@pytest.mark.smoke
def test_a_booking_made_in_the_website_is_saved_with_the_guest_and_dates(
        page: Page, room, admin_api: RestfulBookerApi, created_bookings):
    check_in, check_out = future_dates(nights=2)
    guest = a_guest()

    reservation = ReservationPage(page).open_for(room["roomid"], check_in, check_out).book(guest)
    expect(reservation.confirmation).to_be_visible()

    bookings = admin_api.list_bookings(room["roomid"]).json()["bookings"]
    created_bookings.extend(b["bookingid"] for b in bookings)
    assert len(bookings) == 1
    saved = bookings[0]
    assert (saved["firstname"], saved["lastname"]) == (guest["firstname"], guest["lastname"])
```

**API test with boundary values**

```python
@pytest.mark.parametrize("price", [0, 1000], ids=["price 0", "price 1000"])
def test_room_prices_outside_1_to_999_are_rejected(admin_api: RestfulBookerApi, price):
    response = admin_api.create_room(a_room(roomPrice=price))

    assert response.status == 400
```

**Postman test script**

```javascript
pm.test("Status is 201", () => pm.response.to.have.status(201));

const created = pm.response.json();
pm.environment.set("bookingId", created.bookingid);     // used by the next requests

pm.test("The booking is returned with an id and the guest's data", () => {
    pm.expect(created.bookingid).to.be.above(0);
    pm.expect(created.booking.firstname).to.eql(pm.environment.get("guestFirstname"));
});
```

---

## ▶️ Run the tests

**Requirements:** Python 3.12+, Node.js 20+ (for Newman) and Git.

```bash
# Python dependencies and browser
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# All Playwright tests (UI, API and integration)
pytest

# Only one group: smoke, ui, api, integration
pytest -m smoke

# Watch the browser
pytest --headed --slowmo 300

# Only the checks that expose open defects (they fail on purpose)
pytest -m known_defect

# Postman collection with Newman, as CI runs it
npm install -g newman newman-reporter-htmlextra
newman run postman/collections/restful-booker-platform.postman_collection.json \
  -e postman/environments/public-demo.postman_environment.json \
  -d postman/data/room-types.csv \
  --folder Auth --folder Rooms --folder Booking --folder Messages --folder Branding \
  -r cli,htmlextra --reporter-htmlextra-export newman/report.html

# Postman checks that expose open defects
newman run postman/collections/restful-booker-platform.postman_collection.json \
  -e postman/environments/public-demo.postman_environment.json \
  --folder "Known defects"
```

The Postman collection can also be imported in the Postman app (**Import → File**) together with its environment.

---

## ⚙️ CI/CD

GitHub Actions runs on every push to `main` and on every pull request:

- **Playwright:** UI, API and integration tests with pytest on Chromium. Allure results are kept as an artifact, and traces and screenshots when a test fails.
- **Postman:** the collection with Newman, once per room type in `room-types.csv`. It runs after the Playwright job, not at the same time, because both touch the shared branding.
- **Publish reports:** on `main`, the Allure report and the Newman report are published to **[GitHub Pages](https://naksu707.github.io/travel-booking-automation-framework/)**, even when a test fails, so the report shows what went wrong.

---

## ⚠️ Known limitations

- The public demo is shared and resets its data regularly, so tests create the data they need instead of relying on what is already there.
- The admin credentials (`admin` / `password`) are public demo data, documented by the platform itself.
- The demo sometimes answers `502 Bad Gateway` for a few seconds while it restarts. The Python API client retries only those gateway errors (up to 3 times), so a restart does not fail the run but real errors still do.
- The demo resets its database every few minutes, which also ends every login. If a request made with the admin token answers 403, the API client logs in again once and repeats it; requests with no token or a wrong token are never repeated, so permission checks stay exact.
- The website caches the branding: up to 60 seconds in its own server, and longer when it is read from GitHub Actions. Tests that check a branding change on the website reload the page every 10 seconds until it shows, for up to 3 minutes. The branding is shared by every visitor, so tests that change it always restore the original (with the logo as a full URL, see BUG-006), and the Postman collection only sends the current branding back.
- Branding tests can still collide with someone else changing the branding of the demo at the same moment (for example a local run while CI is running). Tests check the answer of their own update instead of reading the branding again, which keeps that window small.
- Tests that expose an open defect are tagged `known_defect` (pytest) or kept in the **Known defects** folder (Postman). They are left out of the normal run, so CI stays green while the defect is still documented and reproducible.

---

<div align="center">

Made by 💜 **[Maria Jose Ospina](https://github.com/naksu707)** 💜

</div>
