import os
import smtplib
from email.mime.text import MIMEText

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

MAIL_FROM = os.getenv("MAIL_FROM")
MAIL_TO = os.getenv("MAIL_TO")  # virgüllü olabilir


def send_html_mail(subject: str, html_body: str):
    if not all([SMTP_USER, SMTP_PASSWORD, MAIL_FROM, MAIL_TO]):
        print("❌ MAIL CONFIG ERROR: Missing SMTP env vars")
        return

    msg = MIMEText(html_body, "html", "utf-8")
    msg["From"] = MAIL_FROM
    msg["To"] = MAIL_TO
    msg["Subject"] = subject

    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USER, SMTP_PASSWORD)
    server.sendmail(MAIL_FROM, MAIL_TO.split(","), msg.as_string())
    server.quit()

    print("✅ SUMMARY MAIL SENT")
