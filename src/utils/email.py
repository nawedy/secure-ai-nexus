from fastapi import HTTPException
from src.config.settings import settings
import smtplib
from email.mime.text import MIMEText

def send_password_reset_email(email: str, token: str):
    try:
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"

        msg = MIMEText(f"Please click on the following link to reset your password: {reset_link}")
        msg['Subject'] = "Password Reset Request"
        msg['From'] = settings.SMTP_USERNAME
        msg['To'] = email

        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))