"""Regression coverage for a real bug found during manual QA: PUT
/applications/{job_id} used to insert a row for a job_id that didn't exist
(SQLite doesn't enforce the FK), which then permanently 500'd GET
/applications for that user since it tried to serialize a null job.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_current_user
from app.database.session import Base, get_db
from app.main import app
from app.models import *  # noqa: F401,F403
from app.models.company import Company
from app.models.enums import EmploymentType, WorkMode
from app.models.interaction import Application
from app.models.job import Job
from app.models.profile import Profile
from app.models.user import User


@pytest.fixture()
def client():
    # StaticPool is required here (not just check_same_thread=False): FastAPI's
    # TestClient runs sync endpoints in a worker thread via run_in_threadpool,
    # and SQLite's default SingletonThreadPool would hand that thread a brand
    # new (schema-less) :memory: connection. StaticPool shares one connection
    # across all threads.
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    session_local = sessionmaker(bind=engine)
    db = session_local()

    user = User(email="apptest@example.com", hashed_password="x", full_name="App Test")
    db.add(user)
    db.flush()
    db.add(Profile(user_id=user.id))

    company = Company(name="Acme", slug="acme")
    db.add(company)
    db.flush()
    job = Job(
        company_id=company.id,
        title="Engineer",
        original_description="desc",
        source_url="https://x/1",
        canonical_url="https://x/1",
        content_hash="h1",
        employment_type=EmploymentType.FULL_TIME,
        work_mode=WorkMode.HYBRID,
    )
    db.add(job)
    db.commit()

    def override_get_db():
        yield db

    def override_get_current_user():
        return user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as test_client:
        yield test_client, db, job.id, user.id

    app.dependency_overrides.clear()
    db.close()


def test_put_application_with_invalid_job_id_returns_404_and_does_not_insert(client):
    test_client, db, _real_job_id, _user_id = client

    response = test_client.put("/applications/not-a-real-job-id", json={"status": "APPLIED"})

    assert response.status_code == 404
    assert db.query(Application).count() == 0


def test_put_application_with_real_job_id_succeeds(client):
    test_client, db, real_job_id, _user_id = client

    response = test_client.put(f"/applications/{real_job_id}", json={"status": "APPLIED", "notes": "Referred by a friend"})

    assert response.status_code == 200
    assert db.query(Application).count() == 1


def test_get_applications_skips_orphaned_rows_instead_of_500ing(client):
    test_client, db, _real_job_id, user_id = client

    # Simulate a pre-existing orphaned row (e.g. from before the validation
    # fix existed, or a job that was later deleted).
    db.add(Application(user_id=user_id, job_id="orphaned-job-id"))
    db.commit()

    response = test_client.get("/applications")

    assert response.status_code == 200
    assert response.json() == []
