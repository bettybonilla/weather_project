"""create hourly weather aggregates table

Revision ID: 356495c22319
Revises: e7117458292c
Create Date: 2026-02-11 17:37:42.472549

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import func

# revision identifiers, used by Alembic.
revision: str = '356495c22319'
down_revision: Union[str, Sequence[str], None] = 'e7117458292c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'hourly_weather_aggregates',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('zip_code', sa.String(20), nullable=False),
        sa.Column('date', sa.Date, nullable=False),
        sa.Column('hour', sa.Integer, nullable=False),
        sa.Column('avg_temp', sa.Integer, nullable=False),
        sa.Column('avg_rain_prob', sa.Integer, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=func.now()),
        sa.UniqueConstraint('zip_code', 'date', 'hour', name='unique_zip_date_hour'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
