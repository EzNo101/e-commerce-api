from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import CreatedAtMixin, UpdatedAtMixin


class Category(Base, CreatedAtMixin, UpdatedAtMixin):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(default=True)

    # Products -> name of the class which I will create in ORM | category is attribute which I will have in Product
    products = relationship("Product", back_populates="category")
