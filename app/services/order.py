from stripe._error import StripeError
from uuid import uuid4
from sqlalchemy.exc import SQLAlchemyError
from typing import Any

from app.repositories.order import OrderRepository
from app.repositories.cart import CartRepository
from app.services.stripe import StripeService
from app.models.order import Order, OrderStatus, PaymentStatus
from app.models.cart import Cart
from app.db.uow import UnitOfWork
from app.core.errors import (
    OrderAccessDeniedError,
    OrderCheckoutError,
    OrderEmptyCartError,
    OrderNotFoundError,
)


class OrderService:
    def _generate_order_number(self) -> str:
        return f"ORD-{uuid4().hex[:12].upper()}"  # hex -> in hexadecimal type (0-9 and a-f) | [:12] only first 12 (make it shorter)

    def _calculate_total(self, cart: Cart) -> int:
        return sum(item.quantity * item.price_at_time for item in cart.items)

    async def checkout_from_cart(
        self,
        user_id: int,
        uow: UnitOfWork,
        currency: str = "USD",
    ) -> dict[str, Any]:
        cart_repo = CartRepository(uow.session)
        order_repo = OrderRepository(uow.session)
        stripe_service = StripeService()

        cart = await cart_repo.get_by_user_id(user_id)
        if cart is None or not cart.items:
            raise OrderEmptyCartError("Cart is empty")

        total_amount = self._calculate_total(cart)
        order_number = self._generate_order_number()

        try:
            order = await order_repo.create_order_from_cart(
                cart=cart,
                order_number=order_number,
                total_amount=total_amount,
                currency=currency,
            )
            intent = stripe_service.create_payment_intent(
                amount=total_amount,
                currency=currency.lower(),  # Stripe waits for lower register ISO code
                order_id=order.id,
                idempotency_key=f"checkout-{order_number}",
            )
            await order_repo.set_payment_intent_id(order, intent.id)
            await cart_repo.clear_cart(cart)
            await uow.commit()

            hydrated_order = await order_repo.get_by_id(order.id)
            if hydrated_order is None:
                raise OrderCheckoutError("Order created but could not be loaded")

            client_secret = intent.client_secret
            if not isinstance(client_secret, str):
                raise OrderCheckoutError("PaymentIntent has no client_secret")

            return {"order": hydrated_order, "client_secret": client_secret}

        except (SQLAlchemyError, StripeError) as e:
            await uow.rollback()
            raise OrderCheckoutError("Could not checkout") from e

    async def get_by_id(self, user_id: int, order_id: int, uow: UnitOfWork) -> Order:
        order_repo = OrderRepository(uow.session)
        order = await order_repo.get_by_id(order_id)
        if order is None:
            raise OrderNotFoundError("Order not found")

        if user_id != order.user_id:
            raise OrderAccessDeniedError("Access denied")

        return order

    async def list_my_orders(
        self, user_id: int, limit: int, offset: int, uow: UnitOfWork
    ) -> list[Order]:
        order_repo = OrderRepository(uow.session)
        return await order_repo.list_by_user(user_id, limit, offset)

    async def apply_payment_event(
        self, payment_intent_id: str, event_type: str, uow: UnitOfWork
    ) -> None:
        repo = OrderRepository(uow.session)
        order = await repo.get_by_payment_intent_id(payment_intent_id)
        if order is None:
            return

        if event_type == "payment_intent.succeeded":
            if order.payment_status == PaymentStatus.PAID:
                return
            await repo.change_statuses(
                order=order,
                order_status=OrderStatus.PROCESSING,
                payment_status=PaymentStatus.PAID,
            )
        elif event_type == "payment_intent.payment_failed":
            if order.payment_status == PaymentStatus.PAID:
                return
            await repo.change_statuses(
                order=order, order_status=None, payment_status=PaymentStatus.FAILED
            )
        else:
            return

        await uow.commit()
