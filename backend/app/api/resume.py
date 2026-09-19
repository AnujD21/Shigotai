from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.profile import ResumeExtractionResult
from app.services.profile_service import get_or_create_profile
from app.services.resume_service import parse_resume
from app.storage.provider import get_file_storage

router = APIRouter(prefix="/resume", tags=["resume"])

_ALLOWED_EXTENSIONS = {".pdf", ".docx"}
_ALLOWED_CONTENT_TYPES = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
_MAX_SIZE_BYTES = 5 * 1024 * 1024


@router.post("/upload", response_model=ResumeExtractionResult)
async def upload_resume(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    extension = Path(file.filename or "").suffix.lower()
    if extension not in _ALLOWED_EXTENSIONS:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Only PDF and DOCX resumes are supported.")

    content = await file.read()
    if len(content) > _MAX_SIZE_BYTES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Resume file is too large (5MB max).")

    try:
        result = parse_resume(file.filename, content)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc

    profile = get_or_create_profile(db, current_user.id)
    storage = get_file_storage()
    stored_ref = storage.save(
        key=f"resumes/{current_user.id}/resume{extension}",
        content=content,
        content_type=_ALLOWED_CONTENT_TYPES[extension],
    )

    profile.resume_file_path = stored_ref
    profile.resume_original_filename = file.filename
    db.commit()

    return result
