"""empty message

Revision ID: e6c18970fa9f
Revises: 6462d6093c76
Create Date: 2019-08-27 17:47:37.290746

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'e6c18970fa9f'
down_revision = '6462d6093c76'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sub__coment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('upload_time', sa.DateTime(), nullable=True),
    sa.Column('like_num', sa.Integer(), nullable=True),
    sa.Column('body', sa.String(length=500), nullable=True),
    sa.Column('to_cmmt_id', sa.Integer(), nullable=True),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.Column('under_cmmt_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['under_cmmt_id'], ['comment.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_column('comment', 'to_cmmt_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comment', sa.Column('to_cmmt_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.drop_table('sub__coment')
    # ### end Alembic commands ###
