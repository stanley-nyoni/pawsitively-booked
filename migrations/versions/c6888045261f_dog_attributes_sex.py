"""dog attributes - sex

Revision ID: c6888045261f
Revises: 24bf4d0a9cbc
Create Date: 2024-04-30 16:20:16.180486

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c6888045261f'
down_revision = '24bf4d0a9cbc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('dog', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sex', sa.String(length=64), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('dog', schema=None) as batch_op:
        batch_op.drop_column('sex')

    # ### end Alembic commands ###