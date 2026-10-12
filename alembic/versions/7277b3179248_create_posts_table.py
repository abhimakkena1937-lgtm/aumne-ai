"""Create posts table.

Revision ID: 7277b3179248
Revises:
Create Date: 2026-10-12
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Alembic revision identifiers
revision: str = "7277b3179248"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the posts table."""

    op.create_table(
        "posts",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "title",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "content",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Text(),
            server_default="draft",
            nullable=False,
        ),
        sa.Column(
            "flagged_reasons",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('draft', 'flagged', 'approved', 'published')",
            name="check_post_status",
        ),
    )

    op.create_index(
        "ix_posts_id",
        "posts",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove the posts table."""

    op.drop_index("ix_posts_id", table_name="posts")
    op.drop_table("posts")