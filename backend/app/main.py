from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin, auth, companies, dashboard, jobs, matches, notifications, profile, resume, saved
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title="Shigotai API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(resume.router)
app.include_router(jobs.router)
app.include_router(matches.router)
app.include_router(companies.router)
app.include_router(saved.router)
app.include_router(notifications.router)
app.include_router(dashboard.router)
app.include_router(admin.router)


@app.get("/health")
def health():
    return {"status": "ok"}
