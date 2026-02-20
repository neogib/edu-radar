"""add martin cluster function

Revision ID: 02bea8fed6cd
Revises: 8b09b66e3ce4
Create Date: 2026-02-20 17:34:34.692877

"""
from pathlib import Path
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "02bea8fed6cd"
down_revision: Union[str, Sequence[str], None] = "8b09b66e3ce4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    sql = Path(__file__).parent / "sql" / "szkola_clustered.sql"
    op.execute(sql.read_text())


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP FUNCTION IF EXISTS public.szkola_clustered(integer, integer, integer, json)")
