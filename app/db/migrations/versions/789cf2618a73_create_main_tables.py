"""create_main_tables
Revision ID: 789cf2618a73
Revises: 
Create Date: 2021-12-07 19:47:34.476665
"""
from typing import Tuple
from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic
revision = '789cf2618a73'
down_revision = None
branch_labels = None
depends_on = None



def timestamps(indexed: bool = False) -> Tuple[sa.Column, sa.Column]:
    return (
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            index=indexed,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            index=indexed,
        ),
    )


def create_cleanings_table() -> None:
    op.create_table(
        "cleanings",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, index=True),
        sa.Column("description", sa.String(1000), nullable=True),
        sa.Column("cleaning_type", sa.String(255), nullable=False, server_default="spot_clean"),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        *timestamps()
    )


def create_users_table() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.String(50), unique=True, nullable=False, index=True),        
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("email_verified", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("salt", sa.String(255), nullable=False),
        sa.Column("password", sa.Text, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default=sa.true()),     
        *timestamps(),
    )


def upgrade() -> None:
    create_cleanings_table()
    create_users_table()

def downgrade() -> None:
    op.drop_table("cleanings")
    op.drop_table("users")