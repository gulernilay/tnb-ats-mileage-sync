"""
Logger module for ATS Mileage Sync application.

This module provides logging functionality with file output and optional email notifications.
It includes configuration for SMTP mail settings and public API functions for different log levels.
"""

import logging
import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv
load_dotenv()


# =========================
# Mail Logger Config
# =========================
MAIL_ENABLED = os.getenv("MAIL_LOG_ENABLED", "false").lower() in ("1", "true", "yes")

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

MAIL_FROM = os.getenv("MAIL_FROM")
MAIL_TO = os.getenv("MAIL_TO")  # comma-separated list allowed


# =========================
# File Logger Setup
# =========================
logger = logging.getLogger("ATS_MILEAGE")
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler("ats_mileage.log", encoding="utf-8")
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
)
handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(handler)


# =========================
# Mail Sender Function
# =========================
def _send_mail(subject: str, body: str):
    if not MAIL_ENABLED:
        print(f"DEBUG MAIL: Mail disabled, skipping email for subject: {subject}")
        return

    if not all([SMTP_HOST, SMTP_USER, SMTP_PASSWORD, MAIL_FROM, MAIL_TO]):
        print("❌ DEBUG MAIL ERROR: Missing SMTP env vars")
        logger.error("MAIL CONFIG ERROR | Missing SMTP env vars")
        return

    print(f"DEBUG MAIL: Connecting to SMTP {SMTP_HOST}:{SMTP_PORT}")

    msg = EmailMessage()
    msg["From"] = MAIL_FROM
    msg["To"] = [x.strip() for x in MAIL_TO.split(",")]
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            server.set_debuglevel(1)  # 🔥 çok önemli
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)

        print("✅ DEBUG MAIL: Email sent successfully")

    except Exception as e:
        print(f"❌ DEBUG MAIL ERROR: {e}")
        logger.error(f"MAIL SEND ERROR | {str(e)}")


# =========================
# Public Logger API
# =========================
def log_info(message: str):
    """
    Log an informational message.

    Logs the message to file and sends an email notification.

    Args:
        message: The informational message to log
    """
    print(f"DEBUG LOG_INFO: {message}")
    logger.info(message)

def log_error(message: str):
    """
    Log an error message.

    Logs the message to file and sends an email notification.

    Args:
        message: The error message to log
    """
    print(f"DEBUG LOG_ERROR: {message}")
    logger.error(message)
    _send_mail(
        subject="ATS Mileage | ERROR",
        body=message
    )


def log_debug(message: str):
    """
    Log a debug message.

    Logs the message to file only (no email notification for debug messages).

    Args:
        message: The debug message to log
    """
    print(f"DEBUG LOG_DEBUG: {message}")
    logger.debug(message)
    # Debug messages typically don't need email notifications
