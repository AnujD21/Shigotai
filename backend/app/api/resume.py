from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.profile import ResumeExtractionResult
from app.services.profile_service import get_or_create_profile
from app.services.resume_service import parse_resume

router = APIRouter(prefix="/resume", tags=["resume"])

_ALLOWED_EXTENSIONS = {".pdf", ".docx"}
_MAX_SIZE_BYTES = 5 * 1024 * 1024
_STORAGE_ROOT = Path(__file__).resolve().parents[2] / "var" / "resumes"


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
    user_dir = _STORAGE_ROOT / current_user.id
    user_dir.mkdir(parents=True, exist_ok=True)
    stored_path = user_dir / f"resume{extension}"
    stored_path.write_bytes(content)

    profile.resume_file_path = str(stored_path)
    profile.resume_original_filename = file.filename
    db.commit()

    return result
