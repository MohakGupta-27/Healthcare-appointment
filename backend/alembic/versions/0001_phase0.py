"""Phase 0 empty schema placeholder.

Revision ID: 0001_phase0
Revises:
"""

from typing import Sequence, Union

revision: str = "0001_phase0"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
