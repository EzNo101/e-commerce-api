from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.user import router as user_router
from app.api.cart import router as cart_router
from app.api.product import router as product_router
from app.api.category import router as category_router
from app.api.orders import router as orders_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(user_router)
router.include_router(cart_router)
router.include_router(product_router)
router.include_router(category_router)
router.include_router(orders_router)
