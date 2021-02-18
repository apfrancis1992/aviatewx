"""empty message

Revision ID: 0e17d23bcb1e
Revises: 0fa9e6ee676b
Create Date: 2021-02-12 13:52:09.709274

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0e17d23bcb1e'
down_revision = '0fa9e6ee676b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'taf', 'station', ['station_id'], ['station_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'taf', type_='foreignkey')
    # ### end Alembic commands ###
