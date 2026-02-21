"""add trigger for geom_3857

Revision ID: 931733737e93
Revises: e199d0b886e2
Create Date: 2026-02-21 20:13:07.681463

"""
from pathlib import Path
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '931733737e93'
down_revision: Union[str, Sequence[str], None] = 'e199d0b886e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    sql = Path(__file__).parent / "sql" / "szkola_geom_3857_trigger.sql"
    op.execute(sql.read_text())


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TRIGGER IF EXISTS trg_szkola_set_geom_3857 ON public.szkola")
    op.execute("DROP FUNCTION IF EXISTS public.szkola_set_geom_3857()") 
