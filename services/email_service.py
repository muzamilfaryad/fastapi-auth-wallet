from email.message import EmailMessage
import smtplib
import logging

from core.config import get_settings


settings = get_settings()
logger = logging.getLogger(__name__)


def send_password_reset_email(email: str, reset_link: str) -> None:
    subject = "Reset your password"
    body = (
        f"Hello,\n\n"
        f"We received a request to reset your password.\n"
        f"Use this link to continue: {reset_link}\n\n"
        f"If you did not request this, you can ignore this email."
    )

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.smtp_user
    message["To"] = email
    message.set_content(body)

    try:
        with smtplib.SMTP(settings.smtp_server, settings.smtp_port, timeout=30) as server:
            server.ehlo()
            if settings.smtp_port == 587:
                server.starttls()
                server.ehlo()
            if settings.smtp_user and settings.smtp_password:
                server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(message)
        logger.info(f"Password reset email sent to {email}")
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error sending to {email}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error sending email to {email}: {e}")
        raise
