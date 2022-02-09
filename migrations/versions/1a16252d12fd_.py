"""empty message

Revision ID: 1a16252d12fd
Revises: f15d8c14ee32
Create Date: 2022-02-06 14:30:25.923661

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1a16252d12fd'
down_revision = 'f15d8c14ee32'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'gender',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'gender',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###
