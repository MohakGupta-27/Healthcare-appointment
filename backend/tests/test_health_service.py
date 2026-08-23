from unittest.mock import MagicMock

from app.schemas.health import HealthResponse
from app.services.health import get_health


def test_health_is_degraded_when_postgres_fails(monkeypatch) -> None:
    monkeypatch.setattr("app.services.health._check_postgres", lambda _db: "error")
    monkeypatch.setattr("app.services.health._check_redis", lambda: "ok")
    result = get_health(MagicMock())
    assert isinstance(result, HealthResponse)
    assert result.status == "degraded"
    assert result.postgres == "error"
    assert result.redis == "ok"
