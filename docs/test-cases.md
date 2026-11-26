# Test cases

Application under test: [Restful Booker Platform](https://automationintesting.online) (public demo).
Admin credentials: `admin` / `password` (public demo data).

**Layers:** UI = Playwright browser test · API = Playwright `APIRequestContext` test · PM = Postman collection run with Newman.

## Authentication

| ID | Title | Steps | Expected result | Layers | Priority |
|---|---|---|---|---|---|
| TC-AUTH-01 | Admin logs in with valid credentials | Open `/admin`, enter `admin` / `password`, click **Login** | The admin rooms page `/admin/rooms` opens and the **Logout** button is shown | UI | Critical |
| TC-AUTH-02 | Login is rejected with a wrong password | Log in with `admin` / `wrong-password` | "Invalid credentials" is shown and the user stays on the login page | UI, API, PM | Critical |
| TC-AUTH-03 | Login is rejected with an unknown username | Log in with `unknown-user` / `password` | "Invalid credentials" is shown (UI); the API answers 403 | UI, API | High |
| TC-AUTH-04 | Login is rejected with empty fields | Click **Login** with both fields empty | "Invalid credentials" is shown (UI); the API answers 403 | UI, API | High |
| TC-AUTH-05 | Admin logs out | Log in, click **Logout** | The front page `/` opens | UI | High |
| TC-AUTH-06 | Admin pages require login | Open `/admin/rooms` without logging in | The login page `/admin` is shown | UI | Critical |
| TC-AUTH-07 | Login sets a token cookie | `POST /api/auth/login` with valid credentials | 200, and a `token` cookie is set | API, PM | Critical |
| TC-AUTH-08 | A valid token is accepted | `POST /api/auth/validate` with the token from login | 200 | API, PM | High |
| TC-AUTH-09 | An invalid token is rejected | `POST /api/auth/validate` with `not-a-real-token` | 403 | API, PM | High |
| TC-AUTH-10 | A token stops working after logout | Log in, `POST /api/auth/logout` with the token, then validate it | Logout answers 200; validate answers 403 | API | High |

## Rooms

| ID | Title | Steps | Expected result | Layers | Priority |
|---|---|---|---|---|---|
| TC-ROOM-01 | The room list is public | `GET /api/room/` without a token | 200, with a `rooms` list; every room has `roomid`, `roomName`, `type`, `accessible`, `roomPrice` | API, PM | High |
| TC-ROOM-02 | Admin creates a room | `POST /api/room/` with a valid room and the admin token | 201; the room is returned with its new `roomid` and the data that was sent | API, PM | Critical |
| TC-ROOM-03 | A created room can be read by its id | Create a room, then `GET /api/room/{id}` | 200, with the same room name | API, PM | High |
| TC-ROOM-04 | Admin updates a room | Create a room, `PUT /api/room/{id}` with a new price and type | 202; reading the room shows the new values | API, PM | High |
| TC-ROOM-05 | Admin deletes a room | Create a room, `DELETE /api/room/{id}`, then list the rooms | Delete answers 202; the room is no longer in the list | API, PM | High |
| TC-ROOM-12 | Reading a deleted or unknown room answers 404 | Read a deleted room, and a room id that never existed (`999999`) | 404 Not Found. **Fails: BUG-001** (500 Internal Server Error) | API, PM | Medium |
| TC-ROOM-06 | A room cannot be created without a token | `POST /api/room/` with no token cookie | 403 | API, PM | Critical |
| TC-ROOM-07 | A room cannot be created with an invalid token | `POST /api/room/` with `token=not-a-real-token` | 403 | API | High |
| TC-ROOM-08 | An unknown room type is rejected | Create a room with type `Penthouse` | 400, with "Type can only contain the room options Single, Double, Twin, Family or Suite" | API, PM | Medium |
| TC-ROOM-09 | An empty room name is rejected | Create a room with an empty name | 400, with "Room name must be set" | API | Medium |
| TC-ROOM-10 | Prices outside 1–999 are rejected | Create rooms with price 0 and 1000 | 400 for both | API | Medium |
| TC-ROOM-13 | Admin creates a room from the rooms page | Log in, fill name, type Suite, accessible, price 275 and WiFi, click **Create** | The room is listed with its type and price, and the API has it with the same data | UI, API | High |
| TC-ROOM-14 | A room without a name is not created | Click **Create** with an empty name | "Room name must be set" is shown and no room is added | UI | Medium |
| TC-ROOM-15 | Admin deletes a room from the rooms page | Click the delete icon of a room | The row disappears and the API no longer lists the room | UI, API | High |
| TC-ROOM-11 | Every room type can be created | Postman run with `room-types.csv` (Single, Double, Twin, Family, Suite) | Each iteration creates, reads, updates and deletes the room | PM | Medium |

## Guest booking

| ID | Title | Steps | Expected result | Layers | Priority |
|---|---|---|---|---|---|
| TC-BOOK-01 | Guest books a room | Open a room with free dates, click **Reserve Now**, fill first name, last name, email and phone, click **Reserve Now** | "Booking Confirmed" is shown with the check-in and check-out dates | UI, API, PM | Critical |
| TC-BOOK-02 | Price summary | Open a £120 room for 3 nights | Total is £400: 3 × £120 + £25 cleaning fee + £15 service fee | UI | High |
| TC-BOOK-03 | Guest details are required | Click **Reserve Now** with the form empty | "Firstname should not be blank" and "Lastname should not be blank" are shown; no booking is made | UI, API, PM | High |
| TC-BOOK-04 | Invalid email is rejected | Book with email `not-an-email` | An error is shown (UI); 400 with a message (API) | UI, API | Medium |
| TC-BOOK-05 | Name and phone lengths are checked | Book with first name of 2 or 19 letters, last name of 2 letters, phone of 3 or 22 digits | 400 with a message for each | API | Medium |
| TC-BOOK-06 | The same dates cannot be booked twice | Book a room, then book the same dates again (API, Postman, UI) | 409 Conflict (API); an error message and no confirmation (UI). **UI fails: BUG-003** (the page crashes) | UI, API, PM | Critical |
| TC-BOOK-07 | Overlapping dates cannot be booked | Book 4 nights, then book dates that start 2 days later | 409 Conflict | API, PM | Critical |
| TC-BOOK-08 | A stay can start the day the previous one ends | Book a stay, then book from its check-out day | 201 Created | API | High |
| TC-BOOK-09 | Check-out must be after check-in | Book with check-out on the check-in day, and before it | 409 Conflict | API, PM | High |
| TC-BOOK-10 | A booking in the past is rejected | Book dates that ended a week ago | 400 or 409. **Fails: BUG-002** (201 Created) | API, PM | High |
| TC-BOOK-11 | Admin reads and lists bookings | With the admin token, read a booking by id and list the bookings of its room | 200 with the guest's data | API, PM | High |
| TC-BOOK-12 | Guest data is private | Read a booking or the room's bookings without a token, or with an invalid one | 403 Forbidden | API, PM | Critical |
| TC-BOOK-13 | Admin deletes a booking | Delete a booking, then read it | 202, then 404 | API, PM | High |
| TC-BOOK-14 | Deleting a booking frees its dates | Delete a booking, then book the same dates | 201 Created | API | Medium |
| TC-BOOK-15 | A guest cannot delete a booking | Delete a booking without a token | 403 Forbidden | API | Critical |
| TC-BOOK-16 | Cancel returns to the calendar | Click **Reserve Now**, then **Cancel** | The calendar and **Reserve Now** are shown again, without the form | UI | Low |

## Contact form and admin inbox

| ID | Title | Steps | Expected result | Layers | Priority |
|---|---|---|---|---|---|
| TC-MSG-01 | Guest sends a message | Fill name, email, phone, subject and message on the home page and click **Submit** | "Thanks for getting in touch {name}!" with the subject (UI); 201 with the message (API) | UI, API, PM | Critical |
| TC-MSG-02 | Empty form shows every missing field | Click **Submit** with the form empty | "may not be blank" for name, email, phone, subject and message | UI | High |
| TC-MSG-03 | Field lengths are checked | Phone of 10 or 22 digits, subject of 4 or 101 letters, message of 17 or 2001 letters | 400 and the rule for that field ("Phone must be between 11 and 21 characters.", etc.) | UI, API, PM | Medium |
| TC-MSG-04 | Invalid or empty email is rejected | Send with email empty and `not-an-email` | 400 with a message | API | Medium |
| TC-MSG-05 | Phone lengths at the limits are accepted | Send with phones of 11 and 21 digits | 201 Created | API | Low |
| TC-MSG-06 | New message is unread in the inbox | Send a message, open `/admin/message` | The row shows the name and subject, marked unread | UI, API, PM | High |
| TC-MSG-07 | Admin opens a message | Click the message | The pop-up shows name, phone, email, subject and message | UI, API | High |
| TC-MSG-08 | An opened message is marked as read | Open and close the message, reload the inbox | The row is marked read (UI); `read` is true (API) | UI, API, PM | Medium |
| TC-MSG-09 | Admin deletes a message | Click the delete icon of the message | The row disappears and the API no longer lists it | UI, API, PM | High |
| TC-MSG-10 | A guest cannot change messages | Mark as read and delete without a token, or with an invalid one | 403 Forbidden | API, PM | Critical |
| TC-MSG-11 | Messages are private to the admin | List messages and read one without a token, or with an invalid one | 403 Forbidden. **Fails: BUG-004** (200 OK, email and phone exposed) | API, PM | Critical |
| TC-MSG-12 | Reading a deleted message answers 404 | Delete a message, then read it | 404 Not Found. **Fails: BUG-005** (500 Internal Server Error) | API, PM | Medium |

## UI vs. API consistency

| ID | Title | Steps | Expected result | Layers | Priority |
|---|---|---|---|---|---|
| TC-INT-01 | A booking made in the website is saved | Book in the website, then list the room's bookings through the API | Exactly one booking, with the guest's name and the same dates | UI + API | Critical |
| TC-INT-02 | Dates booked in the website are taken | Book in the website, then book the same dates through the API | 409 Conflict | UI + API | Critical |
| TC-INT-03 | A message sent in the website reaches the admin | Send the contact form, then find the message through the API | The message is listed and has the same name, email, phone and text | UI + API | Critical |
| TC-INT-05 | A room created by the admin is offered on the website | Create a Family room for £345 through the API, open the home page | A room card with its description, type and price. **Fails: BUG-008** (only the three original rooms are shown) | UI + API | High |
| TC-INT-06 | Branding changed by the admin reaches the website | Update the branding through the API, open the home page | The new name, address, phone, email and directions, and the name in the footer | UI + API | Medium |
| TC-INT-04 | A booking notifies the admin | Book in the website, then look for the notification through the API | A "You have a new booking!" message from the guest, with the booking dates, email and phone | UI + API | High |

## Branding

| ID | Title | Steps | Expected result | Layers | Priority |
|---|---|---|---|---|---|
| TC-BRAND-01 | The branding is public and complete | `GET /api/branding/` | 200 with name, description, logo, directions, map, contact and address | API, PM | Medium |
| TC-BRAND-02 | The website shows the hotel branding | Open the home page | "Welcome to {name}", the address, phone and email in **Our Location**, the name in the footer | UI | Medium |
| TC-BRAND-03 | Admin updates the branding | `PUT /api/branding/` with new name, directions, email and address | 202, and reading the branding shows the new values | API, PM | High |
| TC-BRAND-04 | Admin renames the hotel from the branding page | Change the name (and the logo to a full URL) in `/admin/branding` and click **Submit** | "Branding updated!" and the API has the new name | UI | Medium |
| TC-BRAND-08 | The branding can be saved without changing the logo | Save the current branding unchanged (API), or change only the name in `/admin/branding` (UI) | 202 / "Branding updated!". **Fails: BUG-006** (400, "Url should be a correct url format") | UI, API, PM | High |
| TC-BRAND-05 | A guest cannot change the branding | `PUT /api/branding/` with no token, or an invalid one | 403, and the branding is unchanged | API, PM | Critical |
| TC-BRAND-06 | Invalid branding is rejected with an explanation | Name with numbers or empty, invalid logo URL, description with numbers, contact name with numbers, invalid email, empty address line 1 or post code | 400 with the rule for that field; the branding is unchanged | UI, API, PM | Medium |
| TC-BRAND-07 | Empty directions are explained with the right field | Update the branding with empty directions | 400 with a message about the directions. **Fails: BUG-007** ("Name should not be blank") | API, PM | Low |

## Test data

- Booking tests create a new room for each test, so their dates are always free, and delete the bookings and the room at the end.
- The branding is shared by everyone who uses the demo: tests that change it save the original and always restore it, with the logo as a full URL because the demo's own relative one is rejected (BUG-006).
- Every test creates its own rooms with a unique name (`QA1234` from pytest, `PM1234` from Postman) and deletes them at the end, so runs never depend on the demo's data or leave rooms behind.
- The demo is shared and resets regularly; no test relies on rooms that already exist.
