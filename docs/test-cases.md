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
| TC-ROOM-11 | Every room type can be created | Postman run with `room-types.csv` (Single, Double, Twin, Family, Suite) | Each iteration creates, reads, updates and deletes the room | PM | Medium |

## Test data

- Every test creates its own rooms with a unique name (`QA1234` from pytest, `PM1234` from Postman) and deletes them at the end, so runs never depend on the demo's data or leave rooms behind.
- The demo is shared and resets regularly; no test relies on rooms that already exist.
