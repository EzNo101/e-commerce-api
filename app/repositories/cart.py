from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.cart import Cart, CartItem


class CartRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_id(self, user_id: int) -> Cart | None:
        result = await self.session.execute(
            select(Cart)
            .options(selectinload(Cart.items))
            .where(Cart.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_for_user(self, user_id: int) -> Cart:
        cart = Cart(user_id=user_id)
        self.session.add(cart)
        await self.session.flush()
        return cart

    async def get_item(self, cart_id: int, product_id: int) -> CartItem | None:
        result = await self.session.execute(
            select(CartItem).where(
                CartItem.cart_id == cart_id,
                CartItem.product_id == product_id,
            )
        )

        return result.scalar_one_or_none()

    async def add_item(
        self,
        cart_id: int,
        product_id: int,
        quantity: int,
        price_at_time: int,
    ) -> CartItem:
        item = CartItem(
            cart_id=cart_id,
            product_id=product_id,
            quantity=quantity,
            price_at_time=price_at_time,
        )
        self.session.add(item)
        await self.session.flush()
        return item

    async def update_item_quantity(self, item: CartItem, quantity: int) -> CartItem:
        item.quantity = quantity
        return item

    async def remove_item(self, item: CartItem) -> None:
        await self.session.delete(item)

    async def clear_cart(self, cart: Cart) -> None:
        for item in list(cart.items):
            await self.session.delete(item)

    async def refresh_cart(self, cart: Cart) -> None:
        await self.session.refresh(cart, attribute_names=["items"])
