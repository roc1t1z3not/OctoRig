"""Add lab_template_id to challenges

Revision ID: add_challenge_lab_tmpl
Revises: db_init
Create Date: 2026-06-14
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "add_challenge_lab_tmpl"
down_revision: Union[str, None] = "db_init"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "challenges",
        sa.Column("lab_template_id", sa.Integer(), sa.ForeignKey("lab_templates.id"), nullable=True)
    )
    op.create_index("ix_challenges_lab_template_id", "challenges", ["lab_template_id"])


def downgrade() -> None:
    op.drop_index("ix_challenges_lab_template_id", "challenges")
    op.drop_column("challenges", "lab_template_id")
