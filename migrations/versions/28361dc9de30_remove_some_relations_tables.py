"""remove some relations tables

Revision ID: 28361dc9de30
Revises: e0f8b91f9308
Create Date: 2025-02-28 00:37:44.327756

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '28361dc9de30'
down_revision: Union[str, None] = 'e0f8b91f9308'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_relation_initiative_voting_options_from_id', table_name='relation_initiative_voting_options')
    op.drop_index('ix_relation_initiative_voting_options_to_id', table_name='relation_initiative_voting_options')
    op.drop_table('relation_initiative_voting_options')
    op.drop_index('ix_relation_rule_voting_options_from_id', table_name='relation_rule_voting_options')
    op.drop_index('ix_relation_rule_voting_options_to_id', table_name='relation_rule_voting_options')
    op.drop_table('relation_rule_voting_options')
    op.drop_index('ix_relation_initiative_user_voting_results_from_id', table_name='relation_initiative_user_voting_results')
    op.drop_index('ix_relation_initiative_user_voting_results_to_id', table_name='relation_initiative_user_voting_results')
    op.drop_table('relation_initiative_user_voting_results')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('relation_initiative_user_voting_results',
    sa.Column('id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('from_id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('to_id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['from_id'], ['initiative.id'], name='relation_initiative_user_voting_results_from_id_fkey'),
    sa.ForeignKeyConstraint(['to_id'], ['user_voting_result.id'], name='relation_initiative_user_voting_results_to_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='relation_initiative_user_voting_results_pkey'),
    sa.UniqueConstraint('from_id', 'to_id', name='idx_unique_initiative_user_voting_results')
    )
    op.create_index('ix_relation_initiative_user_voting_results_to_id', 'relation_initiative_user_voting_results', ['to_id'], unique=False)
    op.create_index('ix_relation_initiative_user_voting_results_from_id', 'relation_initiative_user_voting_results', ['from_id'], unique=False)
    op.create_table('relation_rule_voting_options',
    sa.Column('id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('from_id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('to_id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['from_id'], ['rule.id'], name='relation_rule_voting_options_from_id_fkey', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['to_id'], ['voting_option.id'], name='relation_rule_voting_options_to_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='relation_rule_voting_options_pkey'),
    sa.UniqueConstraint('from_id', 'to_id', name='idx_unique_rule_voting_options')
    )
    op.create_index('ix_relation_rule_voting_options_to_id', 'relation_rule_voting_options', ['to_id'], unique=False)
    op.create_index('ix_relation_rule_voting_options_from_id', 'relation_rule_voting_options', ['from_id'], unique=False)
    op.create_table('relation_initiative_voting_options',
    sa.Column('id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('from_id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('to_id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['from_id'], ['initiative.id'], name='relation_initiative_voting_options_from_id_fkey', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['to_id'], ['voting_option.id'], name='relation_initiative_voting_options_to_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='relation_initiative_voting_options_pkey'),
    sa.UniqueConstraint('from_id', 'to_id', name='idx_unique_initiative_voting_options')
    )
    op.create_index('ix_relation_initiative_voting_options_to_id', 'relation_initiative_voting_options', ['to_id'], unique=False)
    op.create_index('ix_relation_initiative_voting_options_from_id', 'relation_initiative_voting_options', ['from_id'], unique=False)
    # ### end Alembic commands ###
