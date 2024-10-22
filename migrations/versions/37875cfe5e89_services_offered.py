"""services offered

Revision ID: 37875cfe5e89
Revises: 4d04eb684aec
Create Date: 2024-04-24 21:38:52.276788

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '37875cfe5e89'
down_revision = '4d04eb684aec'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('facility', schema=None) as batch_op:
        batch_op.add_column(sa.Column('daycare', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('boarding', sa.Boolean(), nullable=True))
        batch_op.drop_column('services_offered')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('facility', schema=None) as batch_op:
        batch_op.add_column(sa.Column('services_offered', sa.TEXT(), nullable=True))
        batch_op.drop_column('boarding')
        batch_op.drop_column('daycare')

    # ### end Alembic commands ###