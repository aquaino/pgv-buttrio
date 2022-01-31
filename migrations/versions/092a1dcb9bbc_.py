"""empty message

Revision ID: 092a1dcb9bbc
Revises: 3b761d9f8f82
Create Date: 2022-01-08 11:41:40.149704

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '092a1dcb9bbc'
down_revision = '3b761d9f8f82'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'user_types', ['name'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user_types', type_='unique')
    # ### end Alembic commands ###