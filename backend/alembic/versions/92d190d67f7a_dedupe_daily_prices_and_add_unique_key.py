"""Dedupe daily prices and add unique key

Revision ID: 92d190d67f7a
Revises: 5199a6771ee9
Create Date: 2026-05-04 16:20:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '92d190d67f7a'
down_revision: Union[str, Sequence[str], None] = '6a8b9c0d1e2f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        DELETE FROM daily_prices dp
        USING (
            SELECT id
            FROM (
                SELECT id,
                       ROW_NUMBER() OVER (
                           PARTITION BY ticker_id, date
                           ORDER BY id DESC
                       ) AS row_num
                FROM daily_prices
            ) ranked
            WHERE ranked.row_num > 1
        ) duplicates
        WHERE dp.id = duplicates.id
        """
    )
    op.create_unique_constraint(
        'uq_daily_prices_ticker_date',
        'daily_prices',
        ['ticker_id', 'date'],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        'uq_daily_prices_ticker_date',
        'daily_prices',
        type_='unique',
    )
