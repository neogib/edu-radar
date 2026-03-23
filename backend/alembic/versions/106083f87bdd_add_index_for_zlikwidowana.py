"""add index for zlikwidowana

Revision ID: 106083f87bdd
Revises: cd818eb49e59
Create Date: 2026-03-23 20:38:47.886391

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "106083f87bdd"
down_revision: Union[str, Sequence[str], None] = "cd818eb49e59"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        "idx_szkola_geom_3857_active_any_zlikwidowana",
        "szkola",
        ["geom_3857"],
        unique=False,
        postgresql_using="gist",
        postgresql_where=sa.text("geom_3857 IS NOT NULL AND aktualna = true"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "idx_szkola_geom_3857_active_any_zlikwidowana",
        table_name="szkola",
        postgresql_using="gist",
    )
