from datetime import datetime
from sqlalchemy.orm import Mapped, declarative_mixin, mapped_column
from sqlalchemy import func


@declarative_mixin
class CreatedAtMixin:
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


@declarative_mixin
class UpdatedAtMixin:
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
