from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.repositories.category import CategoryRepository
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.db.uow import UnitOfWork
from app.core.errors import (
    CategoryNotFoundError,
    CategoryAlreadyExistsError,
    CategoryCreateError,
)


class CategoryService:
    async def get_all(self, uow: UnitOfWork) -> list[Category]:
        repo = CategoryRepository(uow.session)

        return await repo.get_all()

    async def get_by_id(self, category_id: int, uow: UnitOfWork) -> Category:
        repo = CategoryRepository(uow.session)

        result = await repo.get_by_id(category_id)
        if result is None:
            raise CategoryNotFoundError("Category not found")

        return result

    async def get_by_name(self, category_name: str, uow: UnitOfWork) -> Category:
        repo = CategoryRepository(uow.session)

        result = await repo.get_by_name(category_name)
        if result is None:
            raise CategoryNotFoundError("Category not found")

        return result

    async def create_category(self, data: CategoryCreate, uow: UnitOfWork) -> Category:
        repo = CategoryRepository(uow.session)

        try:
            category = await repo.category_create(
                name=data.name, is_active=data.is_active
            )
            await uow.commit()
        except IntegrityError as e:
            await uow.rollback()
            raise CategoryAlreadyExistsError("Category already exists") from e
        except SQLAlchemyError as e:
            await uow.rollback()
            raise CategoryCreateError("Could not create category") from e

        return category

    async def update_category(
        self, category_id: int, data: CategoryUpdate, uow: UnitOfWork
    ) -> Category:
        repo = CategoryRepository(uow.session)

        category = await repo.get_by_id(category_id)
        if category is None:
            raise CategoryNotFoundError("Category not found")

        updates = data.model_dump(exclude_none=True, exclude_unset=True)
        if not updates:
            return category

        if "name" in updates and updates["name"] != category.name:
            existing = await repo.get_by_name(updates["name"])
            if existing is not None:
                raise CategoryAlreadyExistsError("Category already exists")
        try:
            updated_category = await repo.category_update(category, updates)
            await uow.commit()
        except IntegrityError as e:
            await uow.rollback()
            raise CategoryAlreadyExistsError("Category already exists") from e

        return updated_category

    async def delete_category(self, category_id: int, uow: UnitOfWork) -> None:
        repo = CategoryRepository(uow.session)

        category = await repo.get_by_id(category_id)
        if category is None:
            await uow.rollback()
            raise CategoryNotFoundError("Category not found")

        await repo.category_delete(category)
        await uow.commit()
