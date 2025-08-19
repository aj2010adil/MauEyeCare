from alembic import op
import sqlalchemy as sa


revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=32), nullable=False, server_default='doctor'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    op.create_table(
        'patients',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100)),
        sa.Column('gender', sa.String(length=20)),
        sa.Column('age', sa.Integer()),
        sa.Column('phone', sa.String(length=32)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('ix_patients_phone', 'patients', ['phone'])
    op.create_index('ix_patients_name', 'patients', ['first_name', 'last_name'])

    op.create_table(
        'visits',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('patient_id', sa.Integer(), sa.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False),
        sa.Column('visit_date', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('issue', sa.String(length=255)),
        sa.Column('advice', sa.String(length=255)),
        sa.Column('metrics', sa.JSON()),
    )
    op.create_index('ix_visits_patient_id', 'visits', ['patient_id'])
    op.create_index('ix_visits_visit_date', 'visits', ['visit_date'])

    op.create_table(
        'prescriptions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('patient_id', sa.Integer(), sa.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False),
        sa.Column('visit_id', sa.Integer(), sa.ForeignKey('visits.id', ondelete='SET NULL')),
        sa.Column('pdf_path', sa.String(length=500)),
        sa.Column('rx_values', sa.JSON()),
        sa.Column('spectacles', sa.JSON()),
        sa.Column('medicines', sa.JSON()),
        sa.Column('totals', sa.JSON()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('ix_prescriptions_created_at', 'prescriptions', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_prescriptions_created_at', table_name='prescriptions')
    op.drop_table('prescriptions')
    op.drop_index('ix_visits_visit_date', table_name='visits')
    op.drop_index('ix_visits_patient_id', table_name='visits')
    op.drop_table('visits')
    op.drop_index('ix_patients_name', table_name='patients')
    op.drop_index('ix_patients_phone', table_name='patients')
    op.drop_table('patients')
    op.drop_table('users')


