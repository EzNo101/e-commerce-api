from fastapi import APIRouter, status, HTTPException, Depends
from datetime import datetime, timezone

from app.core.dependencies import get_current_active_user, get_uow
from app.db.uow import UnitOfWork
from app.services.cart import CartService
from app.models.user import User
from app.models.cart import Cart
from app.schemas.cart import CartItemResponse, CartResponse, CartItemAdd, CartItemUpdate
from app.core.errors import (
    ProductNotFoundError,
    ProductNotInCart,
    ProductQuantityError,
)

router = APIRouter(prefix="/cart", tags=["cart"])
cart_service = CartService()


def _to_cart_response(cart: Cart | None, user_id: int) -> CartResponse:
    if cart is None:
        return CartResponse(
            id=0,
            user_id=user_id,
            items=[],
            total=0,
            created_at=datetime.now(timezone.utc),
            updated_at=None,
        )
    items = [CartItemResponse.model_validate(i) for i in cart.items]
    total = sum(i.quantity * i.price_at_time for i in cart.items)
    return CartResponse(
        id=cart.id,
        user_id=cart.user_id,
        items=items,
        total=total,
        created_at=cart.created_at,
        updated_at=cart.updated_at,
    )


@router.get("", response_model=CartResponse, status_code=status.HTTP_200_OK)
async def get_my_cart(
    current_user: User = Depends(get_current_active_user),
    uow: UnitOfWork = Depends(get_uow),
):
    cart = await cart_service.get_cart(current_user.id, uow)
    return _to_cart_response(cart, current_user.id)


@router.post("/items", response_model=CartResponse, status_code=status.HTTP_200_OK)
async def add_item(
    data: CartItemAdd,
    current_user: User = Depends(get_current_active_user),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        cart = await cart_service.add_item(current_user.id, data, uow)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ProductQuantityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return _to_cart_response(cart, current_user.id)


@router.patch(
    "/items/{product_id}", response_model=CartResponse, status_code=status.HTTP_200_OK
)
async def update_item(
    product_id: int,
    data: CartItemUpdate,
    current_user: User = Depends(get_current_active_user),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        cart = await cart_service.update_item(current_user.id, product_id, data, uow)
    except (ProductNotFoundError, ProductNotInCart) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ProductQuantityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return _to_cart_response(cart, current_user.id)


@router.delete(
    "/items/{product_id}", response_model=CartResponse, status_code=status.HTTP_200_OK
)
async def delete_item(
    product_id: int,
    current_user: User = Depends(get_current_active_user),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        cart = await cart_service.delete_item(current_user.id, product_id, uow)
    except ProductNotInCart as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return _to_cart_response(cart, current_user.id)


@router.delete("/items", response_model=CartResponse, status_code=status.HTTP_200_OK)
async def clear_cart(
    current_user: User = Depends(get_current_active_user),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        cart = await cart_service.clear_cart(current_user.id, uow)
    except ProductNotInCart as e:
        raise HTTPException(status_code=status.HTTP_200_OK, detail=str(e))

    return _to_cart_response(cart, current_user.id)
