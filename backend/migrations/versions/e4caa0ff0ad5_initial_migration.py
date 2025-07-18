"""Initial migration

Revision ID: e4caa0ff0ad5
Revises: 
Create Date: 2025-07-03 20:16:16.086801

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e4caa0ff0ad5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('local_scans',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ip_address', sa.String(length=45), nullable=False),
    sa.Column('nmap_result', sa.Text(), nullable=True),
    sa.Column('whois_result', sa.Text(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('local_scans')
    # ### end Alembic commands ###
