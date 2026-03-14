from sqlalchemy import String, ForeignKey, func, Numeric
from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.db.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(125), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1500), nullable=True)
    quantity: Mapped[int] = mapped_column(default=0, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10,2))       # Decimal used for precise numbers
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(onupdate=func.now())

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False) 
    category = relationship("Category", back_populates="products")