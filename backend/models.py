
from datetime import datetime

from sqlalchemy import CheckConstraint, Column, DateTime, Integer, Text

from backend.database import Base


class Post(Base):
    __tablename__ = "posts"

    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'flagged', 'approved', 'published')",
            name="check_post_status",
        ),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    title = Column(Text, nullable=False)

    content = Column(Text, nullable=False)

    status = Column(
        Text,
        nullable=False,
        default="draft",
        server_default="draft",
    )

    flagged_reasons = Column(Text, nullable=True)

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
