"""s3 saved flag

Revision ID: 0da1ea31e4ce
Revises: fd5ec41fab96
Create Date: 2024-11-28 17:42:09.632135

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0da1ea31e4ce"
down_revision: Union[str, None] = "fd5ec41fab96"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "files",
        sa.Column("is_saved_to_s3", sa.Boolean, default=False, nullable=False),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("files", "is_saved_to_s3")
    # ### end Alembic commands ###
