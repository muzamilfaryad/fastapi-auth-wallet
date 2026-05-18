"""add refresh tokens table

Revision ID: 0002_refresh_tokens
Revises: 0001_initial_schema
Create Date: 2026-05-15 00:15:00.000000
"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "0002_refresh_tokens"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS refresh_tokens (
            id INTEGER NOT NULL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            token_hash VARCHAR NOT NULL UNIQUE,
            expires_at DATETIME NOT NULL,
            revoked BOOLEAN,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users (id)
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_refresh_tokens_id ON refresh_tokens (id)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS refresh_tokens")
