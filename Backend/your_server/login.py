"""
login.py — Login validation + Welcome email sender

validate_login : checks email+password against CSV
send_welcome_email : sends HTML welcome email with .whl attached
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from database import get_user_by_email


# ── Email config — set these in your environment or .env file ─────────────────
SMTP_HOST     = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER     = os.getenv("SMTP_USER", "your_email@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your_app_password")
FROM_NAME     = "Audio Classification Hub"


# ════════════════════════════════════════════════════════════════════════════
#  LOGIN VALIDATION
# ════════════════════════════════════════════════════════════════════════════

def validate_login(email: str, password: str) -> dict | None:
    """
    Check if email+password match a record in login.csv.
    Returns user dict if valid, None if invalid.
    Password is stored plain (no hashing) as requested.
    """
    user = get_user_by_email(email)
    if not user:
        return None
    if user["password"] != password:
        return None
    return user


# ════════════════════════════════════════════════════════════════════════════
#  WELCOME EMAIL
# ════════════════════════════════════════════════════════════════════════════

def _build_html_email(name: str) -> str:
    """
    Returns the HTML welcome email body.
    Uses the same design as the provided welcome email template.
    {{UserName}} is replaced with the actual name.
    """
    template = Path("template/welcome_email.html").read_text(encoding="utf-8")
    return template.replace("{{UserName}}", name)


def send_welcome_email(name: str, email: str, whl_path: str):
    """
    Send the welcome HTML email to the user with their .whl attached.
    Called as a background task after successful pipeline run.
    """
    try:
        msg = MIMEMultipart("mixed")
        msg["From"]    = f"{FROM_NAME} <{SMTP_USER}>"
        msg["To"]      = email
        msg["Subject"] = f"🎙️ Welcome to Audio Classification Hub, {name}!"

        # ── Email Body ───────────────────────────────────────────────────
        body_part = MIMEMultipart("alternative")
        
        # Plain text fallback
        text_body = f"Welcome to Audio Classification Hub, {name}!\n\nYour voice authentication journey starts here.\n\nPlease find your SDK package attached."
        body_part.attach(MIMEText(text_body, "plain"))
        
        # HTML body
        html_body = _build_html_email(name)
        body_part.attach(MIMEText(html_body, "html"))
        
        msg.attach(body_part)

        # ── Attach .whl file ─────────────────────────────────────────────
        whl_file = Path(whl_path)
        if whl_file.exists():
            with open(whl_file, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f'attachment; filename="{whl_file.name}"',
            )
            msg.attach(part)

        # ── Send ─────────────────────────────────────────────────────────
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, email, msg.as_string())

        print(f"[EMAIL] Welcome email sent to {email}")

    except Exception as e:
        # Email failure is non-critical — log but don't crash the request
        print(f"[EMAIL ERROR] Failed to send to {email}: {e}")
