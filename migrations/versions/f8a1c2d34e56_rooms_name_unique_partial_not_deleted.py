"""rooms name unique only when not soft-deleted

Revision ID: f8a1c2d34e56
Revises: 28fb9b0aaf72
Create Date: 2026-05-17 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'f8a1c2d34e56'
down_revision: Union[str, Sequence[str], None] = '28fb9b0aaf72'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_INDEX_NAME = 'uq_rooms_name_not_deleted'


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()
    insp = sa.inspect(conn)
    for uc in insp.get_unique_constraints('rooms'):
        if uc.get('column_names') == ['name']:
            op.drop_constraint(uc['name'], 'rooms', type_='unique')
            break

    op.create_index(
        _INDEX_NAME,
        'rooms',
        ['name'],
        unique=True,
        postgresql_where=sa.text('is_deleted = false'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(_INDEX_NAME, table_name='rooms')
    op.create_unique_constraint('rooms_name_key', 'rooms', ['name'])
