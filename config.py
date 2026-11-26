"""Settings read from environment variables, with defaults for the public demo."""
import os

BASE_URL = os.getenv("BASE_URL", "https://automationintesting.online").rstrip("/")

# Public demo credentials, documented by Restful Booker Platform itself
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "password")
