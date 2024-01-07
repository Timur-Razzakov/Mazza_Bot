"""update tariff_name

Revision ID: aa2df158cc61
Revises: b8696327cc0d
Create Date: 2024-01-08 01:45:42.909269

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aa2df158cc61'
down_revision: Union[str, None] = 'b8696327cc0d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tariffs', sa.Column('tariff_name', sa.String(length=255), nullable=False))
    op.add_column('tariffs', sa.Column('tariff_name_uzb', sa.String(length=255), nullable=True))
    op.drop_column('tariffs', 'tariffs_name_uzb')
    op.drop_column('tariffs', 'tariffs_name')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tariffs', sa.Column('tariffs_name', sa.VARCHAR(length=255), autoincrement=False, nullable=False))
    op.add_column('tariffs', sa.Column('tariffs_name_uzb', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.drop_column('tariffs', 'tariff_name_uzb')
    op.drop_column('tariffs', 'tariff_name')
    # ### end Alembic commands ###
