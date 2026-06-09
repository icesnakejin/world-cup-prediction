"""add world cup match metadata

Revision ID: 202606090001
Revises: 202606040001
Create Date: 2026-06-09 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "202606090001"
down_revision: str | None = "202606040001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("matches", sa.Column("match_number", sa.Integer(), nullable=True))
    op.add_column("matches", sa.Column("stage", sa.String(length=30), nullable=True))
    op.add_column("matches", sa.Column("group", sa.String(length=5), nullable=True))
    op.add_column("matches", sa.Column("home_placeholder", sa.String(length=100), nullable=True))
    op.add_column("matches", sa.Column("away_placeholder", sa.String(length=100), nullable=True))
    op.add_column("matches", sa.Column("venue", sa.String(length=150), nullable=True))
    op.create_index(op.f("ix_matches_match_number"), "matches", ["match_number"], unique=True)
    op.create_index(op.f("ix_matches_stage"), "matches", ["stage"], unique=False)
    op.create_index(op.f("ix_matches_group"), "matches", ["group"], unique=False)
    op.alter_column("matches", "home_team", existing_type=sa.String(length=100), nullable=True)
    op.alter_column("matches", "away_team", existing_type=sa.String(length=100), nullable=True)


def downgrade() -> None:
    op.alter_column("matches", "away_team", existing_type=sa.String(length=100), nullable=False)
    op.alter_column("matches", "home_team", existing_type=sa.String(length=100), nullable=False)
    op.drop_index(op.f("ix_matches_group"), table_name="matches")
    op.drop_index(op.f("ix_matches_stage"), table_name="matches")
    op.drop_index(op.f("ix_matches_match_number"), table_name="matches")
    op.drop_column("matches", "venue")
    op.drop_column("matches", "away_placeholder")
    op.drop_column("matches", "home_placeholder")
    op.drop_column("matches", "group")
    op.drop_column("matches", "stage")
    op.drop_column("matches", "match_number")
