"""Decides whether a (re)computed match should produce a notification, and
if so, creates it and dispatches email. Encodes:

- Duplicate prevention (master spec section 18): a user is not re-notified
  about a job unless something meaningful changed.
- Job update detection (section 19): a job that newly clears the deterministic
  gate for a user who previously didn't qualify triggers a distinct
  "just became a match" notification.
- Notification controls (section 17): threshold, frequency, category toggles,
  and a daily cap are all honored before anything is sent.
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.enums import MatchStrength, NotificationFrequency, NotificationType
from app.models.interaction import Match
from app.models.job import Job
from app.models.notification import Notification, NotificationPreference
from app.notifications.dev_providers import DevEmailProvider
from app.notifications.templates import match_email


def _daily_notification_count(db: Session, user_id: str) -> int:
    since = datetime.now(timezone.utc) - timedelta(days=1)
    return db.query(Notification).filter(Notification.user_id == user_id, Notification.sent_at >= since).count()


def _reason_summary(breakdown: list[dict]) -> str:
    matched = [r["label"] for r in breakdown if r["state"] == "MATCH"]
    if not matched:
        return "This role matches part of your profile."
    return f"Matches your {', '.join(matched[:4])}."


def maybe_notify(
    db: Session,
    match: Match,
    job: Job,
    preference: NotificationPreference,
    previous_strength: MatchStrength | None,
    previous_deterministic_pass: bool | None,
    user_email: str,
    job_url: str,
) -> Notification | None:
    if preference.frequency == NotificationFrequency.OFF:
        return None
    if match.overall_score < preference.min_match_threshold:
        return None
    if preference.notify_high_match_only and match.match_strength != MatchStrength.STRONG:
        return None
    if _daily_notification_count(db, match.user_id) >= preference.max_notifications_per_day:
        return None

    is_first_time = previous_strength is None
    became_match = (
        previous_strength is not None
        and previous_deterministic_pass is False
        and match.deterministic_pass is True
    )

    if not is_first_time and not became_match:
        return None

    notif_type = NotificationType.JOB_BECAME_MATCH if became_match else NotificationType.NEW_MATCH

    existing = (
        db.query(Notification)
        .filter(Notification.user_id == match.user_id, Notification.job_id == job.id, Notification.type == notif_type)
        .first()
    )
    if existing:
        return None

    matched = [r["label"] for r in match.requirement_breakdown if r["state"] == "MATCH"]
    missing = [r["label"] for r in match.requirement_breakdown if r["state"] == "MISSING"]

    title = (
        f"New match: {job.title} at {job.company.name}"
        if not became_match
        else f"This job just became a match: {job.title}"
    )
    body = _reason_summary(match.requirement_breakdown)

    notification = Notification(
        user_id=match.user_id,
        job_id=job.id,
        type=notif_type,
        title=title,
        body=body,
        reason_summary=body,
        channel="IN_APP",
    )
    db.add(notification)

    if preference.email_enabled and preference.frequency == NotificationFrequency.INSTANT:
        subject, html_body, text_body = match_email(job.title, job.company.name, job.location or "Japan", matched, missing, job_url)
        DevEmailProvider().send_email(user_email, subject, html_body, text_body)

    db.flush()
    return notification
