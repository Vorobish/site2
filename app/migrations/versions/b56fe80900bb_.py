"""empty message

Revision ID: b56fe80900bb
Revises: a19bb20e1651
Create Date: 2024-11-12 08:50:13.666576

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b56fe80900bb'
down_revision: Union[str, None] = 'a19bb20e1651'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
