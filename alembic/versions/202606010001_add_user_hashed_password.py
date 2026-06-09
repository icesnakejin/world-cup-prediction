"""add user hashed password

Revision ID: 202606010001
Revises: 202605290001
Create Date: 2026-06-01 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "202606010001"
down_revision: str | None = "202605290001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("hashed_password", sa.String(length=255), nullable=False))


def downgrade() -> None:
    op.drop_column("users", "hashed_password")
