<div align="center">

# 🏨 Travel Booking Automation Framework

**UI and API test automation for a hotel booking platform, with Playwright for Python and Postman collections run by Newman**

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-Python-2EAD33?style=flat-square&logo=playwright&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white)
![Postman](https://img.shields.io/badge/Postman-FF6C37?style=flat-square&logo=postman&logoColor=white)
![Newman](https://img.shields.io/badge/Newman-CLI-FF6C37?style=flat-square)
![Allure](https://img.shields.io/badge/Allure-Report-FF4F00?style=flat-square)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white)

</div>

> [!NOTE]
> **Status: in progress 🚧** · The scope and architecture are defined. Implementation starts with the framework core, the guest booking flow and the Postman collection for authentication and rooms.

---

## 💡 About

A test automation framework for **[Restful Booker Platform](https://automationintesting.online/)**, a demo bed-and-breakfast booking site built by Automation in Testing for practicing testing. It has a **guest website** (rooms, availability, booking and contact form), an **admin panel** (rooms, bookings, messages and branding) and a set of **REST APIs** behind them.

The project tests the platform from three angles:

| Layer | Tool | What it checks |
|---|---|---|
| **UI** | Playwright for Python + pytest | What guests and the admin do and see in the browser |
| **API** | Playwright's `APIRequestContext` + pytest | Business rules, status codes and data, from Python |
| **API collections** | Postman + Newman | The same APIs as shareable collections with test scripts, run from the command line and in CI |

> Restful Booker Platform is a public demo application. No real hotel, payments or personal data are involved, and its data is reset regularly.

**Design goals**

- **Two toolsets, one platform:** Playwright covers UI and API in code; Postman documents and checks the APIs in a format that developers, testers and analysts can open and run.
- **UI and API agree:** a booking made in the website must exist in the API and in the admin panel.
- **Maintainable:** Page Object Model for the UI, a small API client for Python, and Postman environments instead of hard-coded URLs.
- **Independent tests:** each test creates its own data (rooms, bookings, messages) and cleans up what it creates.

---

## 🧪 Test scope

| Area | UI (Playwright) | API (Playwright) | Postman | Status |
|---|:---:|:---:|:---:|---|
| Authentication: admin login, invalid credentials, logout, token validation | ✅ | ✅ | ✅ | ✅ Done |
| Rooms: list, details, create, update and delete (admin) | ✅ | ✅ | ✅ | 🔄 API and Postman done, UI next |
| Guest booking: check availability, book a room, required fields, invalid dates, confirmation | ✅ | ✅ | ✅ | Planned |
| Booking management: bookings in the admin report, double booking of the same dates | ✅ | ✅ | ✅ | Planned |
| Contact form: send a message, field validation, message in the admin inbox | ✅ | ✅ | ✅ | Planned |
| Branding: hotel name, contact details and map shown on the website | ✅ | ✅ | ✅ | Planned |
| UI vs. API consistency: what the website shows matches the API | ✅ | ✅ | | Planned |

### Risk-based priorities

| Priority | Features |
|---|---|
| **Critical** | Guest booking, room availability, double booking, admin authentication |
| **High** | Room management, booking validation, contact form, access without login |
| **Medium** | Branding, navigation, secondary validation messages |

Detailed test cases are in [`docs/test-cases.md`](docs/test-cases.md), and the defects found in [`docs/defects.md`](docs/defects.md).

---

## 🛠️ Tech stack

| Purpose | Tool |
|---|---|
| Language | Python 3.12 |
| UI automation | Playwright for Python (`pytest-playwright`) |
| API automation in code | Playwright `APIRequestContext` |
| Test runner | pytest (markers, fixtures, parametrization) |
| API collections | Postman (collections, environments, pre-request and test scripts) |
| Collection runner | Newman, with an HTML report (`newman-reporter-htmlextra`) |
| Reporting | Allure for pytest; HTML report for Newman |
| CI/CD | GitHub Actions |
| IDE | PyCharm / IntelliJ IDEA |

---

## 🏗️ Architecture

```text
travel-booking-automation-framework
├── tests/
│   ├── ui/              Playwright UI tests: booking, rooms, contact, admin
│   ├── api/             Playwright API tests: auth, room, booking, message, branding
│   └── integration/     UI vs. API: what the website does, checked through the API
├── pages/               Page Objects: HomePage, RoomPage, BookingForm, ContactForm,
│                        AdminLoginPage, AdminRoomsPage, AdminMessagesPage
├── api/                 API client and models used by the Python tests
├── data/                Test data builders (guests, rooms, dates) and data files
├── postman/
│   ├── collections/     restful-booker-platform.postman_collection.json
│   ├── environments/    public-demo.postman_environment.json
│   └── data/            CSV files for data-driven collection runs
├── docs/                Test cases, defects, test strategy and test plan
├── conftest.py          Shared fixtures: browser, API context, admin token, test data clean-up
├── pytest.ini           Markers (smoke, ui, api, integration) and settings
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
                    └────────── GitHub Actions ──────┘
```

---

## ✍️ Examples

**UI test with Playwright for Python**

```python
@pytest.mark.smoke
def test_admin_logs_in_and_sees_the_rooms_page(page: Page):
    AdminLoginPage(page).open().login_as(config.ADMIN_USERNAME, config.ADMIN_PASSWORD)

    expect(page).to_have_url(re.compile(r"/admin/rooms$"))
    expect(AdminPanel(page).logout_button).to_be_visible()
```

**API test with Playwright's `APIRequestContext`**

```python
@pytest.mark.smoke
def test_admin_creates_a_room(admin_api: RestfulBookerApi, created_rooms):
    room = a_room(type="Suite", roomPrice=275)

    response = admin_api.create_room(room)

    assert response.status == 201, response.text()
    created = response.json()
    created_rooms.append(created["roomid"])      # deleted again after the test
    assert created["roomName"] == room["roomName"]
```

**Postman test script**

```javascript
pm.test("Status is 201", () => pm.response.to.have.status(201));

const room = pm.response.json();
pm.environment.set("roomId", room.roomid);     // used by the next requests

pm.test("The room is returned with the data that was sent", () => {
    pm.expect(room.roomName).to.eql(pm.environment.get("roomName"));
});
```

---

## ▶️ Run the tests

**Requirements:** Python 3.12+, Node.js 20+ (for Newman) and Git.

```bash
# Python dependencies and browsers
pip install -r requirements.txt
playwright install chromium

# All Playwright tests (UI, API and integration)
pytest

# Only one group: smoke, ui, api
pytest -m smoke

# Watch the browser
pytest --headed --slowmo 300

# Postman collection with Newman
npm install -g newman newman-reporter-htmlextra
newman run postman/collections/restful-booker-platform.postman_collection.json \
  -e postman/environments/public-demo.postman_environment.json \
  -d postman/data/room-types.csv \
  --folder Auth --folder Rooms \
  -r cli,htmlextra --reporter-htmlextra-export newman/report.html

# Only the checks that expose open defects (they fail on purpose)
pytest -m known_defect
newman run postman/collections/restful-booker-platform.postman_collection.json \
  -e postman/environments/public-demo.postman_environment.json \
  --folder "Known defects"
```

The Postman collection can also be imported in the Postman app (**Import → File**) together with its environment.

---

## ⚙️ CI/CD

GitHub Actions runs two jobs on every push to `main` and on every pull request:

- **Playwright:** UI and API tests with pytest on Chromium, publishing the Allure results (and Playwright traces when a test fails) as artifacts.
- **Postman:** the collection with Newman, once per room type in `room-types.csv`, publishing the HTML report as an artifact.

---

## 🗺️ Roadmap

- [x] Framework core: pytest, Playwright, Page Objects, API client, fixtures and configuration
- [x] Postman collection and environment: authentication and rooms
- [ ] Guest booking flow (UI, API and Postman)
- [ ] Contact form and admin messages
- [ ] Admin panel: rooms and bookings
- [ ] Branding
- [ ] UI vs. API consistency tests
- [x] Data-driven Postman runs with CSV files
- [x] CI with GitHub Actions: Playwright and Newman jobs with reports
- [ ] Test strategy, test plan, test cases and defect reports

---

## ⚠️ Known limitations

- The public demo is shared and resets its data regularly, so tests create the data they need instead of relying on what is already there.
- The admin credentials (`admin` / `password`) are public demo data, documented by the platform itself.
- The demo sometimes answers `502 Bad Gateway` for a few seconds while it restarts. The Python API client retries only those gateway errors (up to 3 times), so a restart does not fail the run but real errors still do.
- Tests that expose an open defect are tagged `known_defect` (pytest) or kept in the **Known defects** folder (Postman). They are left out of the normal run, so CI stays green while the defect is still documented and reproducible.

---

<div align="center">

Made by 💜 **[Maria Jose Ospina](https://github.com/naksu707)** 💜

</div>
