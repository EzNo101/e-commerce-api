from app.db.uow import UnitOfWork
from app.repositories.cart import CartRepository
from app.repositories.product import ProductRepository
from app.models.cart import Cart
from app.schemas.cart import CartItemAdd, CartItemUpdate
from app.core.errors import ProductNotFoundError, ProductNotInCart, ProductQuantityError


class CartService:
    async def _get_or_create_cart(self, user_id: int, uow: UnitOfWork) -> Cart:
        repo = CartRepository(uow.session)
        cart = await repo.get_by_user_id(user_id)
        if cart is None:
            cart = await repo.create_for_user(user_id)
        return cart

    async def get_cart(self, user_id: int, uow: UnitOfWork) -> Cart | None:
        cart_repo = CartRepository(uow.session)
        cart = await cart_repo.get_by_user_id(user_id)

        return cart

    async def add_item(self, user_id: int, data: CartItemAdd, uow: UnitOfWork) -> Cart:
        cart_repo = CartRepository(uow.session)
        product_repo = ProductRepository(uow.session)

        product = await product_repo.get_by_id(data.product_id)
        if product is None:
            raise ProductNotFoundError("Product not found")
        if data.quantity > product.quantity:
            raise ProductQuantityError("Insufficient stock")

        cart = await self._get_or_create_cart(user_id, uow)
        existing_item = await cart_repo.get_item(cart.id, product.id)

        if existing_item is not None:
            new_quantity = existing_item.quantity + data.quantity
            if new_quantity > product.quantity:
                raise ProductQuantityError("Insufficient stock")
            await cart_repo.update_item_quantity(existing_item, new_quantity)
        else:
            await cart_repo.add_item(
                cart_id=cart.id,
                product_id=data.product_id,
                quantity=data.quantity,
                price_at_time=product.price,
            )

        await uow.commit()

        updated_cart = await cart_repo.get_by_user_id(user_id)
        return updated_cart

    async def update_item(
        self, user_id: int, product_id: int, data: CartItemUpdate, uow: UnitOfWork
    ) -> Cart:
        cart_repo = CartRepository(uow.session)
        product_repo = ProductRepository(uow.session)

        product = await product_repo.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError("Product not found")
        if data.quantity > product.quantity:
            raise ProductQuantityError("Insufficient stock")

        cart = await self._get_or_create_cart(user_id, uow)
        existing_item = await cart_repo.get_item(cart.id, product_id)

        if existing_item is None:
            raise ProductNotInCart("Product not in cart")

        await cart_repo.update_item_quantity(existing_item, data.quantity)
        await uow.commit()

        updated_cart = await cart_repo.get_by_user_id(
            user_id
        )  # do not use uow.refresh(cart) because sometimes cannot load items
        return updated_cart

    async def delete_item(self, user_id: int, product_id: int, uow: UnitOfWork) -> Cart:
        cart_repo = CartRepository(uow.session)
        cart = await cart_repo.get_by_user_id(user_id)
        if cart is None:
            raise ProductNotInCart("Product not in cart")

        item = await cart_repo.get_item(cart.id, product_id)
        if item is None:
            raise ProductNotInCart("Product not in cart")

        await cart_repo.remove_item(item)
        await uow.commit()

        updated_cart = await cart_repo.get_by_user_id(user_id)
        return updated_cart

    async def clear_cart(self, user_id: int, uow: UnitOfWork) -> Cart:
        cart_repo = CartRepository(uow.session)

        cart = await cart_repo.get_by_user_id(user_id)
        if cart is None:
            raise ProductNotInCart("Cart already empty")

        await cart_repo.clear_cart(cart)
        await uow.commit()

        updated_cart = await cart_repo.get_by_user_id(user_id)
        return updated_cart
