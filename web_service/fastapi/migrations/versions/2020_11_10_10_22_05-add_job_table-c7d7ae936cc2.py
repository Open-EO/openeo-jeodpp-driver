"""add job table

Revision ID: c7d7ae936cc2
Revises: b6009c870307
Create Date: 2020-11-10 10:22:05.040004

"""
from alembic import op
import fastapi_utils.guid_type
import geoalchemy2.types
import sqlalchemy as sa
import sqlalchemy_utils
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c7d7ae936cc2'
down_revision = 'b6009c870307'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('job',
    sa.Column('id', postgresql.UUID(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('process', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('status', sa.String(), server_default='created', nullable=False),
    sa.Column('progress', sa.Integer(), nullable=True),
    sa.Column('plan', sa.String(), nullable=True),
    sa.Column('costs', sa.Float(), nullable=True),
    sa.Column('budget', sa.Integer(), nullable=True),
    sa.Column('created', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_job')),
    schema='openeo_dev'
    )
    op.create_index('idx_job_description', 'job', ['description'], unique=False, schema='openeo_dev', postgresql_using='btree')
    op.create_index('idx_job_process', 'job', ['process'], unique=False, schema='openeo_dev', postgresql_using='gin')
    op.create_index('idx_job_status', 'job', ['status'], unique=False, schema='openeo_dev', postgresql_using='btree')
    op.create_index('idx_job_title', 'job', ['title'], unique=False, schema='openeo_dev', postgresql_using='btree')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('idx_job_title', table_name='job', schema='openeo_dev')
    op.drop_index('idx_job_status', table_name='job', schema='openeo_dev')
    op.drop_index('idx_job_process', table_name='job', schema='openeo_dev')
    op.drop_index('idx_job_description', table_name='job', schema='openeo_dev')
    op.drop_table('job', schema='openeo_dev')
    # ### end Alembic commands ###
