import logging
import smtplib
from email.message import EmailMessage

from app.notifications.base import EmailProvider

logger = logging.getLogger(__name__)


class SMTPEmailProvider(EmailProvider):
    """Email over SMTP with STARTTLS (or implicit TLS on port 465).

    Works with free relays that don't require owning a domain -- a Gmail
    account with an app password (~500 emails/day) or Brevo's free SMTP
    (300/day) -- which is what lets verify-email and password-reset reach
    real users on a $0 deployment.
    """

    def __init__(self, host: str, port: int, username: str, password: str, from_address: str):
        self._host = host
        self._port = port
        self._username = username.strip()
        # Google displays app passwords in groups ("abcd efgh ijkl mnop");
        # pasted with the spaces, the SMTP login fails.
        self._password = password.replace(" ", "") if host.strip().endswith("gmail.com") else password
        self._from_address = from_address

    def send_email(self, to: str, subject: str, html_body: str, text_body: str) -> None:
        message = EmailMessage()
        message["From"] = self._from_address
        message["To"] = to
        message["Subject"] = subject
        message.set_content(text_body)
        message.add_alternative(html_body, subtype="html")

        # Same best-effort contract as the other providers: a mail outage must
        # never break registration, password reset, or match notifications.
        try:
            if self._port == 465:
                with smtplib.SMTP_SSL(self._host, self._port, timeout=15) as server:
                    server.login(self._username, self._password)
                    server.send_message(message)
            else:
                with smtplib.SMTP(self._host, self._port, timeout=15) as server:
                    server.starttls()
                    server.login(self._username, self._password)
                    server.send_message(message)
        except (smtplib.SMTPException, OSError):
            logger.exception("Failed to send email to %s via SMTP", to)
