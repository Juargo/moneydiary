from sqlalchemy import Column, Integer, String, Boolean, Date, Decimal, ForeignKey, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table('users',
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('name', String, nullable=False),
        Column('email', String, unique=True, nullable=False),
        Column('password_hash', String, nullable=False),
        Column('default_financial_method_id', Integer, ForeignKey('financial_methods.id')),
        Column('created_at', TIMESTAMP),
        Column('updated_at', TIMESTAMP)
    )

    op.create_table('accounts',
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
        Column('account_type_id', Integer, ForeignKey('account_types.id'), nullable=False),
        Column('name', String, nullable=False),
        Column('current_balance', Decimal, nullable=False, default=0),
        Column('is_tracking_only', Boolean, nullable=False, default=False),
        Column('include_in_net_worth', Boolean, nullable=False, default=True),
        Column('created_at', TIMESTAMP),
        Column('updated_at', TIMESTAMP)
    )

    op.create_table('account_types',
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('name', String, nullable=False),
        Column('description', String),
        Column('icon', String),
        Column('created_at', TIMESTAMP),
        Column('updated_at', TIMESTAMP)
    )

    op.create_table('category_groups',
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('name', String, nullable=False),
        Column('is_expense', Boolean, nullable=False),
        Column('icon', String),
        Column('display_order', Integer, default=0),
        Column('created_at', TIMESTAMP),
        Column('updated_at', TIMESTAMP)
    )

    op.create_table('categories',
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('category_group_id', Integer, ForeignKey('category_groups.id')),
        Column('name', String, nullable=False),
        Column('is_income', Boolean, nullable=False),
        Column('icon', String),
        Column('display_order', Integer, default=0),
        Column('created_at', TIMESTAMP),
        Column('updated_at', TIMESTAMP)
    )

    op.create_table('subcategories',
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('category_id', Integer, ForeignKey('categories.id'), nullable=False),
        Column('name', String, nullable=False),
        Column('display_order', Integer, default=0),
        Column('created_at', TIMESTAMP),
        Column('updated_at', TIMESTAMP)
    )

    op.create_table('financial_methods',
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('name', String, nullable=False),
        Column('description', Text),
        Column('key', String, unique=True, nullable=False),
        Column('created_at', TIMESTAMP),
        Column('updated_at', TIMESTAMP)
    )

    op.create_table('method_fifty_thirty_twenty',
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
        Column('needs_percentage', Decimal, nullable=False, default=50),
        Column('wants_percentage', Decimal, nullable=False, default=30),
        Column('savings_percentage', Decimal, nullable=False, default=20),
        Column('created_at', TIMESTAMP),
        Column('updated_at', TIMESTAMP)
    )

    op.create_table('method_envelope',
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
        Column('is_physical', Boolean, nullable=False, default=False),
        Column('rollover_unused', Boolean, nullable=False, default=True),
        Column('created_at', TIMESTAMP),
        Column('updated_at', TIMESTAMP)
    )

    op.create_table('method_zero_based',
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
        Column('include_investments', Boolean, nullable=False, default=True),
        Column('created_at', TIMESTAMP),
        Column('updated_at', TIMESTAMP)
    )

    op.create_table('method_kakebo',
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
        Column('monthly_saving_goal', Decimal, nullable=False, default=0),
        Column('use_weekly_reflection', Boolean, nullable=False, default=True),
        Column('created_at', TIMESTAMP),
        Column('updated_at', TIMESTAMP)
    )

    op.create_table('method_pay_yourself_first',
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
        Column('saving_percentage', Decimal, nullable=False, default=20),
        Column('investment_percentage', Decimal, nullable=False, default=10),
        Column('created_at', TIMESTAMP),
        Column('updated_at', TIMESTAMP)
    )

    op.create_table('envelopes',
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
        Column('name', String, nullable=False),
        Column('category_id', Integer, ForeignKey('categories.id')),
        Column('monthly_allocation', Decimal, nullable=False, default=0),
        Column('current_balance', Decimal, nullable=False, default=0),
        Column('rollover', Boolean, nullable=False, default=True),
        Column('created_at', TIMESTAMP),
        Column('updated_at', TIMESTAMP)
    )

    op.create_table('transactions',
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
        Column('account_id', Integer, ForeignKey('accounts.id'), nullable=False),
        Column('transfer_account_id', Integer, ForeignKey('accounts.id')),
        Column('category_id', Integer, ForeignKey('categories.id')),
        Column('subcategory_id', Integer, ForeignKey('subcategories.id')),
        Column('envelope_id', Integer, ForeignKey('envelopes.id')),
        Column('status_id', Integer, ForeignKey('transaction_statuses.id'), nullable=False),
        Column('amount', Decimal, nullable=False),
        Column('description', Text),
        Column('transaction_date', Date, nullable=False),
        Column('is_recurring', Boolean, nullable=False, default=False),
        Column('is_planned', Boolean, nullable=False, default=False),
        Column('created_at', TIMESTAMP),
        Column('updated_at', TIMESTAMP)
    )

    op.create_table('transaction_statuses',
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('name', String, nullable=False),
        Column('description', String),
        Column('created_at', TIMESTAMP),
        Column('updated_at', TIMESTAMP)
    )

def downgrade():
    op.drop_table('transactions')
    op.drop_table('transaction_statuses')
    op.drop_table('envelopes')
    op.drop_table('method_pay_yourself_first')
    op.drop_table('method_kakebo')
    op.drop_table('method_zero_based')
    op.drop_table('method_envelope')
    op.drop_table('method_fifty_thirty_twenty')
    op.drop_table('financial_methods')
    op.drop_table('subcategories')
    op.drop_table('categories')
    op.drop_table('category_groups')
    op.drop_table('account_types')
    op.drop_table('accounts')
    op.drop_table('users')