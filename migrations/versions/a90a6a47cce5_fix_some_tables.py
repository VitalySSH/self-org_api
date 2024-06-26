"""fix some tables

Revision ID: a90a6a47cce5
Revises: 7f9f2035d0d0
Create Date: 2024-04-21 01:45:55.139503

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a90a6a47cce5'
down_revision: Union[str, None] = '7f9f2035d0d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('community_description', sa.Column('creator_id', sa.String(), nullable=False))
    op.drop_index('ix_community_description_user_id', table_name='community_description')
    op.create_unique_constraint('idx_unique_community_description_id', 'community_description', ['value', 'community_id'])
    op.create_index(op.f('ix_community_description_creator_id'), 'community_description', ['creator_id'], unique=False)
    op.drop_column('community_description', 'user_id')
    op.add_column('community_name', sa.Column('creator_id', sa.String(), nullable=False))
    op.drop_index('ix_community_name_user_id', table_name='community_name')
    op.create_unique_constraint('idx_unique_community_name_id', 'community_name', ['name', 'community_id'])
    op.create_index(op.f('ix_community_name_creator_id'), 'community_name', ['creator_id'], unique=False)
    op.drop_column('community_name', 'user_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('community_name', sa.Column('user_id', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_index(op.f('ix_community_name_creator_id'), table_name='community_name')
    op.drop_constraint('idx_unique_community_name_id', 'community_name', type_='unique')
    op.create_index('ix_community_name_user_id', 'community_name', ['user_id'], unique=False)
    op.drop_column('community_name', 'creator_id')
    op.add_column('community_description', sa.Column('user_id', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_index(op.f('ix_community_description_creator_id'), table_name='community_description')
    op.drop_constraint('idx_unique_community_description_id', 'community_description', type_='unique')
    op.create_index('ix_community_description_user_id', 'community_description', ['user_id'], unique=False)
    op.drop_column('community_description', 'creator_id')
    # ### end Alembic commands ###
