"""empty message

Revision ID: 65c98df88eb5
Revises: 5331aef1169d
Create Date: 2020-10-15 17:45:58.467627

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '65c98df88eb5'
down_revision = '5331aef1169d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('artist', 'city',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.alter_column('artist', 'state',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.alter_column('venue', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('venue', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('artist', 'state',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.alter_column('artist', 'city',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    # ### end Alembic commands ###
