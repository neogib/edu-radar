"""make regon and kod_pocztowy nullable

Revision ID: fff7ba934856
Revises: db9f404de7d5
Create Date: 2026-02-02 22:09:12.459381

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'fff7ba934856'
down_revision: Union[str, Sequence[str], None] = 'db9f404de7d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "szkola",
        "regon",
        existing_type=sqlmodel.sql.sqltypes.AutoString(),
        nullable=True,
    )
    op.alter_column(
        "szkola",
        "kod_pocztowy",
        existing_type=sqlmodel.sql.sqltypes.AutoString(),
        nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "szkola",
        "kod_pocztowy",
        existing_type=sqlmodel.sql.sqltypes.AutoString(),
        nullable=False,
    )
    op.alter_column(
        "szkola",
        "regon",
        existing_type=sqlmodel.sql.sqltypes.AutoString(),
        nullable=False,
    )
