from datetime import datetime

from pydantic import BaseModel

from app.models.enums import NotificationFrequency, NotificationType


class NotificationOut(BaseModel):
    id: str
    type: NotificationType
    title: str
    body: str
    reason_summary: str | None
    channel: str
    is_read: bool
    sent_at: datetime
    job_id: str | None

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    items: list[NotificationOut]
    unread_count: int


class NotificationPreferenceOut(BaseModel):
    frequency: NotificationFrequency
    email_enabled: bool
    push_enabled: bool
    min_match_threshold: float
    max_notifications_per_day: int
    notify_new_graduate: bool
    notify_visa_related: bool
    notify_high_match_only: bool

    model_config = {"from_attributes": True}


class NotificationPreferenceUpdate(BaseModel):
    frequency: NotificationFrequency | None = None
    email_enabled: bool | None = None
    push_enabled: bool | None = None
    min_match_threshold: float | None = None
    max_notifications_per_day: int | None = None
    notify_new_graduate: bool | None = None
    notify_visa_related: bool | None = None
    notify_high_match_only: bool | None = None
