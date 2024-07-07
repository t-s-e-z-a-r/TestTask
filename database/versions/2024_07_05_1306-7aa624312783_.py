"""empty message

Revision ID: 7aa624312783
Revises: 48d137b96a64
Create Date: 2024-07-05 13:06:21.977655

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7aa624312783"
down_revision: Union[str, None] = "48d137b96a64"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("comments", sa.Column("parent_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "comments", "comments", ["parent_id"], ["id"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "comments", type_="foreignkey")
    op.drop_column("comments", "parent_id")
    # ### end Alembic commands ###
