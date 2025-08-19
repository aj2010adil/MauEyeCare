from alembic import op
import sqlalchemy as sa


revision = '0002_pos_and_inventory'
down_revision = '0001_init'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('category', sa.String(32), nullable=False, index=True),
        sa.Column('hsn_sac', sa.String(16)),
        sa.Column('brand', sa.String(100)),
        sa.Column('color', sa.String(50)),
        sa.Column('eye_size', sa.String(16)),
        sa.Column('gst_rate', sa.Numeric(5,2), server_default='0'),
        sa.Column('mrp', sa.Numeric(10,2), server_default='0'),
        sa.Column('price', sa.Numeric(10,2), server_default='0'),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true')),
        sa.Column('schedule_h', sa.Boolean(), server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('ix_products_name', 'products', ['name'])
    op.create_index('ix_products_category', 'products', ['category'])
    op.create_index('ix_products_brand', 'products', ['brand'])
    op.create_index('ix_products_cat_brand', 'products', ['category', 'brand'])

    op.create_table(
        'stock_batches',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False),
        sa.Column('batch_no', sa.String(64), nullable=False),
        sa.Column('expiry_date', sa.Date()),
        sa.Column('quantity', sa.Integer(), server_default='0'),
        sa.Column('cost_price', sa.Numeric(10,2), server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('is_schedule_h', sa.Boolean(), server_default=sa.text('false')),
    )
    op.create_index('ix_stock_expiry', 'stock_batches', ['expiry_date'])

    op.create_table(
        'goods_receipts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('vendor_name', sa.String(255), nullable=False),
        sa.Column('invoice_no', sa.String(64)),
        sa.Column('received_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    op.create_table(
        'goods_receipt_lines',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('goods_receipt_id', sa.Integer(), sa.ForeignKey('goods_receipts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('batch_no', sa.String(64), nullable=False),
        sa.Column('expiry_date', sa.Date()),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('cost_price', sa.Numeric(10,2), nullable=False),
    )

    op.create_table(
        'loyalty_accounts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('patient_id', sa.Integer(), index=True),
        sa.Column('points', sa.Integer(), server_default='0'),
    )

    op.create_table(
        'pos_orders',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('patient_id', sa.Integer()),
        sa.Column('order_no', sa.String(32)),
        sa.Column('subtotal', sa.Numeric(10,2), server_default='0'),
        sa.Column('gst_amount', sa.Numeric(10,2), server_default='0'),
        sa.Column('discount_amount', sa.Numeric(10,2), server_default='0'),
        sa.Column('total', sa.Numeric(10,2), server_default='0'),
        sa.Column('paid_amount', sa.Numeric(10,2), server_default='0'),
        sa.Column('loyalty_points_earned', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('ix_pos_orders_created_at', 'pos_orders', ['created_at'])

    op.create_table(
        'pos_order_lines',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('order_id', sa.Integer(), sa.ForeignKey('pos_orders.id', ondelete='CASCADE'), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('batch_id', sa.Integer()),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('price', sa.Numeric(10,2), nullable=False),
        sa.Column('gst_rate', sa.Numeric(5,2), server_default='0'),
        sa.Column('discount_rate', sa.Numeric(5,2), server_default='0'),
    )

    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('order_id', sa.Integer(), sa.ForeignKey('pos_orders.id', ondelete='CASCADE'), nullable=False),
        sa.Column('method', sa.String(32), nullable=False),
        sa.Column('amount', sa.Numeric(10,2), nullable=False),
        sa.Column('reference', sa.String(64)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    op.create_table(
        'lab_jobs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('order_id', sa.Integer()),
        sa.Column('patient_id', sa.Integer()),
        sa.Column('frame_measurements', sa.JSON()),
        sa.Column('seg_heights', sa.JSON()),
        sa.Column('status', sa.String(32), server_default='created'),
        sa.Column('barcode', sa.String(64)),
        sa.Column('supplier', sa.String(100)),
        sa.Column('technician', sa.String(100)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    op.create_table(
        'lab_remakes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('lab_job_id', sa.Integer(), sa.ForeignKey('lab_jobs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('reason', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    op.create_table(
        'consents',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('visit_id', sa.Integer()),
        sa.Column('type', sa.String(64), nullable=False),
        sa.Column('content', sa.JSON(), nullable=False),
        sa.Column('signed_by', sa.String(100), nullable=False),
        sa.Column('signed_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )


def downgrade() -> None:
    op.drop_table('consents')
    op.drop_table('lab_remakes')
    op.drop_table('lab_jobs')
    op.drop_table('payments')
    op.drop_table('pos_order_lines')
    op.drop_index('ix_pos_orders_created_at', table_name='pos_orders')
    op.drop_table('pos_orders')
    op.drop_table('loyalty_accounts')
    op.drop_table('goods_receipt_lines')
    op.drop_table('goods_receipts')
    op.drop_index('ix_stock_expiry', table_name='stock_batches')
    op.drop_table('stock_batches')
    op.drop_index('ix_products_cat_brand', table_name='products')
    op.drop_index('ix_products_brand', table_name='products')
    op.drop_index('ix_products_category', table_name='products')
    op.drop_index('ix_products_name', table_name='products')
    op.drop_table('products')


