# Defects

Defects found while testing the [Restful Booker Platform](https://automationintesting.online) public demo.
Each one has an automated check that reproduces it, left out of the normal run:
`pytest -m known_defect` and the **Known defects** folder of the Postman collection.

| ID | Title | Severity | Status | Found by |
|---|---|---|---|---|
| BUG-001 | Reading a deleted or unknown room answers 500 instead of 404 | Medium | Open | API (Playwright) and Postman |

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
