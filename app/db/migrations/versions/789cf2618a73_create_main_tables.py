"""create_main_tables
Revision ID: 789cf2618a73
Revises: 
Create Date: 2021-12-07 19:47:34.476665
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision = '789cf2618a73'
down_revision = None
branch_labels = None
depends_on = None


def create_cleanings_table() -> None:
    op.create_table(
        "cleanings",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, index=True),
        sa.Column("description", sa.String(1000), nullable=True),
        sa.Column("cleaning_type", sa.String(255), nullable=False, server_default="spot_clean"),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
    )

def upgrade() -> None:
    create_cleanings_table()

def downgrade() -> None:
    op.drop_table("cleanings")