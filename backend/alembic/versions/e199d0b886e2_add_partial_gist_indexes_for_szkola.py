"""add partial gist indexes for szkola

Revision ID: e199d0b886e2
Revises: 764081c811b1
Create Date: 2026-02-21 19:53:36.394837

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'e199d0b886e2'
down_revision: Union[str, Sequence[str], None] = '764081c811b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("DROP INDEX IF EXISTS public.idx_szkola_geom_3857")

    op.create_index(
        "idx_szkola_geom_3857_active_not_zlikwidowana",
        "szkola",
        ["geom_3857"],
        unique=False,
        postgresql_using="gist",
        postgresql_where=sa.text(
            "geom_3857 IS NOT NULL AND aktualna = true AND zlikwidowana = false"
        ),
    )
    op.create_index(
        "idx_szkola_geom_3857_active_zlikwidowana",
        "szkola",
        ["geom_3857"],
        unique=False,
        postgresql_using="gist",
        postgresql_where=sa.text(
            "geom_3857 IS NOT NULL AND aktualna = true AND zlikwidowana = true"
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "idx_szkola_geom_3857_active_zlikwidowana",
        table_name="szkola",
        postgresql_using="gist",
    )
    op.drop_index(
        "idx_szkola_geom_3857_active_not_zlikwidowana",
        table_name="szkola",
        postgresql_using="gist",
    )

    op.create_index(
        "idx_szkola_geom_3857",
        "szkola",
        ["geom_3857"],
        unique=False,
        postgresql_using="gist",
    )
