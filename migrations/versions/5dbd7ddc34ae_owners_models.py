"""owners models

Revision ID: 5dbd7ddc34ae
Revises: 125398646d75
Create Date: 2024-04-21 23:51:23.021778

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5dbd7ddc34ae'
down_revision = '125398646d75'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('dog_owner',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('facility_owner',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('dog',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('breed', sa.String(length=64), nullable=True),
    sa.Column('age', sa.Integer(), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['dog_owner.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('dog', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_dog_name'), ['name'], unique=True)

    op.create_table('facility',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('location', sa.String(length=64), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['facility_owner.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('facility', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_facility_name'), ['name'], unique=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('facility', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_facility_name'))

    op.drop_table('facility')
    with op.batch_alter_table('dog', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_dog_name'))

    op.drop_table('dog')
    op.drop_table('facility_owner')
    op.drop_table('dog_owner')
    # ### end Alembic commands ###