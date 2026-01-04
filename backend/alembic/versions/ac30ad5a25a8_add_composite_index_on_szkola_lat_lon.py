"""add composite index on szkola lat lon

Revision ID: ac30ad5a25a8
Revises: 0d29d728f7e7
Create Date: 2026-01-04 12:51:10.720754

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ac30ad5a25a8"
down_revision: Union[str, Sequence[str], None] = "0d29d728f7e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        "idx_szkola_lat_lon",
        "szkola",
        ["geolokalizacja_latitude", "geolokalizacja_longitude"],
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("idx_szkola_lat_lon", table_name="szkola")
