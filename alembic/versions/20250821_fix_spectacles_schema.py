"""
Fix spectacles schema to match application model

Revision ID: 20250821_fix_spectacles_schema
Revises: 4a9b8c7d6e5f
Create Date: 2025-08-21
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20250821_fix_spectacles_schema'
down_revision: Union[str, None] = '4a9b8c7d6e5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if 'spectacles' not in inspector.get_table_names():
        # Create full table if missing
        op.create_table(
            'spectacles',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('name', sa.String(255), nullable=False),
            sa.Column('brand', sa.String(100), nullable=False, server_default='Unknown'),
            sa.Column('price', sa.Float(), nullable=False, server_default='0'),
            sa.Column('image_url', sa.String(500)),
            sa.Column('frame_material', sa.String(100)),
            sa.Column('frame_shape', sa.String(50)),
            sa.Column('lens_type', sa.String(50)),
            sa.Column('gender', sa.String(20)),
            sa.Column('age_group', sa.String(50)),
            sa.Column('description', sa.Text()),
            sa.Column('specifications', sa.JSON()),
            sa.Column('quantity', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('in_stock', sa.Boolean(), nullable=False, server_default=sa.text('true')),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
            sa.Column('updated_at', sa.DateTime(timezone=True)),
        )
        return

    cols = {c['name'] for c in inspector.get_columns('spectacles')}

    # Rename model_name -> name if needed
    if 'name' not in cols and 'model_name' in cols:
        op.add_column('spectacles', sa.Column('name', sa.String(255), nullable=True))
        op.execute("UPDATE spectacles SET name = model_name")
        op.alter_column('spectacles', 'name', nullable=False)
        cols.add('name')

    # Map stock -> quantity
    if 'quantity' not in cols and 'stock' in cols:
        op.add_column('spectacles', sa.Column('quantity', sa.Integer(), nullable=False, server_default='0'))
        op.execute("UPDATE spectacles SET quantity = COALESCE(stock, 0)")
        cols.add('quantity')

    # Ensure required columns exist
    required = [
        ('brand', sa.String(100), False, "'Unknown'"),
        ('price', sa.Float(), False, '0'),
        ('image_url', sa.String(500), True, None),
        ('frame_material', sa.String(100), True, None),
        ('frame_shape', sa.String(50), True, None),
        ('lens_type', sa.String(50), True, None),
        ('gender', sa.String(20), True, None),
        ('age_group', sa.String(50), True, None),
        ('description', sa.Text(), True, None),
        ('specifications', sa.JSON(), True, None),
        ('in_stock', sa.Boolean(), False, 'true'),
        ('created_at', sa.DateTime(timezone=True), True, 'NOW()'),
        ('updated_at', sa.DateTime(timezone=True), True, None),
    ]

    for name, coltype, nullable, default in required:
        if name not in cols:
            if default is not None:
                op.add_column('spectacles', sa.Column(name, coltype, nullable=nullable, server_default=sa.text(default)))
            else:
                op.add_column('spectacles', sa.Column(name, coltype, nullable=nullable))


def downgrade() -> None:
    # Non-trivial to downgrade reliably; leaving as no-op.
    pass
