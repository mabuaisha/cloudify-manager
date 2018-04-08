"""4.3 to 4.4 - add is_hidden_value column to secrets table

Revision ID: c7652b2a97a4
Revises: 3483e421713d
Create Date: 2018-04-03 14:31:11.832546

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c7652b2a97a4'
down_revision = '3483e421713d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    # server_default accepts string or SQL element only
    op.add_column('secrets', sa.Column('is_hidden_value',
                                       sa.Boolean(),
                                       nullable=False,
                                       server_default='f'))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('secrets', 'is_hidden_value')
    # ### end Alembic commands ###
