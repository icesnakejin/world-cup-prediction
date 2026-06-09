"""wallet source of truth and uppercase status

Revision ID: 202606020001
Revises: 202606010001
Create Date: 2026-06-02 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "202606020001"
down_revision: str | None = "202606010001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_column("users", "balance")
    op.execute("UPDATE markets SET status = 'OPEN' WHERE status = 'open'")
    op.execute("UPDATE bets SET status = 'PENDING' WHERE status = 'pending'")
    op.alter_column("markets", "status", existing_type=sa.String(length=30), server_default="OPEN")
    op.alter_column("bets", "status", existing_type=sa.String(length=30), server_default="PENDING")


def downgrade() -> None:
    op.add_column("users", sa.Column("balance", sa.Integer(), server_default="10000", nullable=False))
    op.execute("UPDATE markets SET status = 'open' WHERE status = 'OPEN'")
    op.execute("UPDATE bets SET status = 'pending' WHERE status = 'PENDING'")
    op.alter_column("markets", "status", existing_type=sa.String(length=30), server_default="open")
    op.alter_column("bets", "status", existing_type=sa.String(length=30), server_default="pending")
