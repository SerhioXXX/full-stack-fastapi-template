from sqlmodel import Session, create_engine, select

from app import crud
from app.core.config import settings
from app.models import Role, User, UserCreate

engine = create_engine(str(settings.DATABASE_URL), pool_pre_ping=True)


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


# Dev/demo accounts created by init_db (idempotent). Same password as FIRST_SUPERUSER by default.
SEED_DEMO_PASSWORD = "changethis"
SEED_DEMO_USERS: list[dict[str, str | Role]] = [
    {
        "email": "manager@example.com",
        "password": SEED_DEMO_PASSWORD,
        "role": Role.MANAGER,
        "full_name": "Demo Manager",
    },
    {
        "email": "member@example.com",
        "password": SEED_DEMO_PASSWORD,
        "role": Role.MEMBER,
        "full_name": "Demo Member",
    },
]


def _ensure_user(
    session: Session,
    *,
    email: str,
    password: str,
    role: Role,
    full_name: str | None = None,
) -> User:
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        return crud.create_user(
            session=session,
            user_create=UserCreate(
                email=email,
                password=password,
                role=role,
                full_name=full_name,
            ),
        )

    if user.role != role or user.is_superuser != (role == Role.ADMIN):
        user.role = role
        user.is_superuser = role == Role.ADMIN
        if full_name and not user.full_name:
            user.full_name = full_name
        session.add(user)
        session.commit()
        session.refresh(user)
    return user


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    _ensure_user(
        session,
        email=settings.FIRST_SUPERUSER,
        password=settings.FIRST_SUPERUSER_PASSWORD,
        role=Role.ADMIN,
        full_name="Demo Admin",
    )

    for seed in SEED_DEMO_USERS:
        _ensure_user(
            session,
            email=str(seed["email"]),
            password=str(seed["password"]),
            role=Role(seed["role"]),
            full_name=str(seed["full_name"]) if seed.get("full_name") else None,
        )
