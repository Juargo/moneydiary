"""bank asdas

Revision ID: 8cbb9a57bb80
Revises: 2bf73624c130
Create Date: 2025-05-03 22:44:50.335267

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8cbb9a57bb80'
down_revision: Union[str, None] = '2bf73624c130'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
