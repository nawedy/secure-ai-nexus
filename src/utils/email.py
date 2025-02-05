import smtplib
from email.mime.text import MIMEText
from src.config.settings import settings
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


async def send_contact_email(name: str, email: str, message: str):
    """
    Sends a contact email.

    Args:
        name: Name of the sender.
        email: Email of the sender.
        message: Message of the sender.

    Returns:
        None
    """
    try:
        # Create email message
        msg = MIMEText(f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}")
        msg["Subject"] = f"Contact Form Submission from {name}"
        msg["From"] = settings.SMTP_USERNAME
        msg["To"] = "contact@getaisecured.com"

        # Send email
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error when sending contact email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error sending contact email",
        )
    except Exception as e:
        logger.error(f"Error sending contact email: {e}")
        raise e
