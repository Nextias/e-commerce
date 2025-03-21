"""init project

Revision ID: 9b330ff29d34
Revises: 
Create Date: 2025-03-10 15:25:04.782680

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9b330ff29d34'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('category', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_category_name'), ['name'], unique=False)

    op.create_table('order_status',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('order_status', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_order_status_name'), ['name'], unique=False)

    op.create_table('product',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('description', sa.String(length=140), nullable=False),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('rating', sa.Float(), nullable=True),
    sa.Column('brand', sa.String(length=40), nullable=True),
    sa.Column('stock', sa.Integer(), nullable=False),
    sa.Column('photo_path', sa.String(length=200), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_product_name'), ['name'], unique=True)

    op.create_table('role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=20), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('role', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_role_name'), ['name'], unique=True)

    op.create_table('categories',
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
    sa.PrimaryKeyConstraint('category_id', 'product_id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password_hash', sa.String(length=256), nullable=False),
    sa.Column('about_me', sa.String(length=140), nullable=True),
    sa.Column('first_name', sa.String(length=30), nullable=True),
    sa.Column('last_name', sa.String(length=30), nullable=True),
    sa.Column('phone_number', sa.String(length=20), nullable=True),
    sa.Column('address', sa.String(length=60), nullable=True),
    sa.Column('banned', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_user_role_id'), ['role_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_user_username'), ['username'], unique=True)

    op.create_table('basket',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('basket', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_basket_user_id'), ['user_id'], unique=False)

    op.create_table('review',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('review', sa.String(length=140), nullable=True),
    sa.Column('rating', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('review', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_review_product_id'), ['product_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_review_user_id'), ['user_id'], unique=False)

    op.create_table('basket_products',
    sa.Column('basket_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['basket_id'], ['basket.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
    sa.PrimaryKeyConstraint('basket_id', 'product_id')
    )
    op.create_table('order',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_number', sa.String(length=40), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('shipment_date', sa.Date(), nullable=True),
    sa.Column('status_id', sa.Integer(), nullable=False),
    sa.Column('address', sa.String(length=60), nullable=True),
    sa.Column('total_amount', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('basket_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['basket_id'], ['basket.id'], ),
    sa.ForeignKeyConstraint(['status_id'], ['order_status.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_order_order_number'), ['order_number'], unique=True)
        batch_op.create_index(batch_op.f('ix_order_status_id'), ['status_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_order_user_id'), ['user_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_order_user_id'))
        batch_op.drop_index(batch_op.f('ix_order_status_id'))
        batch_op.drop_index(batch_op.f('ix_order_order_number'))

    op.drop_table('order')
    op.drop_table('basket_products')
    with op.batch_alter_table('review', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_review_user_id'))
        batch_op.drop_index(batch_op.f('ix_review_product_id'))

    op.drop_table('review')
    with op.batch_alter_table('basket', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_basket_user_id'))

    op.drop_table('basket')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_username'))
        batch_op.drop_index(batch_op.f('ix_user_role_id'))
        batch_op.drop_index(batch_op.f('ix_user_email'))

    op.drop_table('user')
    op.drop_table('categories')
    with op.batch_alter_table('role', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_role_name'))

    op.drop_table('role')
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_product_name'))

    op.drop_table('product')
    with op.batch_alter_table('order_status', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_order_status_name'))

    op.drop_table('order_status')
    with op.batch_alter_table('category', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_category_name'))

    op.drop_table('category')
    # ### end Alembic commands ###
