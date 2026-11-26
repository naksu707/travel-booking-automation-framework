"""
Small client for the Restful Booker Platform APIs, built on Playwright's APIRequestContext.

All services sit behind the website under /api/<service>:
  auth   POST /api/auth/login | /validate | /logout
  room   GET/POST /api/room/   GET/PUT/DELETE /api/room/{id}
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

    # ---------- auth ----------

    def login(self, username: str = config.ADMIN_USERNAME, password: str = config.ADMIN_PASSWORD) -> APIResponse:
        response = self._send("POST", "/api/auth/login", data={"username": username, "password": password})
        self.token = self.token_from(response)
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

    # ---------- helpers ----------

    def _send(self, method: str, path: str, **options) -> APIResponse:
        """Sends the request, retrying only gateway errors of the shared demo."""
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
