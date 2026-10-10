import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import get_settings

settings = get_settings()

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
# On serverless hosts (Vercel sets VERCEL=1) each instance may be frozen
# between requests, so a long-lived pool just holds dead connections against
# the database's connection limit. Open per request instead, and point
# DATABASE_URL at the provider's pooler (Neon: the "-pooler" host).
pool_options = {"poolclass": NullPool} if os.environ.get("VERCEL") else {"pool_pre_ping": True}
# pool_pre_ping avoids "server closed the connection unexpectedly" errors that
# managed Postgres providers (Neon, Supabase, RDS) cause by closing idle
# connections -- harmless no-op against SQLite.
engine = create_engine(settings.database_url, connect_args=connect_args, **pool_options)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
