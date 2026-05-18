"""initial schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-05-15 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER NOT NULL PRIMARY KEY,
            email VARCHAR NOT NULL UNIQUE,
            hashed_password VARCHAR NOT NULL,
            is_active BOOLEAN,
            is_verified BOOLEAN,
            points_balance INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_users_id ON users (id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_users_email ON users (email)")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INTEGER NOT NULL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            token_hash VARCHAR NOT NULL UNIQUE,
            expires_at DATETIME NOT NULL,
            used BOOLEAN,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users (id)
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_password_reset_tokens_id ON password_reset_tokens (id)")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS wallets (
            id INTEGER NOT NULL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            wallet_address VARCHAR NOT NULL,
            wallet_type VARCHAR NOT NULL,
            attached_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users (id),
            CONSTRAINT uq_wallets_user_id UNIQUE (user_id)
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_wallets_id ON wallets (id)")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS points_ledger (
            id INTEGER NOT NULL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            transaction_type VARCHAR NOT NULL,
            reason VARCHAR NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users (id)
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_points_ledger_id ON points_ledger (id)")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS point_redeems (
            id INTEGER NOT NULL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            points_used INTEGER NOT NULL,
            status VARCHAR,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users (id)
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_point_redeems_id ON point_redeems (id)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS point_redeems")
    op.execute("DROP TABLE IF EXISTS points_ledger")
    op.execute("DROP TABLE IF EXISTS wallets")
    op.execute("DROP TABLE IF EXISTS password_reset_tokens")
    op.execute("DROP TABLE IF EXISTS users")
