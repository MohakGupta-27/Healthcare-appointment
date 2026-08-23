from app.core.config import settings


def test_hold_ttl_defaults_to_five_minutes() -> None:
    assert settings.hold_ttl_seconds == 300


def test_email_backend_defaults_to_console() -> None:
    assert settings.email_backend == "console"


def test_cors_origins_parse() -> None:
    assert "http://localhost:5173" in settings.cors_origin_list
