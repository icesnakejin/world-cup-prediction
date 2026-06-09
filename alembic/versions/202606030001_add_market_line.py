"""add market line

Revision ID: 202606030001
Revises: 202606020001
Create Date: 2026-06-03 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "202606030001"
down_revision: str | None = "202606020001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("markets", sa.Column("line", sa.Numeric(precision=10, scale=2), nullable=True))


def downgrade() -> None:
    op.drop_column("markets", "line")
