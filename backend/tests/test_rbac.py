import pytest
from unittest.mock import MagicMock

from app.api.deps import require_role
from app.models.user import User, UserRole


def _make_user(role: str = "patient") -> User:
    user = MagicMock(spec=User)
    user.id = "test-user-id"
    user.email = "test@example.com"
    user.full_name = "Test User"
    user.role = UserRole(role)
    user.is_active = True
    return user


def test_require_role_allows_matching_role():
    admin = _make_user("admin")
    checker = require_role("admin")
    result = checker(current_user=admin)
    assert result.role == UserRole.admin


def test_require_role_denies_non_matching_role():
    from fastapi import HTTPException

    patient = _make_user("patient")
    checker = require_role("admin")
    with pytest.raises(HTTPException) as exc_info:
        checker(current_user=patient)
    assert exc_info.value.status_code == 403
    assert "Insufficient permissions" in exc_info.value.detail


def test_require_role_allows_multiple_roles():
    doctor = _make_user("doctor")
    checker = require_role("doctor", "admin")
    result = checker(current_user=doctor)
    assert result.role == UserRole.doctor
