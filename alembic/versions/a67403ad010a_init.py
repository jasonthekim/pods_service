"""init2

Revision ID: a67403ad010a
Revises: 
Create Date: 2022-06-28 21:00:50.688816

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel              ##### Required when using sqlmodel and not use sqlalchemy
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a67403ad010a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade(engine_name):
    globals()["upgrade_alltenants"]()


def downgrade(engine_name):
    globals()["downgrade_alltenants"]()




def upgrade_alltenants():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('exporteddata',
    sa.Column('source_pod', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('tag', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('roles_required', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('tenant_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('site_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('creation_ts', sa.DateTime(), nullable=True),
    sa.Column('update_ts', sa.DateTime(), nullable=True),
    sa.Column('roles_inherited', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('export_path', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('source_owner', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.PrimaryKeyConstraint('source_pod')
    )
    op.create_table('password',
    sa.Column('pod_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('admin_username', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('admin_password', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('user_username', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('user_password', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('tenant_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('site_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.PrimaryKeyConstraint('pod_id')
    )
    op.create_table('pod',
    sa.Column('environment_variables', sa.JSON(), nullable=True),
    sa.Column('data_requests', postgresql.ARRAY(sa.String()), nullable=True),
    sa.Column('roles_required', postgresql.ARRAY(sa.String()), nullable=True),
    sa.Column('status_container', sa.JSON(), nullable=True),
    sa.Column('data_attached', postgresql.ARRAY(sa.String()), nullable=True),
    sa.Column('roles_inherited', postgresql.ARRAY(sa.String()), nullable=True),
    sa.Column('permissions', postgresql.ARRAY(sa.String(), dimensions=1), nullable=True),
    sa.Column('pod_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('pod_template', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('status_requested', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('tenant_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('site_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('k8_name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('url', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('status', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('creation_ts', sa.DateTime(), nullable=True),
    sa.Column('update_ts', sa.DateTime(), nullable=True),
    sa.Column('server_protocol', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('routing_port', sa.Integer(), nullable=True),
    sa.Column('instance_port', sa.Integer(), nullable=True),
    sa.Column('logs', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.PrimaryKeyConstraint('pod_id')
    )
    # ### end Alembic commands ###


def downgrade_alltenants():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('pod')
    op.drop_table('password')
    op.drop_table('exporteddata')
    # ### end Alembic commands ###