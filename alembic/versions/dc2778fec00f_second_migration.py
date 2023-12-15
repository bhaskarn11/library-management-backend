"""second migration

Revision ID: dc2778fec00f
Revises: d507d8cd17a0
Create Date: 2023-12-16 00:38:00.176012

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dc2778fec00f'
down_revision: Union[str, None] = 'd507d8cd17a0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
