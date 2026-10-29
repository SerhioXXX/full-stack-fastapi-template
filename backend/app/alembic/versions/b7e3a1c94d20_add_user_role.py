"""Add user role

Revision ID: b7e3a1c94d20
Revises: fe56fa70289e
Create Date: 2026-10-29 23:50:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b7e3a1c94d20"
down_revision = "fe56fa70289e"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "user",
        sa.Column(
            "role",
            sa.String(length=20),
            nullable=False,
            server_default="member",
        ),
    )
    op.create_index(op.f("ix_user_role"), "user", ["role"], unique=False)
    # Backfill: existing superusers become admins; everyone else stays member.
    op.execute(sa.text("UPDATE \"user\" SET role = 'admin' WHERE is_superuser IS TRUE"))
    op.alter_column("user", "role", server_default=None)


def downgrade():
    op.drop_index(op.f("ix_user_role"), table_name="user")
    op.drop_column("user", "role")
