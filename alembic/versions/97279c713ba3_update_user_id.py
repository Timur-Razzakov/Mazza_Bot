"""update user_id

Revision ID: 97279c713ba3
Revises: 483cdfcced7c
Create Date: 2024-01-11 15:51:09.145062

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '97279c713ba3'
down_revision: Union[str, None] = '483cdfcced7c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
