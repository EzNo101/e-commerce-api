from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order, OrderItem, OrderStatus, PaymentStatus
from app.models.cart import Cart


class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, order_id: int) -> Order | None:
        result = await self.session.execute(
            select(Order).options(selectinload(Order.items)).where(Order.id == order_id)
        )

        return result.scalar_one_or_none()

    async def get_by_payment_intent_id(self, payment_intent_id: str) -> Order | None:
        result = await self.session.execute(
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.stripe_payment_intent_id == payment_intent_id)
        )

        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: int, limit: int, offset: int) -> list[Order]:
        result = await self.session.execute(
            select(Order)
            .where(Order.user_id == user_id)
            .options(selectinload(Order.items))
            .order_by(Order.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        return list(result.scalars().all())

    async def get_by_order_number(self, order_number: str) -> Order | None:
        result = await self.session.execute(
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.order_number == order_number)
        )
        return result.scalar_one_or_none()

    async def create_order_from_cart(
        self,
        cart: Cart,
        order_number: str,
        total_amount: int,
        order_status: OrderStatus = OrderStatus.PENDING,
        payment_status: PaymentStatus = PaymentStatus.PENDING,
    ) -> Order:
        order = Order(
            order_number=order_number,
            user_id=cart.user_id,
            total_amount=total_amount,
            order_status=order_status,
            payment_status=payment_status,
        )
        self.session.add(order)
        await self.session.flush()

        for cart_item in cart.items:
            item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price_at_time=cart_item.price_at_time,
            )
            self.session.add(item)

        return order

    async def create_order(
        self,
        order_number: str,
        user_id: int,
        total_amount: int,
        order_status: OrderStatus = OrderStatus.PENDING,
        payment_status: PaymentStatus = PaymentStatus.PENDING,
    ) -> Order:
        order = Order(
            order_number=order_number,
            user_id=user_id,
            total_amount=total_amount,
            order_status=order_status,
            payment_status=payment_status,
        )

        self.session.add(order)
        await self.session.flush()
        return order

    async def add_item(
        self, order_id: int, product_id: int, quantity: int, price_at_time: int
    ) -> OrderItem:
        item = OrderItem(
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            price_at_time=price_at_time,
        )

        self.session.add(item)
        return item

    async def set_payment_intent_id(
        self, order: Order, payment_intent_id: str
    ) -> Order:
        order.stripe_payment_intent_id = payment_intent_id
        return order

    async def change_statuses(
        self,
        order: Order,
        order_status: OrderStatus | None,
        payment_status: PaymentStatus | None,
    ) -> Order:
        if order_status is not None:
            order.order_status = order_status
        if payment_status is not None:
            order.payment_status = payment_status
        return order
