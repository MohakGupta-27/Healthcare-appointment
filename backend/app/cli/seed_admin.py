"""Seed an admin user from environment variables.

Usage:
    python -m app.cli.seed_admin

Required environment variables:
    ADMIN_EMAIL
    ADMIN_PASSWORD
    ADMIN_FULL_NAME
"""

import os
import sys
from pathlib import Path

# Ensure backend directory is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.repositories.user import get_user_by_email


def main() -> None:
    email = os.environ.get("ADMIN_EMAIL")
    password = os.environ.get("ADMIN_PASSWORD")
    full_name = os.environ.get("ADMIN_FULL_NAME")

    if not all([email, password, full_name]):
        print(
            "ERROR: Set ADMIN_EMAIL, ADMIN_PASSWORD, and ADMIN_FULL_NAME "
            "environment variables before running this command."
        )
        sys.exit(1)

    db = SessionLocal()
    try:
        existing = get_user_by_email(db, email.lower())
        if existing:
            print(f"Admin user {email} already exists (id={existing.id}).")
            return

        admin = User(
            email=email.lower(),
            hashed_password=hash_password(password),
            full_name=full_name,
            role=UserRole.admin,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print(f"Admin user created: {admin.email} (id={admin.id})")
    finally:
        db.close()


if __name__ == "__main__":
    main()
