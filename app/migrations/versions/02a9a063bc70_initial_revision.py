"""Initial revision

Revision ID: 02a9a063bc70
Revises: b842a058d53e
Create Date: 2024-11-13 22:15:44.024885

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '02a9a063bc70'
down_revision: Union[str, None] = 'b842a058d53e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('orders',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('summa', sa.DECIMAL(), nullable=False),
    sa.Column('delivery', sa.String(), nullable=True),
    sa.Column('phone', sa.String(), nullable=True),
    sa.Column('address', sa.String(), nullable=True),
    sa.Column('pay_stat', sa.String(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('comment', sa.Text(), nullable=True),
    sa.Column('time_create', sa.DateTime(), nullable=True),
    sa.Column('time_update', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_orders_id'), 'orders', ['id'], unique=False)
    op.create_index(op.f('ix_orders_user_id'), 'orders', ['user_id'], unique=False)
    op.create_table('orderins',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('menu_id', sa.Integer(), nullable=False),
    sa.Column('time_create', sa.DateTime(), nullable=True),
    sa.Column('time_update', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['menu_id'], ['menus.id'], ),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_orderins_id'), 'orderins', ['id'], unique=False)
    op.create_index(op.f('ix_orderins_menu_id'), 'orderins', ['menu_id'], unique=False)
    op.create_index(op.f('ix_orderins_order_id'), 'orderins', ['order_id'], unique=False)
    op.create_index(op.f('ix_categories_id'), 'categories', ['id'], unique=False)
    op.drop_index('ix_menus_slug', table_name='menus')
    op.drop_column('menus', 'slug')
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.add_column('menus', sa.Column('slug', sa.VARCHAR(), nullable=True))
    op.create_index('ix_menus_slug', 'menus', ['slug'], unique=1)
    op.drop_index(op.f('ix_categories_id'), table_name='categories')
    op.drop_index(op.f('ix_orderins_order_id'), table_name='orderins')
    op.drop_index(op.f('ix_orderins_menu_id'), table_name='orderins')
    op.drop_index(op.f('ix_orderins_id'), table_name='orderins')
    op.drop_table('orderins')
    op.drop_index(op.f('ix_orders_user_id'), table_name='orders')
    op.drop_index(op.f('ix_orders_id'), table_name='orders')
    op.drop_table('orders')
    # ### end Alembic commands ###
