"""initial schema

Revision ID: 202605290001
Revises:
Create Date: 2026-05-29 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "202605290001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("balance", sa.Integer(), server_default="10000", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "matches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("home_team", sa.String(length=100), nullable=False),
        sa.Column("away_team", sa.String(length=100), nullable=False),
        sa.Column("kickoff_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=30), server_default="scheduled", nullable=False),
        sa.Column("home_score", sa.Integer(), nullable=True),
        sa.Column("away_score", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_matches_id"), "matches", ["id"], unique=False)
    op.create_index(op.f("ix_matches_kickoff_time"), "matches", ["kickoff_time"], unique=False)

    op.create_table(
        "markets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("match_id", sa.Integer(), nullable=False),
        sa.Column("market_type", sa.String(length=50), server_default="match_winner", nullable=False),
        sa.Column("selection", sa.String(length=30), nullable=False),
        sa.Column("odds", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("status", sa.String(length=30), server_default="open", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["match_id"], ["matches.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("match_id", "market_type", "selection", name="uq_markets_match_type_selection"),
    )
    op.create_index(op.f("ix_markets_id"), "markets", ["id"], unique=False)
    op.create_index(op.f("ix_markets_match_id"), "markets", ["match_id"], unique=False)

    op.create_table(
        "bets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("match_id", sa.Integer(), nullable=False),
        sa.Column("market_id", sa.Integer(), nullable=False),
        sa.Column("selection", sa.String(length=30), nullable=False),
        sa.Column("stake", sa.Integer(), nullable=False),
        sa.Column("odds", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("payout", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=30), server_default="pending", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["market_id"], ["markets.id"]),
        sa.ForeignKeyConstraint(["match_id"], ["matches.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_bets_id"), "bets", ["id"], unique=False)
    op.create_index(op.f("ix_bets_market_id"), "bets", ["market_id"], unique=False)
    op.create_index(op.f("ix_bets_match_id"), "bets", ["match_id"], unique=False)
    op.create_index(op.f("ix_bets_user_id"), "bets", ["user_id"], unique=False)

    op.create_table(
        "wallet_transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("transaction_type", sa.String(length=50), nullable=False),
        sa.Column("reference_id", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_wallet_transactions_id"), "wallet_transactions", ["id"], unique=False)
    op.create_index(op.f("ix_wallet_transactions_reference_id"), "wallet_transactions", ["reference_id"], unique=False)
    op.create_index(op.f("ix_wallet_transactions_user_id"), "wallet_transactions", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_wallet_transactions_user_id"), table_name="wallet_transactions")
    op.drop_index(op.f("ix_wallet_transactions_reference_id"), table_name="wallet_transactions")
    op.drop_index(op.f("ix_wallet_transactions_id"), table_name="wallet_transactions")
    op.drop_table("wallet_transactions")

    op.drop_index(op.f("ix_bets_user_id"), table_name="bets")
    op.drop_index(op.f("ix_bets_match_id"), table_name="bets")
    op.drop_index(op.f("ix_bets_market_id"), table_name="bets")
    op.drop_index(op.f("ix_bets_id"), table_name="bets")
    op.drop_table("bets")

    op.drop_index(op.f("ix_markets_match_id"), table_name="markets")
    op.drop_index(op.f("ix_markets_id"), table_name="markets")
    op.drop_table("markets")

    op.drop_index(op.f("ix_matches_kickoff_time"), table_name="matches")
    op.drop_index(op.f("ix_matches_id"), table_name="matches")
    op.drop_table("matches")

    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")
