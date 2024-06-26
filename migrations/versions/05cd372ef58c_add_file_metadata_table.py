"""add file_metadata table

Revision ID: 05cd372ef58c
Revises: e367f73cab28
Create Date: 2024-04-20 19:00:38.364882

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '05cd372ef58c'
down_revision: Union[str, None] = 'e367f73cab28'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('file_metadata',
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('path', sa.String(), nullable=False),
        sa.Column('mimetype', sa.String(), nullable=False),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('updated', sa.DateTime(), nullable=True),
        sa.Column('id', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id', 'path', name='idx_unique_file_metadata_path')
    )
    op.create_index(op.f('ix_initiative_category_community_id'), 'initiative_category', ['community_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_initiative_category_community_id'), table_name='initiative_category')
    op.drop_table('file_metadata')
    # ### end Alembic commands ###
