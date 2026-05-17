"""add job log artifact columns

Revision ID: b2f1a7c9d4e1
Revises: 0627d0ee4087
Create Date: 2026-03-22 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b2f1a7c9d4e1"
down_revision: Union[str, None] = "0627d0ee4087"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("log_path", sa.String(), nullable=True))
    op.add_column("jobs", sa.Column("log_url", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("jobs", "log_url")
    op.drop_column("jobs", "log_path")
