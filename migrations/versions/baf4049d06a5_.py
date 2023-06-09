"""empty message

Revision ID: baf4049d06a5
Revises: 9e7a2421dcf5
Create Date: 2023-03-16 18:15:42.373848

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'baf4049d06a5'
down_revision = '9e7a2421dcf5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('administrator', schema=None) as batch_op:
        batch_op.add_column(sa.Column('active', sa.Boolean(), nullable=False))
        batch_op.drop_column('actived')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('administrator', schema=None) as batch_op:
        batch_op.add_column(sa.Column('actived', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False))
        batch_op.drop_column('active')

    # ### end Alembic commands ###
