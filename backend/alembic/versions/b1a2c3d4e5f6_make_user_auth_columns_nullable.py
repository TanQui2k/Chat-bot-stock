"""Make users email and hashed_password nullable

Revision ID: b1a2c3d4e5f6
Revises: 92d190d67f7a
Create Date: 2026-05-07 17:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b1a2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "92d190d67f7a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "users",
        "email",
        existing_type=sa.String(length=255),
        nullable=True,
    )
    op.alter_column(
        "users",
        "hashed_password",
        existing_type=sa.String(length=255),
        nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "users",
        "hashed_password",
        existing_type=sa.String(length=255),
        nullable=False,
    )
    op.alter_column(
        "users",
        "email",
        existing_type=sa.String(length=255),
        nullable=False,
    )
