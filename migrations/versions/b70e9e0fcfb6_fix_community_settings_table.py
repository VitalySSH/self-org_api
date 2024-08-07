"""fix community settings table

Revision ID: b70e9e0fcfb6
Revises: 3ca946dc4556
Create Date: 2024-07-12 11:42:07.272617

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b70e9e0fcfb6'
down_revision: Union[str, None] = '3ca946dc4556'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('community_settings', 'name_id',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('community_settings', 'description_id',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('community_settings', 'quorum',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('community_settings', 'vote',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('user_community_settings', 'is_default_add_member',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user_community_settings', 'is_default_add_member',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.alter_column('community_settings', 'vote',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('community_settings', 'quorum',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('community_settings', 'description_id',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('community_settings', 'name_id',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###
