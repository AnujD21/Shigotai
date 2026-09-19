import logging

import httpx

from app.notifications.base import EmailProvider

logger = logging.getLogger(__name__)


class ResendEmailProvider(EmailProvider):
    """Real email delivery via Resend (https://resend.com). Swap for another
    provider by implementing EmailProvider the same way -- nothing else in
    the notification pipeline needs to change.
    """

    def __init__(self, api_key: str, from_address: str):
        self._api_key = api_key
        self._from_address = from_address

    def send_email(self, to: str, subject: str, html_body: str, text_body: str) -> None:
        # A flaky email provider must never break registration, password
        # reset, or match notifications -- log and move on rather than
        # propagating, matching the dev provider's "best effort" contract.
        try:
            response = httpx.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={
                    "from": self._from_address,
                    "to": [to],
                    "subject": subject,
                    "html": html_body,
                    "text": text_body,
                },
                timeout=15.0,
            )
            response.raise_for_status()
        except httpx.HTTPError:
            logger.exception("Failed to send email to %s via Resend", to)
