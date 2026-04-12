from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.repositories.product import ProductRepository
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.db.uow import UnitOfWork
from app.core.errors import (
    ProductCreateError,
    ProductNotFoundError,
    ProductAlreadyExistsError,
)


class ProductService:
    async def get_all(self, limit: int, offset: int, uow: UnitOfWork) -> list[Product]:
        repo = ProductRepository(uow.session)
        result = await repo.get_all(limit, offset)
        return result

    async def get_by_id(self, product_id: int, uow: UnitOfWork) -> Product:
        repo = ProductRepository(uow.session)

        result = await repo.get_by_id(product_id)
        if result is None:
            raise ProductNotFoundError("Product not found")

        return result

    async def get_by_name(self, product_name: str, uow: UnitOfWork) -> Product:
        repo = ProductRepository(uow.session)

        result = await repo.get_by_name(product_name)
        if result is None:
            raise ProductNotFoundError("Product not found")

        return result

    async def create_product(self, data: ProductCreate, uow: UnitOfWork) -> Product:
        repo = ProductRepository(uow.session)
        try:
            product = await repo.create_product(
                name=data.name,
                description=data.description,
                quantity=data.quantity,
                price=data.price,
                category_id=data.category_id,
            )
            await uow.commit()
            await uow.refresh(product)
        except IntegrityError as e:
            await (
                uow.rollback()
            )  # better do it manually because sometimes cannot works automatically
            raise ProductAlreadyExistsError(
                "Product with this name already exists"
            ) from e
        except SQLAlchemyError as e:
            await uow.rollback()
            raise ProductCreateError("Could not create product") from e
        return product

    async def update_product(
        self, product_id: int, data: ProductUpdate, uow: UnitOfWork
    ) -> Product:
        repo = ProductRepository(uow.session)

        product = await repo.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError("Product not found")

        updates = data.model_dump(exclude_none=True, exclude_unset=True)
        if not updates:
            return product

        if "name" in updates and updates["name"] != product.name:
            existing_product = await repo.get_by_name(updates["name"])
            if existing_product:
                raise ProductAlreadyExistsError("Product name already exists")

        updated_product = await repo.update_product(product, updates)
        await uow.commit()
        await uow.refresh(product)

        return updated_product

    async def delete_product(self, product_id: int, uow: UnitOfWork) -> None:
        repo = ProductRepository(uow.session)

        product = await repo.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError("Product not found")

        await repo.delete_product(product)
        await uow.commit()
