"""fix initiative category table

Revision ID: e367f73cab28
Revises: 9d22ccd28363
Create Date: 2024-04-16 20:08:06.845202

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e367f73cab28'
down_revision: Union[str, None] = '9d22ccd28363'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_initiative_category_community_id'), 'initiative_category', ['community_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_initiative_category_community_id'), table_name='initiative_category')
    # ### end Alembic commands ###
