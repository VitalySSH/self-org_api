"""Remove RelationUserCsRequestMemberRemove table

Revision ID: 47ce006b363d
Revises: 55b182fdc84f
Create Date: 2024-08-25 23:22:25.771413

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '47ce006b363d'
down_revision: Union[str, None] = '55b182fdc84f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_relation_user_cs_request_member_remove_from_id', table_name='relation_user_cs_request_member_remove')
    op.drop_index('ix_relation_user_cs_request_member_remove_to_id', table_name='relation_user_cs_request_member_remove')
    op.drop_table('relation_user_cs_request_member_remove')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('relation_user_cs_request_member_remove',
    sa.Column('from_id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('to_id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['from_id'], ['user_community_settings.id'], name='relation_user_cs_request_member_remove_from_id_fkey'),
    sa.ForeignKeyConstraint(['to_id'], ['request_member.id'], name='relation_user_cs_request_member_remove_to_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='relation_user_cs_request_member_remove_pkey'),
    sa.UniqueConstraint('from_id', 'to_id', name='idx_unique_user_community_settings_request_member_remove')
    )
    op.create_index('ix_relation_user_cs_request_member_remove_to_id', 'relation_user_cs_request_member_remove', ['to_id'], unique=False)
    op.create_index('ix_relation_user_cs_request_member_remove_from_id', 'relation_user_cs_request_member_remove', ['from_id'], unique=False)
    # ### end Alembic commands ###