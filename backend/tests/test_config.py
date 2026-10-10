import pytest

from app.core.config import Settings


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("https://shigotai.vercel.app", ["https://shigotai.vercel.app"]),
        ("https://a.example.com, https://b.example.com", ["https://a.example.com", "https://b.example.com"]),
        ('["https://a.example.com", "https://b.example.com"]', ["https://a.example.com", "https://b.example.com"]),
    ],
)
def test_cors_origins_accepts_comma_separated_and_json(monkeypatch, raw, expected):
    monkeypatch.setenv("CORS_ORIGINS", raw)
    assert Settings().cors_origins == expected


def test_production_requires_real_auth_secret(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.delenv("AUTH_SECRET", raising=False)
    with pytest.raises(ValueError):
        Settings()
