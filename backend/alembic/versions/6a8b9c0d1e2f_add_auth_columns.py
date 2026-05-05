"""Add auth columns and phone verification table

Revision ID: 6a8b9c0d1e2f
Revises: 5199a6771ee9
Create Date: 2026-04-01 09:00:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '6a8b9c0d1e2f'
down_revision: Union[str, Sequence[str], None] = '5199a6771ee9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS phone_number VARCHAR(20)")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS phone_verified BOOLEAN DEFAULT FALSE")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS google_id VARCHAR(255)")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_providers JSONB DEFAULT '[]'")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS default_auth_method VARCHAR(20) DEFAULT 'password'")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name VARCHAR(255)")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(500)")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP WITH TIME ZONE")
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS phone_verifications (
            id SERIAL PRIMARY KEY,
            phone_number VARCHAR(20) NOT NULL,
            verification_code VARCHAR(6) NOT NULL,
            is_used BOOLEAN DEFAULT FALSE,
            expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
        """
    )
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_phone_number ON users(phone_number)")
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_google_id ON users(google_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_phone_verifications_phone_number ON phone_verifications(phone_number)")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP INDEX IF EXISTS ix_phone_verifications_phone_number")
    op.execute("DROP TABLE IF EXISTS phone_verifications")
    op.execute("DROP INDEX IF EXISTS ix_users_google_id")
    op.execute("DROP INDEX IF EXISTS ix_users_phone_number")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS last_login")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS avatar_url")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS full_name")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS default_auth_method")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS auth_providers")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS google_id")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS phone_verified")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS phone_number")
