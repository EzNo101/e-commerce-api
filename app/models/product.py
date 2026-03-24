from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import CreatedAtMixin, UpdatedAtMixin


class Product(Base, CreatedAtMixin, UpdatedAtMixin):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(125), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1500), nullable=True)
    quantity: Mapped[int] = mapped_column(default=0, nullable=False)
    price: Mapped[int] = mapped_column(nullable=False)

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), nullable=False
    )
    category = relationship("Category", back_populates="products")
