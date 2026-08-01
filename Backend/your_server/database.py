"""
database.py — All database read/write operations
Storage: CSV file (Database/login.csv) + per-user folders

CSV Columns:
    name, email, password, username, registered_at, whl_path
"""

import csv
import os
from pathlib import Path
from datetime import datetime

# Resolve BASE_DB relative to this file's location so it works regardless of CWD
BASE_DB   = Path(__file__).parent.parent.parent / "DataBase"
LOGIN_CSV = BASE_DB / "login.csv"

# Columns in the CSV
COLUMNS = ["name", "email", "password", "username", "registered_at", "whl_path"]


# ── Ensure Database folder and CSV exist ─────────────────────────────────────

def _ensure_csv():
    BASE_DB.mkdir(parents=True, exist_ok=True)
    if not LOGIN_CSV.exists():
        with open(LOGIN_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS)
            writer.writeheader()


# ── Read all users ────────────────────────────────────────────────────────────

def _read_all() -> list:
    _ensure_csv()
    with open(LOGIN_CSV, "r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ── Write all users (full overwrite) ─────────────────────────────────────────

def _write_all(rows: list):
    _ensure_csv()
    with open(LOGIN_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


# ════════════════════════════════════════════════════════════════════════════
#  PUBLIC FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════

def user_exists(email: str) -> bool:
    """Check if an email is already registered."""
    rows = _read_all()
    return any(r["email"].lower() == email.lower() for r in rows)


def create_user(name: str, email: str, password: str, username: str) -> dict:
    """
    Add a new user row to login.csv.
    Also creates Database/<username>/ folder.
    Returns the new user dict.
    """
    _ensure_csv()

    # Create user folder in Database/
    user_folder = BASE_DB / username
    user_folder.mkdir(parents=True, exist_ok=True)
    (user_folder / "voices").mkdir(exist_ok=True)

    new_user = {
        "name": name,
        "email": email,
        "password": password,      # stored plain as requested (no hashing)
        "username": username,
        "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "whl_path": "",
    }

    rows = _read_all()
    rows.append(new_user)
    _write_all(rows)

    return new_user


def get_user_by_email(email: str) -> dict | None:
    """Return the user row dict for a given email, or None if not found."""
    rows = _read_all()
    for r in rows:
        if r["email"].lower() == email.lower():
            return r
    return None


def get_user_by_username(username: str) -> dict | None:
    """Return the user row dict for a given username, or None."""
    rows = _read_all()
    for r in rows:
        if r["username"].lower() == username.lower():
            return r
    return None


def save_whl_path(email: str, whl_path: str):
    """
    Update the whl_path column for the user with this email.
    Called after a successful .whl build.
    """
    rows = _read_all()
    for r in rows:
        if r["email"].lower() == email.lower():
            r["whl_path"] = str(whl_path)
            break
    _write_all(rows)


def get_whl_path(email: str) -> str | None:
    """Return the whl_path for a user, or None if not built yet."""
    user = get_user_by_email(email)
    if user and user.get("whl_path"):
        return user["whl_path"]
    return None


def get_all_users() -> list:
    """Return all user rows (admin use)."""
    return _read_all()


def delete_user(email: str) -> bool:
    """Remove a user from the CSV. Returns True if found and deleted."""
    rows = _read_all()
    new_rows = [r for r in rows if r["email"].lower() != email.lower()]
    if len(new_rows) == len(rows):
        return False   # user not found
    _write_all(new_rows)
    return True
