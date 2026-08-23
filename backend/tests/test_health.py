from fastapi.testclient import TestClient


def test_health_reports_postgres_and_redis(client: TestClient) -> None:
    response = client.get("/health")
    body = response.json()
    assert set(body.keys()) == {"status", "postgres", "redis"}
    assert body["postgres"] in {"ok", "error"}
    assert body["redis"] in {"ok", "error"}
    if body["postgres"] == "ok" and body["redis"] == "ok":
        assert response.status_code == 200
        assert body["status"] == "ok"
    else:
        assert response.status_code == 503
        assert body["status"] == "degraded"


def test_health_also_available_under_api_prefix(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code in {200, 503}
    assert "postgres" in response.json()
    assert "redis" in response.json()
