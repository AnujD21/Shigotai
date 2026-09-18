from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.notification import Notification, NotificationPreference
from app.models.user import User
from app.schemas.notification import (
    NotificationListResponse,
    NotificationPreferenceOut,
    NotificationPreferenceUpdate,
)

router = APIRouter(tags=["notifications"])


@router.get("/notifications", response_model=NotificationListResponse)
def get_notifications(limit: int = 30, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.sent_at.desc())
        .limit(min(100, limit))
        .all()
    )
    unread = db.query(Notification).filter(Notification.user_id == current_user.id, Notification.is_read.is_(False)).count()
    return NotificationListResponse(items=items, unread_count=unread)


@router.put("/notifications/{notification_id}/read", status_code=status.HTTP_204_NO_CONTENT)
def mark_read(notification_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.user_id == current_user.id)
        .first()
    )
    if not notification:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Notification not found.")
    notification.is_read = True
    db.commit()
    return None


@router.put("/notifications/read-all", status_code=status.HTTP_204_NO_CONTENT)
def mark_all_read(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(Notification).filter(Notification.user_id == current_user.id, Notification.is_read.is_(False)).update(
        {"is_read": True}
    )
    db.commit()
    return None


@router.get("/notification-preferences", response_model=NotificationPreferenceOut)
def get_preferences(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pref = db.query(NotificationPreference).filter(NotificationPreference.user_id == current_user.id).first()
    if not pref:
        pref = NotificationPreference(user_id=current_user.id)
        db.add(pref)
        db.commit()
        db.refresh(pref)
    return pref


@router.put("/notification-preferences", response_model=NotificationPreferenceOut)
def update_preferences(
    payload: NotificationPreferenceUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    pref = db.query(NotificationPreference).filter(NotificationPreference.user_id == current_user.id).first()
    if not pref:
        pref = NotificationPreference(user_id=current_user.id)
        db.add(pref)
        db.flush()
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(pref, field, value)
    db.commit()
    db.refresh(pref)
    return pref
