"""create zipcodes table

Revision ID: e7117458292c
Revises: 
Create Date: 2026-02-11 17:37:02.196648

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import func

# revision identifiers, used by Alembic.
revision: str = 'e7117458292c'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'zip_codes',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('zip_code', sa.String(20), unique=True, nullable=False),
        sa.Column('latitude', sa.Float(5), nullable=False),
        sa.Column('longitude', sa.Float(5), nullable=False),
        sa.Column('country_code', sa.String(2), nullable=False),
        sa.Column('state', sa.Text, nullable=False),
        sa.Column('city', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=func.now()),
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
