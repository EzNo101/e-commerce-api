from fastapi import APIRouter, HTTPException, Depends, status, Query, Request, Header
from typing import Any, cast

from stripe import SignatureVerificationError

from app.services.order import OrderService
from app.services.stripe import StripeService
from app.schemas.order import OrderResponse
from app.models.user import User
from app.core.dependencies import get_current_active_user, get_uow
from app.core.errors import (
    OrderCheckoutError,
    OrderEmptyCartError,
    OrderNotFoundError,
    OrderAccessDeniedError,
)
from app.db.uow import UnitOfWork


router = APIRouter(prefix="/orders", tags=["orders"])
order_service = OrderService()
stripe_service = StripeService()


@router.get("/my", response_model=list[OrderResponse], status_code=status.HTTP_200_OK)
async def list_orders_by_user(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    uow: UnitOfWork = Depends(get_uow),
):
    return await order_service.list_my_orders(current_user.id, limit, offset, uow)


@router.get("/{order_id}", response_model=OrderResponse, status_code=status.HTTP_200_OK)
async def get_by_id(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        return await order_service.get_by_id(current_user.id, order_id, uow)
    except OrderNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except OrderAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/checkout", response_model=OrderResponse, status_code=status.HTTP_201_CREATED
)
async def checkout_order(
    currency: str = Query(default="USD", min_length=3, max_length=3),
    current_user: User = Depends(get_current_active_user),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        return await order_service.checkout_from_cart(current_user.id, uow, currency)
    except OrderEmptyCartError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except OrderCheckoutError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post(
    "/webhook/stripe", response_model=dict[str, Any], status_code=status.HTTP_200_OK
)
async def stripe_webhook(
    request: Request,  # gives access to raw request body
    stripe_signature: str | None = Header(
        default=None,
        alias="Stripe-Signature",  # alias means search in HTTP headers for Stripe-Signature
    ),  # Takes the header that Stripe sends for authentication.
    uow: UnitOfWork = Depends(get_uow),
):
    if stripe_signature is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe-Signature header",
        )
    payload = (
        await request.body()
    )  # we need raw bytes because signature checked in raw bytes

    try:
        event = stripe_service.construct_webhook_event(
            payload, stripe_signature
        )  # checks signature using STRIPE_WEBHOOK_SECRET
    except (SignatureVerificationError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid webhook signature"
        )

    event_type = event["type"]
    if not isinstance(event_type, str):
        return {"received": True}
    allowed_events = {
        "payment_intent.succeeded",
        "payment_intent.payment_failed",
    }  # ignoring all others boring events
    if event_type not in allowed_events:
        return {"received": True}  # for stripe is important status codes not json

    data_object = cast(dict[str, Any], event["data"]["object"])

    payment_intent_id = data_object.get(
        "id"
    )  # take payment intent id because we need to find order by it
    if not isinstance(payment_intent_id, str):
        return {"received": True}

    await order_service.apply_payment_event(
        payment_intent_id=payment_intent_id,
        event_type=event_type,
        uow=uow,
    )
    return {"received": True}
