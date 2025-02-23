"""Add unique constraint on first_name, last_name, and user_id

Revision ID: ea5bd9a527dd
Revises: 26ddc3f525f6
Create Date: 2025-02-09 20:11:08.763409

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ea5bd9a527dd'
down_revision: Union[str, None] = '26ddc3f525f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('unique_contact', 'contacts', ['first_name', 'last_name', 'user_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('unique_contact', 'contacts', type_='unique')
    # ### end Alembic commands ###
