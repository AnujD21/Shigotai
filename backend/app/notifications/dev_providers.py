"""Dev-mode notification providers: no external service required.

Emails are written to backend/var/outbox/ as .html files instead of being
sent, so the notification pipeline is fully exercised and inspectable without
an EMAIL_API_KEY. Swap in a real provider (Resend/SendGrid) behind the same
EmailProvider interface for production -- see README "Adding a notification
provider".
"""

import re
from pathlib import Path

from app.notifications.base import EmailProvider, PushProvider

_OUTBOX_DIR = Path(__file__).resolve().parents[2] / "var" / "outbox"


class DevEmailProvider(EmailProvider):
    def send_email(self, to: str, subject: str, html_body: str, text_body: str) -> None:
        _OUTBOX_DIR.mkdir(parents=True, exist_ok=True)
        safe_subject = re.sub(r"[^a-zA-Z0-9-_]", "_", subject)[:60]
        from datetime import datetime, timezone

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
        path = _OUTBOX_DIR / f"{timestamp}__{to}__{safe_subject}.html"
        path.write_text(
            f"<!-- To: {to} -->\n<!-- Subject: {subject} -->\n{html_body}\n\n<!-- Plain text fallback:\n{text_body}\n-->",
            encoding="utf-8",
        )


class DevPushProvider(PushProvider):
    def send_push(self, user_id: str, title: str, body: str, url: str) -> None:
        # No browser push transport in dev mode; in-app notifications already
        # cover this. Real deployments wire pywebpush + WEB_PUSH_* keys here.
        return None
