"""empty message

Revision ID: 9e7a2421dcf5
Revises: 
Create Date: 2023-03-16 18:14:43.449124

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '9e7a2421dcf5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('admin_token_old', schema=None) as batch_op:
        batch_op.drop_index('token_value')

    with op.batch_alter_table('administrator', schema=None) as batch_op:
        batch_op.add_column(sa.Column('actived', sa.Boolean(), nullable=False))
        batch_op.drop_column('active')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('administrator', schema=None) as batch_op:
        batch_op.add_column(sa.Column('active', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False))
        batch_op.drop_column('actived')

    with op.batch_alter_table('admin_token_old', schema=None) as batch_op:
        batch_op.create_index('token_value', ['token_value'], unique=False)

    # ### end Alembic commands ###
