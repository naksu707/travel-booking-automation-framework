# Defects

Defects found while testing the [Restful Booker Platform](https://automationintesting.online) public demo.
Each one has an automated check that reproduces it, left out of the normal run:
`pytest -m known_defect` and the **Known defects** folder of the Postman collection.

| ID | Title | Severity | Status | Found by |
|---|---|---|---|---|
| BUG-001 | Reading a deleted or unknown room answers 500 instead of 404 | Medium | Open | API (Playwright) and Postman |
| BUG-002 | A booking for dates in the past is accepted | High | Open | API (Playwright) and Postman |
| BUG-003 | Booking dates that are already taken crashes the reservation page | High | Open | UI (Playwright) |

---

## BUG-001 · Reading a deleted or unknown room answers 500 instead of 404

| Field | Value |
|---|---|
| Severity | Medium |
| Priority | Medium |
| Component | Room API, `GET /api/room/{id}` |
| Environment | https://automationintesting.online (public demo) |
| Test cases | TC-ROOM-12 |
| Automated checks | `test_reading_a_deleted_room_answers_404`, `test_reading_a_room_that_never_existed_answers_404`, Postman **Known defects / BUG-001** |

**Steps to reproduce**

1. Log in: `POST /api/auth/login` with `admin` / `password`.
2. Create a room: `POST /api/room/` with a valid room. Note its `roomid`.
3. Delete it: `DELETE /api/room/{roomid}`. The answer is `202 Accepted`.
4. Read it: `GET /api/room/{roomid}`.

The same happens when reading an id that never existed, for example `GET /api/room/999999`.

**Expected result:** `404 Not Found`. The room does not exist.

**Actual result:** `500 Internal Server Error`.

**Impact:** a client cannot tell "this room does not exist" apart from "the server is broken". Monitoring counts every lookup of a removed room as a server failure, and any client that retries on 5xx errors will retry a request that can never succeed.

**Evidence:** reproduced in every Newman iteration (5 of 5) and in the pytest run of 2026-11-26.

---

## BUG-002 · A booking for dates in the past is accepted

| Field | Value |
|---|---|
| Severity | High |
| Priority | High |
| Component | Booking API, `POST /api/booking/` |
| Environment | https://automationintesting.online (public demo) |
| Test cases | TC-BOOK-10 |
| Automated checks | `test_a_booking_in_the_past_is_rejected`, Postman **Known defects / BUG-002** |

**Steps to reproduce**

1. Pick any room id (for example, create one as admin).
2. As a guest (no token), send `POST /api/booking/` with valid guest details and dates that already went by, for example check-in 10 days ago and check-out 7 days ago.

**Expected result:** the booking is rejected (`400 Bad Request` or `409 Conflict`), as it is when the check-out is before the check-in.

**Actual result:** `201 Created`. The booking is saved for dates that are already over.

**Impact:** the hotel gets bookings that can never happen, and those past dates show as taken in the admin report. The API only checks that check-out is after check-in; it never compares the dates with today.

**Evidence:** pytest run of 2026-11-26: `AssertionError: a booking in the past was accepted with 201`.

---

## BUG-003 · Booking dates that are already taken crashes the reservation page

| Field | Value |
|---|---|
| Severity | High |
| Priority | High |
| Component | Website, reservation page (`/reservation/{room id}`) |
| Environment | https://automationintesting.online (public demo), Chromium |
| Test cases | TC-BOOK-06 |
| Automated check | `test_booking_dates_that_are_already_taken_shows_an_error` |

**Steps to reproduce**

1. Book a room for some dates (in the website or with `POST /api/booking/`).
2. Open the same room for the same dates: `/reservation/{room id}?checkin=...&checkout=...`.
3. Click **Reserve Now**, fill first name, last name, email and phone, and click **Reserve Now** again.

**Expected result:** the form stays open with a message saying the dates are not available.

**Actual result:** the whole page is replaced by "This page couldn't load. Reload to try again, or go back." No message explains what happened, and the details the guest typed are lost.

**Impact:** this is the normal situation when two guests want the same dates, and the guest sees a broken site instead of being asked to pick other dates. The API itself behaves correctly (`409 Conflict`, see TC-BOOK-06); the website does not handle that answer, which comes without the list of errors the form expects.

**Evidence:** pytest run of 2026-11-26: the page shows the heading "This page couldn't load" instead of the error message. Screenshot: [`docs/evidence/BUG-003-taken-dates-page-crash.png`](evidence/BUG-003-taken-dates-page-crash.png).
