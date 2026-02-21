"""add pg_trgm extension

Revision ID: ff54b79a33d7
Revises: 931733737e93
Create Date: 2026-02-21 20:38:38.231428

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'ff54b79a33d7'
down_revision: Union[str, Sequence[str], None] = '931733737e93'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute("CREATE INDEX IF NOT EXISTS idx_szkola_nazwa_trgm ON public.szkola USING GIN (nazwa gin_trgm_ops)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_miejscowosc_nazwa_trgm ON public.miejscowosc USING GIN (nazwa gin_trgm_ops)")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP INDEX IF EXISTS public.idx_miejscowosc_nazwa_trgm")
    op.execute("DROP INDEX IF EXISTS public.idx_szkola_nazwa_trgm")
