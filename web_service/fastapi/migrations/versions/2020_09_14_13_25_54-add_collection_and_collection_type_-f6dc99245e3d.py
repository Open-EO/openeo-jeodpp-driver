"""add collection and collection_type tables

Revision ID: f6dc99245e3d
Revises: 
Create Date: 2020-09-14 13:25:54.735659

"""
from alembic import op
import fastapi_utils.guid_type
import geoalchemy2.types
import sqlalchemy as sa
import sqlalchemy_utils
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f6dc99245e3d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('collection_type',
    sa.Column('collection_type_oid', sa.Integer(), nullable=False),
    sa.Column('collection_type_name', sa.String(), nullable=False),
    sa.Column('collection_type_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('created', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('collection_type_oid', name=op.f('pk_collection_type')),
    sa.UniqueConstraint('collection_type_name', name=op.f('uq_collection_type_collection_type_name')),
    schema='openeo_dev'
    )
    op.create_table('collection',
    sa.Column('collection_oid', sa.Integer(), nullable=False),
    sa.Column('collection_id', sa.String(), nullable=False),
    sa.Column('collection_footprint', geoalchemy2.types.Geometry(geometry_type='MULTIPOLYGON', srid=4326, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry'), nullable=False),
    sa.Column('collection_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('collection_history', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('collection_jeolab', sa.Boolean(), nullable=False),
    sa.Column('collection_type_ref', sa.Integer(), nullable=True),
    sa.Column('updated', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['collection_type_ref'], ['openeo_dev.collection_type.collection_type_oid'], name=op.f('fk_collection_collection_type_ref_collection_type')),
    sa.PrimaryKeyConstraint('collection_oid', name=op.f('pk_collection')),
    sa.UniqueConstraint('collection_id', name=op.f('uq_collection_collection_id')),
    sa.UniqueConstraint('collection_type_ref', name=op.f('uq_collection_collection_type_ref')),
    schema='openeo_dev'
    )
    op.create_index('idx_collection_footprint', 'collection', ['collection_footprint'], unique=False, schema='openeo_dev', postgresql_using='gist')
    op.create_index('idx_collection_history', 'collection', ['collection_history'], unique=False, schema='openeo_dev', postgresql_using='gin')
    op.create_index('idx_collection_identifier', 'collection', ['collection_id'], unique=False, schema='openeo_dev', postgresql_using='btree')
    op.create_index('idx_collection_metadata', 'collection', ['collection_metadata'], unique=False, schema='openeo_dev', postgresql_using='gin')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('idx_collection_metadata', table_name='collection', schema='openeo_dev')
    op.drop_index('idx_collection_identifier', table_name='collection', schema='openeo_dev')
    op.drop_index('idx_collection_history', table_name='collection', schema='openeo_dev')
    op.drop_index('idx_collection_footprint', table_name='collection', schema='openeo_dev')
    op.drop_table('collection', schema='openeo_dev')
    op.drop_table('collection_type', schema='openeo_dev')
    # ### end Alembic commands ###
