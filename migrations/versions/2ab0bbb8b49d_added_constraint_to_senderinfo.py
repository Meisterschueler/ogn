"""Added Constraint to SenderInfo

Revision ID: 2ab0bbb8b49d
Revises: a72b2205b55c
Create Date: 2020-12-11 23:27:16.497547

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2ab0bbb8b49d'
down_revision = 'a72b2205b55c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sender_infos', sa.Column('address_type', sa.VARCHAR(), nullable=True))
    op.create_index('idx_sender_infos_address_address_origin_uc', 'sender_infos', ['address', 'address_origin'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('idx_sender_infos_address_address_origin_uc', table_name='sender_infos')
    op.drop_column('sender_infos', 'address_type')
    # ### end Alembic commands ###
