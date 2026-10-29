import uuid
from datetime import UTC, datetime
from enum import Enum

from typing import Self

from pydantic import EmailStr, model_validator
from sqlalchemy import Column, Enum as SAEnum
from sqlmodel import Field, Relationship, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(UTC)


class Role(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"


def sync_role_and_superuser(
    *,
    role: Role | None = None,
    is_superuser: bool | None = None,
    current_role: Role | None = None,
) -> dict[str, Role | bool]:
    """Keep role as source of truth; sync legacy is_superuser.

    - Explicit role wins and sets is_superuser (True only for admin).
    - Legacy clients that only set is_superuser=True with default/member role
      are promoted to admin.
    - Legacy is_superuser=False on an admin demotes role to member.
    """
    updates: dict[str, Role | bool] = {}
    if role is not None:
        updates["role"] = role
        updates["is_superuser"] = role == Role.ADMIN
    elif is_superuser is not None:
        if is_superuser:
            updates["role"] = Role.ADMIN
            updates["is_superuser"] = True
        else:
            demoted_role = (
                Role.MEMBER if current_role in (None, Role.ADMIN) else current_role
            )
            updates["role"] = demoted_role
            updates["is_superuser"] = False
    return updates


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    role: Role = Field(default=Role.MEMBER, index=True, max_length=20)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(SQLModel):
    email: EmailStr | None = Field(default=None, max_length=255)
    is_active: bool | None = None
    is_superuser: bool | None = None
    role: Role | None = None
    full_name: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    # Store enum *values* (admin/manager/member) as VARCHAR, not enum member names.
    role: Role = Field(
        default=Role.MEMBER,
        sa_column=Column(
            SAEnum(
                Role,
                values_callable=lambda enum: [item.value for item in enum],
                native_enum=False,
                length=20,
            ),
            nullable=False,
            index=True,
        ),
    )
    hashed_password: str
    created_at: datetime | None = Field(default_factory=get_datetime_utc)
    items: list[Item] = Relationship(back_populates="owner", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime | None = None
    permissions: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def populate_permissions(self) -> Self:
        # Lazy import avoids circular dependency with app.core.rbac.
        from app.core.rbac import permissions_for

        object.__setattr__(
            self, "permissions", sorted(permissions_for(self.role))
        )
        return self


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(default_factory=get_datetime_utc)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime | None = None


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class MetricsPublic(SQLModel):
    """Lightweight insights payload for the metrics page."""

    total_users: int
    active_users: int
    total_items: int


class SystemSettings(SQLModel):
    """In-memory global settings stub (not persisted)."""

    site_name: str = Field(default="Full Stack FastAPI Project", max_length=255)
    maintenance_mode: bool = False
    support_email: EmailStr | None = None


class SystemSettingsUpdate(SQLModel):
    site_name: str | None = Field(default=None, max_length=255)
    maintenance_mode: bool | None = None
    support_email: EmailStr | None = None
