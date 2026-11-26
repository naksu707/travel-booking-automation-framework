# Test strategy

Application under test: [Restful Booker Platform](https://automationintesting.online), a demo bed-and-breakfast site with a guest website, an admin panel and REST APIs.

## 1. Goals

- Check that guests can find a room, book it and contact the hotel, and that the admin sees and manages what guests send.
- Check the business rules where they live: in the APIs (status codes, validation, permissions) and in what the website shows.
- Prove that the layers agree: what happens in the browser is saved in the API, and what the admin changes reaches the website.
- Find and document real defects with steps, evidence and an automated check that reproduces them.

## 2. Test levels and tools

| Level | Tool | Why this tool |
|---|---|---|
| **API** | Playwright `APIRequestContext` + pytest | Fast and precise. Most rules (validation, permissions, conflicts) are tested here, with many data combinations through `parametrize`. |
| **UI** | Playwright for Python + pytest, Page Object Model | What a person actually sees: confirmations, error messages, navigation. Only the flows that matter to users, not every rule again. |
| **Integration (UI + API)** | Both, in the same test | Checks that the layers agree: a booking made in the website exists in the API; a branding change in the API reaches the website. |
| **API collections** | Postman + Newman | The same APIs as a collection that developers and analysts can open and run, with scripts that chain requests and a data-driven run per room type. |

The split follows the test pyramid: most checks are API tests (fast, stable), fewer are UI tests (slower, closer to the user), and a handful of integration tests join both.

## 3. What is in and out of scope

**In scope:** admin authentication, rooms, guest booking, booking management, contact form and admin inbox, branding, permissions of every admin-only action, consistency between UI and API.

**Out of scope:** performance and load (the demo is shared and public), visual design and responsive layouts, browsers other than Chromium, the admin booking report calendar, accessibility audits.

## 4. Test design techniques

- **Equivalence partitioning and boundary values:** room prices (0, 1–999, 1000), name and phone lengths (just below, at and just above each limit), message subject and text lengths.
- **Decision tables:** booking dates (same dates, overlapping, back-to-back, check-out before or on check-in, past dates).
- **State transitions:** message unread → read → deleted; booking created → deleted → dates free again.
- **Permission matrix:** every admin action tried with no token, an invalid token and the admin token.
- **Error guessing:** reading deleted records, empty forms, values with numbers where only letters are allowed.

## 5. Test data

- Every test creates the data it needs (rooms, bookings, messages) with unique names, and deletes it at the end, so tests are independent of each other and of the demo's own data.
- Booking tests create a new room for each test, so its dates are always free even when other people use the demo.
- The branding is shared by everyone: tests that change it save the original first and always put it back.

## 6. Environments and risks of a shared public demo

| Risk | Mitigation |
|---|---|
| The demo restarts and answers `502` for a few seconds | The API client retries only gateway errors (502, 503, 504), up to 3 times |
| Other people change or delete data at the same time | Unique test data; never rely on data the test did not create |
| The demo resets its database regularly | Each test creates and cleans its own data within a few seconds |
| The website caches the branding for up to 60 seconds | Tests that check a branding change on the website reload until it shows (up to 90 s) |
| The database reset also ends every login | The API client logs in again once when the admin token answers 403 |

## 7. Defect management

Each defect is written in [`defects.md`](defects.md) with severity, steps, expected and actual result, impact and evidence. Its automated check is tagged `known_defect` (pytest) or kept in the **Known defects** folder (Postman): it is left out of the normal run so CI stays green, and it can be run on demand to confirm the defect is still there or has been fixed.

## 8. Entry and exit criteria

**Entry:** the demo site answers, and the admin login works.

**Exit for a run:** all tests in the normal run pass; every failure is either fixed in the test or confirmed as a defect, documented and tagged.

## 9. Reporting

GitHub Actions runs the Playwright tests and the Postman collection on every push and pull request, and publishes the Allure report and the Newman report to GitHub Pages from `main`.
