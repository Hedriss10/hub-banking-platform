"""Add safra_batch_search table

Revision ID: c8f91e2ab410
Revises: a8c2843827ed
Create Date: 2026-05-14

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'c8f91e2ab410'
down_revision: Union[str, Sequence[str], None] = 'a8c2843827ed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'safra_batch_search',
        sa.Column('batch_job_id', sa.Uuid(), nullable=False),
        sa.Column('cpf', sa.String(), nullable=True),
        sa.Column('margem', sa.Float(), nullable=True),
        sa.Column('lotacao', sa.String(), nullable=True),
        sa.Column('autorizada', sa.Boolean(), nullable=True),
        sa.Column('nome', sa.String(), nullable=True),
        sa.Column('secretaria', sa.String(), nullable=True),
        sa.Column('tipoServidor', sa.String(), nullable=True),
        sa.Column('cargo', sa.String(), nullable=True),
        sa.Column('regimeJuridico', sa.String(), nullable=True),
        sa.Column('dataAdmissao', sa.DateTime(timezone=True), nullable=True),
        sa.Column('uf', sa.String(), nullable=True),
        sa.Column('renda', sa.Float(), nullable=True),
        sa.Column('phone_one', sa.String(), nullable=True),
        sa.Column('phone_two', sa.String(), nullable=True),
        sa.Column('phone_three', sa.String(), nullable=True),
        sa.Column('phone_four', sa.String(), nullable=True),
        sa.Column('phone_five', sa.String(), nullable=True),
        sa.Column(
            'id', sa.Uuid(), server_default=sa.text('gen_random_uuid()'), nullable=False
        ),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text("timezone('utc', now())"),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text("timezone('utc', now())"),
            nullable=False,
        ),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_safra_batch_search_batch_job_id'),
        'safra_batch_search',
        ['batch_job_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f('ix_safra_batch_search_batch_job_id'), table_name='safra_batch_search'
    )
    op.drop_table('safra_batch_search')
