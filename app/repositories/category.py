from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists

from app.models.category import Category


class CategoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[Category]:
        result = await self.session.execute(select(Category).order_by(Category.name))

        return list(result.scalars().all())

    async def get_by_id(self, category_id: int) -> Category | None:
        return await self.session.get(Category, category_id)

    async def get_by_name(self, category_name: str) -> Category | None:
        result = await self.session.execute(
            select(Category).where(Category.name == category_name)
        )
        return result.scalar_one_or_none()

    async def exists_by_name(self, category_name: str) -> bool:
        result = await self.session.execute(
            select(exists().where(Category.name == category_name))
        )
        return result.scalar_one()

    async def category_create(self, name: str, is_active: bool) -> Category:
        category = Category(name=name, is_active=is_active)
        self.session.add(category)
        await self.session.flush()
        return category

    async def category_update(
        self, category: Category, updates: dict[str, Any]
    ) -> Category:
        for field, value in updates.items():
            setattr(category, field, value)

        return category

    async def category_delete(self, category: Category) -> None:
        await self.session.delete(category)
