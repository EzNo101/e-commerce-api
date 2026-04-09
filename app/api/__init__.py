from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.user import router as user_router
from app.api.cart import router as cart_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(user_router)
router.include_router(cart_router)
