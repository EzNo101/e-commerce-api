from typing import Any
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product


class ProductRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all(self, limit: int, offset: int) -> list[Product]:
        result = await self.session.execute(
            select(Product)
            .order_by(Product.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        return list(result.scalars().all())

    async def get_by_id(self, product_id: int) -> Product | None:
        return await self.session.get(Product, product_id)

    async def get_by_name(self, product_name: str) -> Product | None:
        result = await self.session.execute(
            select(Product).where(Product.name == product_name)
        )
        return result.scalar_one_or_none()

    async def exists_by_name(self, product_name: str) -> bool:
        result = await self.session.execute(
            select(exists().where(Product.name == product_name))
        )
        return result.scalar_one()

    async def create_product(
        self,
        name: str,
        description: str | None,
        quantity: int,
        price: int,
        category_id: int,
    ) -> Product:
        product = Product(
            name=name,
            description=description,
            quantity=quantity,
            price=price,
            category_id=category_id,
        )
        self.session.add(product)
        await self.session.flush()
        return product

    async def update_product(
        self, product: Product, updates: dict[str, Any]
    ) -> Product:
        for field, value in updates.items():
            setattr(product, field, value)

        return product

    async def delete_product(self, product: Product) -> None:
        await self.session.delete(product)
