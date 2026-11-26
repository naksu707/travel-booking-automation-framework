# Defects

Defects found while testing the [Restful Booker Platform](https://automationintesting.online) public demo.
Each one has an automated check that reproduces it, left out of the normal run:
`pytest -m known_defect` and the **Known defects** folder of the Postman collection.

| ID | Title | Severity | Status | Found by |
|---|---|---|---|---|
| BUG-001 | Reading a deleted or unknown room answers 500 instead of 404 | Medium | Open | API (Playwright) and Postman |
| BUG-002 | A booking for dates in the past is accepted | High | Open | API (Playwright) and Postman |
| BUG-003 | Booking dates that are already taken crashes the reservation page | High | Open | UI (Playwright) |
| BUG-004 | Guest messages, with email and phone, can be read without logging in | Critical | Open | API (Playwright) and Postman |
| BUG-005 | Reading a deleted message answers 500 instead of 404 | Medium | Open | API (Playwright) and Postman |
| BUG-006 | The branding cannot be saved: the demo's own logo URL is rejected | High | Open | API and UI (Playwright), Postman |
| BUG-007 | Empty directions are reported as "Name should not be blank" | Low | Open | API (Playwright) and Postman |
| BUG-008 | Rooms created by the admin are never offered to guests on the website | High | Open | Integration (UI + API) |

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

---

## BUG-004 · Guest messages, with email and phone, can be read without logging in

| Field | Value |
|---|---|
| Severity | Critical |
| Priority | High |
| Component | Message API, `GET /api/message/` and `GET /api/message/{id}` |
| Environment | https://automationintesting.online (public demo) |
| Test cases | TC-MSG-11 |
| Automated checks | `test_the_list_of_messages_is_private_to_the_admin`, `test_a_message_with_contact_details_is_private_to_the_admin`, Postman **Known defects / BUG-004** |

**Steps to reproduce**

1. As a guest, send a message with the contact form (or `POST /api/message/`).
2. Without logging in (no token, or an invalid one), send `GET /api/message/`.
3. Take any `id` from the list and send `GET /api/message/{id}`, still without logging in.

**Expected result:** `403 Forbidden` for both. Only the admin may read the inbox, as already happens for marking a message as read or deleting it (both answer 403 without a token).

**Actual result:** `200 OK`. The list shows every guest's name and subject, and each message shows the guest's **email, phone number and full text**.

**Impact:** a privacy and data-protection issue. Anyone who knows the API can collect the contact details of every guest who wrote to the hotel, and guests who book also get an automatic message with their email, phone and booking dates. The rest of the API protects this kind of data: reading a booking without a token answers 403 (TC-BOOK-12).

**Evidence:** pytest run of 2026-11-26: `AssertionError: the list of messages is public, assert 200 == 403`, with no token and with an invalid token.

---

## BUG-005 · Reading a deleted message answers 500 instead of 404

| Field | Value |
|---|---|
| Severity | Medium |
| Priority | Low |
| Component | Message API, `GET /api/message/{id}` |
| Environment | https://automationintesting.online (public demo) |
| Test cases | TC-MSG-12 |
| Automated checks | `test_reading_a_deleted_message_answers_404`, Postman **Known defects / BUG-005** |

**Steps to reproduce**

1. Send a message as a guest and note its `messageid`.
2. Log in as admin and delete it: `DELETE /api/message/{id}` answers `202 Accepted`.
3. Read it: `GET /api/message/{id}`.

**Expected result:** `404 Not Found`.

**Actual result:** `500 Internal Server Error`.

**Impact:** same pattern as BUG-001 in the room API: a missing record is reported as a server failure. Since the two services behave the same way, the cause is probably shared (the database lookup does not handle "no rows found"), so fixing it in one place may fix both.

**Evidence:** pytest run of 2026-11-26: `assert 500 == 404` for `GET /api/message/30` after deleting it.

---

## BUG-006 · The branding cannot be saved: the demo's own logo URL is rejected

| Field | Value |
|---|---|
| Severity | High |
| Priority | High |
| Component | Branding API `PUT /api/branding/` and admin page `/admin/branding` |
| Environment | https://automationintesting.online (public demo), Chromium |
| Test cases | TC-BRAND-04, TC-BRAND-08 |
| Automated checks | `test_the_current_branding_can_be_saved_back_unchanged`, `test_admin_renames_the_hotel_without_touching_the_logo`, Postman **Known defects / BUG-006** |

**Steps to reproduce**

1. Read the branding: `GET /api/branding/`. The logo URL is `/images/rbp-logo.jpg`.
2. As admin, send the same branding back without changing anything: `PUT /api/branding/`.
3. In the website: log in, open **Branding**, change only the hotel name and click **Submit**.

**Expected result:** `202 Accepted`, and "Branding updated!" in the admin page.

**Actual result:** `400 Bad Request` with "Url should be a correct url format". The admin page shows the same message under the form, and nothing is saved.

**Impact:** the admin cannot change anything in the branding (name, contact details, address, directions) unless they first notice that the logo field must be rewritten as a full URL. The value the system created itself does not pass its own validation. Found by the test that saves the branding back after each branding test: it could never restore it.

**Evidence:** pytest run of 2026-11-26: every branding test failed to restore the original branding with `400 ... Url should be a correct url format`, and the admin page snapshot shows that message under the form. Workaround used by the tests: the same image with an absolute URL (`https://automationintesting.online/images/rbp-logo.jpg`), which is accepted.

---

## BUG-007 · Empty directions are reported as "Name should not be blank"

| Field | Value |
|---|---|
| Severity | Low |
| Priority | Low |
| Component | Branding API `PUT /api/branding/` |
| Environment | https://automationintesting.online (public demo) |
| Test cases | TC-BRAND-07 |
| Automated checks | `test_empty_directions_are_explained_with_the_right_field`, Postman **Known defects / BUG-007** |

**Steps to reproduce**

1. As admin, send the current branding (with an absolute logo URL) with `"directions": ""` to `PUT /api/branding/`.

**Expected result:** `400 Bad Request` with a message about the directions, for example "Directions should not be blank".

**Actual result:** `400 Bad Request` with **"Name should not be blank"**, although the name is filled in.

**Impact:** the admin is told to fix a field that is already correct, and cannot tell from the message that the directions are missing. The message of the name field was reused for the directions field.

**Evidence:** pytest run of 2026-11-26: `the error does not mention the directions: ['Name should not be blank', ...]`.

---

## BUG-008 · Rooms created by the admin are never offered to guests on the website

| Field | Value |
|---|---|
| Severity | High |
| Priority | High |
| Component | Website home page, **Our Rooms** section |
| Environment | https://automationintesting.online (public demo), Chromium |
| Test cases | TC-INT-05 |
| Automated check | `test_a_room_created_by_the_admin_is_offered_on_the_website` |

**Steps to reproduce**

1. Log in as admin and create a room, in the admin panel or with `POST /api/room/` (for example a Family room for £345).
2. Check that it exists: `GET /api/room/` lists it, and it shows in `/admin/rooms`.
3. Open the home page and look at **Our Rooms**. Reload several times over a minute and a half.

**Expected result:** the new room is shown with its description, type and price, and a **Book now** button.

**Actual result:** only the three original rooms (Single, Double, Suite) are shown, even after reloading for more than 90 seconds. The new room can only be booked by someone who already knows its address (`/reservation/{room id}`).

**Impact:** rooms the hotel adds cannot be found or booked by guests from the website, which is lost revenue for every new room. The admin has no sign that anything is wrong: the room appears in the admin panel and in the API.

**Evidence:** pytest run of 2026-11-26: room 87 was created (the API lists it), and the home page snapshot after 90 seconds of reloading shows only rooms 1, 2 and 3. Seen in two separate runs.
