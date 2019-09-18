"""empty message

Revision ID: 688ae74db27d
Revises: 
Create Date: 2019-08-13 12:24:44.038110

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '688ae74db27d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nickname', sa.String(length=60), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_nickname'), 'user', ['nickname'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_nickname'), table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###
