from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from typing import List

from app.db.base import Base
from app.models.mixins import CreatedAtMixin, UpdatedAtMixin


class CartItem(Base, CreatedAtMixin):
    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(default=1, nullable=False)
    price_at_time: Mapped[int] = mapped_column(nullable=False)

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")


class Cart(Base, CreatedAtMixin, UpdatedAtMixin):
    __tablename__ = "carts"

    id: Mapped[int] = mapped_column(primary_key=True)
    items: Mapped[List[CartItem]] = relationship(
        "CartItem", back_populates="cart", cascade="all, delete-orphan"
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, unique=True
    )

    user = relationship("User", back_populates="cart")
