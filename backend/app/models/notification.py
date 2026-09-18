from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin, utcnow
from app.models.enums import NotificationFrequency, NotificationType


class Notification(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "notifications"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id: Mapped[str | None] = mapped_column(ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True)

    type: Mapped[NotificationType] = mapped_column(Enum(NotificationType), default=NotificationType.NEW_MATCH)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    reason_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    channel: Mapped[str] = mapped_column(String(20), default="IN_APP")
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    meta: Mapped[dict] = mapped_column(JSON, default=dict)

    job: Mapped["Job"] = relationship()


class NotificationPreference(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "notification_preferences"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    frequency: Mapped[NotificationFrequency] = mapped_column(
        Enum(NotificationFrequency), default=NotificationFrequency.INSTANT
    )
    email_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    push_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    min_match_threshold: Mapped[float] = mapped_column(Float, default=0.55)
    max_notifications_per_day: Mapped[int] = mapped_column(Integer, default=5)
    notify_new_graduate: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_visa_related: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_high_match_only: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship(back_populates="notification_preference")
