"""add relation table

Revision ID: 2dbcbc3aaf15
Revises: 916b77233e98
Create Date: 2024-04-15 13:13:25.712675

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2dbcbc3aaf15'
down_revision: Union[str, None] = '916b77233e98'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('relation_voting_result_voting_options',
        sa.Column('from_id', sa.String(), nullable=False),
        sa.Column('to_id', sa.String(), nullable=False),
        sa.Column('id', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['from_id'], ['voting_result.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['to_id'], ['voting_option.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('from_id', 'to_id', name='idx_unique_voting_result_voting_option')
    )
    op.create_index(op.f('ix_relation_voting_result_voting_options_from_id'), 'relation_voting_result_voting_options', ['from_id'], unique=False)
    op.create_index(op.f('ix_relation_voting_result_voting_options_to_id'), 'relation_voting_result_voting_options', ['to_id'], unique=False)
    op.drop_index('ix_relation_voting_result_voting_options._from_id', table_name='relation_voting_result_voting_options.')
    op.drop_index('ix_relation_voting_result_voting_options._to_id', table_name='relation_voting_result_voting_options.')
    op.drop_table('relation_voting_result_voting_options.')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('relation_voting_result_voting_options.',
    sa.Column('from_id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('to_id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['from_id'], ['voting_result.id'], name='relation_voting_result_voting_options._from_id_fkey', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['to_id'], ['voting_option.id'], name='relation_voting_result_voting_options._to_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='relation_voting_result_voting_options._pkey'),
    sa.UniqueConstraint('from_id', 'to_id', name='idx_unique_voting_result_voting_options')
    )
    op.create_index('ix_relation_voting_result_voting_options._to_id', 'relation_voting_result_voting_options.', ['to_id'], unique=False)
    op.create_index('ix_relation_voting_result_voting_options._from_id', 'relation_voting_result_voting_options.', ['from_id'], unique=False)
    op.drop_index(op.f('ix_relation_voting_result_voting_options_to_id'), table_name='relation_voting_result_voting_options')
    op.drop_index(op.f('ix_relation_voting_result_voting_options_from_id'), table_name='relation_voting_result_voting_options')
    op.drop_table('relation_voting_result_voting_options')
    # ### end Alembic commands ###