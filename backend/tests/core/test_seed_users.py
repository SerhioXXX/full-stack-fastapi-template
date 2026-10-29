from sqlmodel import Session, select

from app.core.db import SEED_DEMO_USERS, init_db
from app.core.config import settings
from app.models import Role, User


def test_init_db_seeds_admin_manager_member(db: Session) -> None:
    init_db(db)

    admin = db.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    assert admin is not None
    assert admin.role == Role.ADMIN
    assert admin.is_superuser is True

    for seed in SEED_DEMO_USERS:
        user = db.exec(select(User).where(User.email == seed["email"])).first()
        assert user is not None
        assert user.role == seed["role"]
        assert user.is_superuser is False

    # Idempotent: second call does not fail or duplicate.
    init_db(db)
    emails = [
        settings.FIRST_SUPERUSER,
        *[str(seed["email"]) for seed in SEED_DEMO_USERS],
    ]
    for email in emails:
        matches = db.exec(select(User).where(User.email == email)).all()
        assert len(matches) == 1
