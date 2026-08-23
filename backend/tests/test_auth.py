import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from datetime import timedelta

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User, UserRole


# --- Security unit tests ---


def test_hash_and_verify_password():
    hashed = hash_password("correctpassword")
    assert verify_password("correctpassword", hashed)
    assert not verify_password("wrongpassword", hashed)


def test_create_and_decode_token():
    from app.core.security import decode_access_token

    token = create_access_token(subject="user-123", role="patient")
    payload = decode_access_token(token)
    assert payload["sub"] == "user-123"
    assert payload["role"] == "patient"


def test_expired_token_raises():
    from app.core.security import decode_access_token
    from jose import ExpiredSignatureError

    token = create_access_token(
        subject="user-123", role="patient", expires_delta=timedelta(seconds=-1)
    )
    with pytest.raises(ExpiredSignatureError):
        decode_access_token(token)


def test_invalid_token_raises():
    from app.core.security import decode_access_token
    from jose import JWTError

    with pytest.raises(JWTError):
        decode_access_token("not-a-valid-jwt")


# --- Auth API integration tests ---


@pytest.fixture()
def _mock_db():
    """Patch get_db to return a mock session for auth tests."""
    users_store: dict[str, User] = {}

    def fake_get_db():
        db = MagicMock()

        def fake_execute(stmt):
            result = MagicMock()
            where_clause = stmt.whereclause
            if where_clause is not None:
                right_val = where_clause.right.value if hasattr(where_clause.right, "value") else None
                col_name = where_clause.left.key if hasattr(where_clause.left, "key") else ""
                if col_name == "email":
                    result.scalar_one_or_none.return_value = users_store.get(right_val)
                elif col_name == "id":
                    found = None
                    for u in users_store.values():
                        if u.id == right_val:
                            found = u
                            break
                    result.scalar_one_or_none.return_value = found
                else:
                    result.scalar_one_or_none.return_value = None
            else:
                result.scalar_one_or_none.return_value = None
            return result

        def fake_add(user):
            import uuid as _uuid
            if not user.id:
                user.id = str(_uuid.uuid4())
            users_store[user.email] = user

        def fake_commit():
            pass

        def fake_refresh(user):
            pass

        db.execute.side_effect = fake_execute
        db.add.side_effect = fake_add
        db.commit.side_effect = fake_commit
        db.refresh.side_effect = fake_refresh
        yield db

    from app.main import app
    from app.db.session import get_db
    app.dependency_overrides[get_db] = fake_get_db
    yield users_store
    app.dependency_overrides.clear()


def _register(client, email="test@example.com", password="securepass123", full_name="Test User"):
    return client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": full_name},
    )


def _login(client, email="test@example.com", password="securepass123"):
    return client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )


def test_register_success(client: TestClient, _mock_db):
    resp = _register(client)
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "test@example.com"
    assert body["role"] == "patient"
    assert "id" in body


def test_register_duplicate_email(client: TestClient, _mock_db):
    _register(client)
    resp = _register(client)
    assert resp.status_code == 409
    assert "already registered" in resp.json()["detail"]


def test_register_short_password(client: TestClient, _mock_db):
    resp = _register(client, password="short")
    assert resp.status_code == 422


def test_login_success(client: TestClient, _mock_db):
    _register(client)
    resp = _login(client)
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_wrong_password(client: TestClient, _mock_db):
    _register(client)
    resp = _login(client, password="wrongpassword")
    assert resp.status_code == 401


def test_login_nonexistent_email(client: TestClient, _mock_db):
    resp = _login(client, email="nobody@example.com")
    assert resp.status_code == 401


def test_me_with_valid_token(client: TestClient, _mock_db):
    _register(client)
    login_resp = _login(client)
    token = login_resp.json()["access_token"]
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@example.com"


def test_me_without_token(client: TestClient, _mock_db):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401


def test_me_with_invalid_token(client: TestClient, _mock_db):
    resp = client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer invalid-token"}
    )
    assert resp.status_code == 401


def test_me_with_expired_token(client: TestClient, _mock_db):
    _register(client)
    login_resp = _login(client)
    from app.core.security import decode_access_token
    payload = decode_access_token(login_resp.json()["access_token"])
    expired_token = create_access_token(
        subject=payload["sub"], role=payload["role"],
        expires_delta=timedelta(seconds=-1),
    )
    resp = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert resp.status_code == 401
