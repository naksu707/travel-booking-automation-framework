"""
Small client for the Restful Booker Platform APIs, built on Playwright's APIRequestContext.

All services sit behind the website under /api/<service>:
  auth   POST /api/auth/login | /validate | /logout
  room   GET/POST /api/room/   GET/PUT/DELETE /api/room/{id}
  message POST /api/message/ (public)   GET /api/message/ | /count | /{id}   PUT /api/message/{id}/read   DELETE /api/message/{id}
  branding GET /api/branding/ (public)   PUT /api/branding/ (admin)
  booking POST /api/booking/ (public)   GET /api/booking/?roomid=   GET/PUT/DELETE /api/booking/{id} (admin)

Logging in does not return the token in the body: the auth service sets a cookie named "token",
and the room service reads that cookie on create, update and delete.
"""
import time

from playwright.sync_api import APIRequestContext, APIResponse

import config

# The shared public demo sometimes answers 502/503/504 for a few seconds while it restarts.
# Those gateway errors are retried; every other status goes straight to the test.
GATEWAY_ERRORS = {502, 503, 504}
RETRIES = 3


class RestfulBookerApi:

    def __init__(self, request: APIRequestContext):
        self.request = request
        self.token: str | None = None
        self._credentials: tuple[str, str] | None = None

    # ---------- auth ----------

    def login(self, username: str = config.ADMIN_USERNAME, password: str = config.ADMIN_PASSWORD) -> APIResponse:
        response = self._send_once("POST", "/api/auth/login", data={"username": username, "password": password})
        self.token = self.token_from(response)
        self._credentials = (username, password) if self.token else None
        return response

    def validate(self, token: str) -> APIResponse:
        return self._send("POST", "/api/auth/validate", data={"token": token})

    def logout(self, token: str) -> APIResponse:
        return self._send("POST", "/api/auth/logout", data={"token": token})

    # ---------- rooms ----------

    def list_rooms(self) -> APIResponse:
        return self._send("GET", "/api/room/")

    def get_room(self, room_id: int) -> APIResponse:
        return self._send("GET", f"/api/room/{room_id}")

    def create_room(self, room: dict, token: str | None = "current") -> APIResponse:
        return self._send("POST", "/api/room/", data=room, headers=self._auth_cookie(token))

    def update_room(self, room_id: int, room: dict, token: str | None = "current") -> APIResponse:
        return self._send("PUT", f"/api/room/{room_id}", data=room, headers=self._auth_cookie(token))

    def delete_room(self, room_id: int, token: str | None = "current") -> APIResponse:
        return self._send("DELETE", f"/api/room/{room_id}", headers=self._auth_cookie(token))

    # ---------- bookings ----------

    def create_booking(self, booking: dict) -> APIResponse:
        """Guests book without logging in, so no token is sent."""
        return self._send("POST", "/api/booking/", data=booking)

    def get_booking(self, booking_id: int, token: str | None = "current") -> APIResponse:
        return self._send("GET", f"/api/booking/{booking_id}", headers=self._auth_cookie(token))

    def list_bookings(self, room_id: int, token: str | None = "current") -> APIResponse:
        return self._send("GET", "/api/booking/", params={"roomid": str(room_id)}, headers=self._auth_cookie(token))

    def update_booking(self, booking_id: int, booking: dict, token: str | None = "current") -> APIResponse:
        return self._send("PUT", f"/api/booking/{booking_id}", data=booking, headers=self._auth_cookie(token))

    def delete_booking(self, booking_id: int, token: str | None = "current") -> APIResponse:
        return self._send("DELETE", f"/api/booking/{booking_id}", headers=self._auth_cookie(token))

    # ---------- messages ----------

    def send_message(self, message: dict) -> APIResponse:
        """Guests use the contact form without logging in, so no token is sent."""
        return self._send("POST", "/api/message/", data=message)

    def list_messages(self, token: str | None = "current") -> APIResponse:
        return self._send("GET", "/api/message/", headers=self._auth_cookie(token))

    def get_message(self, message_id: int, token: str | None = "current") -> APIResponse:
        return self._send("GET", f"/api/message/{message_id}", headers=self._auth_cookie(token))

    def unread_count(self, token: str | None = "current") -> APIResponse:
        return self._send("GET", "/api/message/count", headers=self._auth_cookie(token))

    def mark_message_read(self, message_id: int, token: str | None = "current") -> APIResponse:
        return self._send("PUT", f"/api/message/{message_id}/read", headers=self._auth_cookie(token))

    def delete_message(self, message_id: int, token: str | None = "current") -> APIResponse:
        return self._send("DELETE", f"/api/message/{message_id}", headers=self._auth_cookie(token))

    def find_message(self, subject: str) -> dict | None:
        """The message summary (id, name, subject, read) with this subject, or None."""
        messages = self.list_messages().json()["messages"]
        return next((m for m in messages if m["subject"] == subject), None)

    # ---------- branding ----------

    def get_branding(self) -> APIResponse:
        return self._send("GET", "/api/branding/")

    def update_branding(self, branding: dict, token: str | None = "current") -> APIResponse:
        return self._send("PUT", "/api/branding/", data=branding, headers=self._auth_cookie(token))

    # ---------- helpers ----------

    def _send(self, method: str, path: str, **options) -> APIResponse:
        """Sends the request, retrying only gateway errors of the shared demo.

        The demo also resets its database every few minutes, which ends every login. If a
        request made with this client's own admin token answers 403, the client logs in again
        once and repeats it; a request with no token or another token is never repeated."""
        response = self._send_once(method, path, **options)
        sent_cookie = options.get("headers", {}).get("Cookie", "")
        if response.status == 403 and self._credentials and self.token and sent_cookie == f"token={self.token}":
            self.login(*self._credentials)
            options["headers"] = {**options["headers"], "Cookie": f"token={self.token}"}
            response = self._send_once(method, path, **options)
        return response

    def _send_once(self, method: str, path: str, **options) -> APIResponse:
        for attempt in range(1, RETRIES + 1):
            response = self.request.fetch(path, method=method, **options)
            if response.status not in GATEWAY_ERRORS or attempt == RETRIES:
                return response
            time.sleep(attempt * 2)

    def _auth_cookie(self, token: str | None) -> dict:
        """token="current" uses the token of the last login; None sends no cookie at all."""
        value = self.token if token == "current" else token
        return {"Cookie": f"token={value}"} if value else {}

    @staticmethod
    def token_from(response: APIResponse) -> str | None:
        """Reads the "token" cookie from the Set-Cookie header of a login response."""
        for header in response.headers_array:
            if header["name"].lower() == "set-cookie" and header["value"].startswith("token="):
                return header["value"].split(";", 1)[0].removeprefix("token=")
        return None
