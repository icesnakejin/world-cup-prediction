"""create tournament tables

Revision ID: 202606040001
Revises: 202606030001
Create Date: 2026-06-04 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "202606040001"
down_revision: str | None = "202606030001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "tournaments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), server_default="OPEN", nullable=False),
        sa.Column("winner_team", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tournaments_id"), "tournaments", ["id"], unique=False)
    op.create_index(op.f("ix_tournaments_year"), "tournaments", ["year"], unique=False)

    op.create_table(
        "tournament_markets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tournament_id", sa.Integer(), nullable=False),
        sa.Column("market_type", sa.String(length=50), server_default="tournament_winner", nullable=False),
        sa.Column("selection", sa.String(length=100), nullable=False),
        sa.Column("odds", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("status", sa.String(length=30), server_default="OPEN", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tournament_id"], ["tournaments.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tournament_id",
            "market_type",
            "selection",
            name="uq_tournament_markets_tournament_type_selection",
        ),
    )
    op.create_index(op.f("ix_tournament_markets_id"), "tournament_markets", ["id"], unique=False)
    op.create_index(op.f("ix_tournament_markets_tournament_id"), "tournament_markets", ["tournament_id"], unique=False)

    op.create_table(
        "tournament_bets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("tournament_market_id", sa.Integer(), nullable=False),
        sa.Column("selection", sa.String(length=100), nullable=False),
        sa.Column("odds", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("stake", sa.Integer(), nullable=False),
        sa.Column("payout", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=30), server_default="PENDING", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tournament_market_id"], ["tournament_markets.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tournament_bets_id"), "tournament_bets", ["id"], unique=False)
    op.create_index(op.f("ix_tournament_bets_user_id"), "tournament_bets", ["user_id"], unique=False)
    op.create_index(
        op.f("ix_tournament_bets_tournament_market_id"),
        "tournament_bets",
        ["tournament_market_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_tournament_bets_tournament_market_id"), table_name="tournament_bets")
    op.drop_index(op.f("ix_tournament_bets_user_id"), table_name="tournament_bets")
    op.drop_index(op.f("ix_tournament_bets_id"), table_name="tournament_bets")
    op.drop_table("tournament_bets")
    op.drop_index(op.f("ix_tournament_markets_tournament_id"), table_name="tournament_markets")
    op.drop_index(op.f("ix_tournament_markets_id"), table_name="tournament_markets")
    op.drop_table("tournament_markets")
    op.drop_index(op.f("ix_tournaments_year"), table_name="tournaments")
    op.drop_index(op.f("ix_tournaments_id"), table_name="tournaments")
    op.drop_table("tournaments")
