"""backet

Revision ID: 28b1dc671d7d
Revises: 0d55054c9471
Create Date: 2025-02-23 14:23:02.954581

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '28b1dc671d7d'
down_revision = '0d55054c9471'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('backet', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('backet', schema=None) as batch_op:
        batch_op.drop_column('created_at')

    # ### end Alembic commands ###
