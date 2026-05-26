import logging
import smtplib
from email.message import EmailMessage
import config

logger = logging.getLogger(__name__)


def send_email(subject: str, html_content: str) -> bool:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = config.SENDER_EMAIL
    msg["To"] = ", ".join(config.RECIPIENT_EMAILS)
    msg.set_content("Please view this email in an HTML-capable client.")
    msg.add_alternative(html_content, subtype="html")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(config.SENDER_EMAIL, config.SENDER_APP_PASSWORD)
            smtp.send_message(msg)
        logger.info(f"Email sent successfully to {', '.join(config.RECIPIENT_EMAILS)}")
        return True
    except smtplib.SMTPAuthenticationError:
        logger.error("Gmail authentication failed — check SENDER_EMAIL and SENDER_APP_PASSWORD")
        return False
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False
