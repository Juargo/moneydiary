from alembic import op
import sqlalchemy as sa

def upgrade():
    # First, create tables with no foreign key dependencies
    op.create_table('category_groups',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('is_expense', sa.Boolean, nullable=False),
        sa.Column('icon', sa.String),
        sa.Column('display_order', sa.Integer, default=0),
        sa.Column('created_at', sa.TIMESTAMP),
        sa.Column('updated_at', sa.TIMESTAMP)
    )

    op.create_table('account_types',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('description', sa.String),
        sa.Column('icon', sa.String),
        sa.Column('created_at', sa.TIMESTAMP),
        sa.Column('updated_at', sa.TIMESTAMP)
    )

    op.create_table('financial_methods',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('key', sa.String, unique=True, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP),
        sa.Column('updated_at', sa.TIMESTAMP)
    )

    op.create_table('transaction_statuses',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('description', sa.String),
        sa.Column('created_at', sa.TIMESTAMP),
        sa.Column('updated_at', sa.TIMESTAMP)
    )

    # Then create tables that depend on primary tables
    op.create_table('users',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('email', sa.String, unique=True, nullable=False),
        sa.Column('password_hash', sa.String, nullable=False),
        sa.Column('default_financial_method_id', sa.Integer, sa.ForeignKey('financial_methods.id')),
        sa.Column('created_at', sa.TIMESTAMP),
        sa.Column('updated_at', sa.TIMESTAMP)
    )

    op.create_table('categories',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('category_group_id', sa.Integer, sa.ForeignKey('category_groups.id')),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('is_income', sa.Boolean, nullable=False),
        sa.Column('icon', sa.String),
        sa.Column('display_order', sa.Integer, default=0),
        sa.Column('created_at', sa.TIMESTAMP),
        sa.Column('updated_at', sa.TIMESTAMP)
    )

    # Then tables that depend on users and categories
    op.create_table('subcategories',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('category_id', sa.Integer, sa.ForeignKey('categories.id'), nullable=False),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('display_order', sa.Integer, default=0),
        sa.Column('created_at', sa.TIMESTAMP),
        sa.Column('updated_at', sa.TIMESTAMP)
    )

    op.create_table('accounts',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('account_type_id', sa.Integer, sa.ForeignKey('account_types.id'), nullable=False),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('current_balance', sa.Numeric, nullable=False, default=0),
        sa.Column('is_tracking_only', sa.Boolean, nullable=False, default=False),
        sa.Column('include_in_net_worth', sa.Boolean, nullable=False, default=True),
        sa.Column('created_at', sa.TIMESTAMP),
        sa.Column('updated_at', sa.TIMESTAMP)
    )
    op.create_table('envelopes',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('category_id', sa.Integer, sa.ForeignKey('categories.id')),
        sa.Column('monthly_allocation', sa.Numeric, nullable=False, default=0),
        sa.Column('current_balance', sa.Numeric, nullable=False, default=0),
        sa.Column('rollover', sa.Boolean, nullable=False, default=True),
        sa.Column('created_at', sa.TIMESTAMP),
        sa.Column('updated_at', sa.TIMESTAMP)
    )

    op.create_table('budget_plans',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('financial_method_id', sa.Integer, sa.ForeignKey('financial_methods.id'), nullable=False),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('total_income', sa.Numeric, nullable=False, default=0),
        sa.Column('total_expenses', sa.Numeric, nullable=False, default=0),
        sa.Column('start_date', sa.Date, nullable=False),
        sa.Column('end_date', sa.Date, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.TIMESTAMP),
        sa.Column('updated_at', sa.TIMESTAMP)
    )

    # Create financial method specific tables
    op.create_table('method_fifty_thirty_twenty',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('needs_percentage', sa.Numeric, nullable=False, default=50),
        sa.Column('wants_percentage', sa.Numeric, nullable=False, default=30),
        sa.Column('savings_percentage', sa.Numeric, nullable=False, default=20),
        sa.Column('created_at', sa.TIMESTAMP),
        sa.Column('updated_at', sa.TIMESTAMP)
    )
    op.create_table('method_envelope',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('is_physical', sa.Boolean, nullable=False, default=False),
        sa.Column('rollover_unused', sa.Boolean, nullable=False, default=True),
        sa.Column('created_at', sa.TIMESTAMP),
        sa.Column('updated_at', sa.TIMESTAMP)
    )

    op.create_table('method_zero_based',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('include_investments', sa.Boolean, nullable=False, default=True),
        sa.Column('created_at', sa.TIMESTAMP),
        sa.Column('updated_at', sa.TIMESTAMP)
    )

    op.create_table('method_kakebo',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('monthly_saving_goal', sa.Numeric, nullable=False, default=0),
        sa.Column('use_weekly_reflection', sa.Boolean, nullable=False, default=True),
        sa.Column('created_at', sa.TIMESTAMP),
        sa.Column('updated_at', sa.TIMESTAMP)
    )

    op.create_table('method_pay_yourself_first',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('saving_percentage', sa.Numeric, nullable=False, default=20),
        sa.Column('investment_percentage', sa.Numeric, nullable=False, default=10),
        sa.Column('created_at', sa.TIMESTAMP),
        sa.Column('updated_at', sa.TIMESTAMP)
    )

    op.create_table('recurring_patterns',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('amount', sa.Numeric, nullable=False),
        sa.Column('frequency', sa.String, nullable=False),
        sa.Column('day_of_month', sa.Integer),
        sa.Column('day_of_week', sa.Integer),
        sa.Column('month', sa.Integer),
        sa.Column('description', sa.Text),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('created_at', sa.TIMESTAMP),
        sa.Column('updated_at', sa.TIMESTAMP)
    )

    # Add CSV imports table
    op.create_table('csv_imports',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('filename', sa.String, nullable=False),
        sa.Column('original_filename', sa.String, nullable=False),
        sa.Column('record_count', sa.Integer, nullable=False, default=0),
        sa.Column('success_count', sa.Integer, nullable=False, default=0),
        sa.Column('error_count', sa.Integer, nullable=False, default=0),
        sa.Column('duplicate_count', sa.Integer, nullable=False, default=0),
        sa.Column('status', sa.String, nullable=False),
        sa.Column('started_at', sa.TIMESTAMP),
        sa.Column('completed_at', sa.TIMESTAMP),
        sa.Column('created_at', sa.TIMESTAMP),
        sa.Column('updated_at', sa.TIMESTAMP)
    )

    # Finally, tables that depend on multiple other tables
    op.create_table('transactions',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('account_id', sa.Integer, sa.ForeignKey('accounts.id'), nullable=False),
        sa.Column('transfer_account_id', sa.Integer, sa.ForeignKey('accounts.id')),
        sa.Column('category_id', sa.Integer, sa.ForeignKey('categories.id')),
        sa.Column('subcategory_id', sa.Integer, sa.ForeignKey('subcategories.id')),
        sa.Column('envelope_id', sa.Integer, sa.ForeignKey('envelopes.id')),
        sa.Column('status_id', sa.Integer, sa.ForeignKey('transaction_statuses.id'), nullable=False),
        sa.Column('recurring_pattern_id', sa.Integer, sa.ForeignKey('recurring_patterns.id')),
        sa.Column('import_id', sa.Integer, sa.ForeignKey('csv_imports.id')),
        sa.Column('external_id', sa.String),
        sa.Column('amount', sa.Numeric, nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('notes', sa.Text),
        sa.Column('transaction_date', sa.Date, nullable=False),
        sa.Column('is_recurring', sa.Boolean, nullable=False, default=False),
        sa.Column('is_planned', sa.Boolean, nullable=False, default=False),
        sa.Column('kakebo_emotion', sa.String),
        sa.Column('created_at', sa.TIMESTAMP),
        sa.Column('updated_at', sa.TIMESTAMP)
    )

    op.create_table('budget_items',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('budget_id', sa.Integer, sa.ForeignKey('budget_plans.id'), nullable=False),
        sa.Column('category_id', sa.Integer, sa.ForeignKey('categories.id'), nullable=False),
        sa.Column('subcategory_id', sa.Integer, sa.ForeignKey('subcategories.id')),
        sa.Column('envelope_id', sa.Integer, sa.ForeignKey('envelopes.id')),
        sa.Column('amount', sa.Numeric, nullable=False),
        sa.Column('month_year', sa.String, nullable=False),
        sa.Column('notes', sa.Text),
        sa.Column('created_at', sa.TIMESTAMP),
        sa.Column('updated_at', sa.TIMESTAMP)
    )

def downgrade():
    # Drop tables in reverse dependency order
    op.drop_table('budget_items')
    op.drop_table('transactions')
    op.drop_table('recurring_patterns')
    op.drop_table('csv_imports')
    op.drop_table('method_pay_yourself_first')
    op.drop_table('method_kakebo')
    op.drop_table('method_zero_based')
    op.drop_table('method_envelope')
    op.drop_table('method_fifty_thirty_twenty')
    op.drop_table('budget_plans')
    op.drop_table('envelopes')
    op.drop_table('accounts')
    op.drop_table('subcategories')
    op.drop_table('categories')
    op.drop_table('users')
    op.drop_table('transaction_statuses')
    op.drop_table('financial_methods')
    op.drop_table('account_types')
    op.drop_table('category_groups')
