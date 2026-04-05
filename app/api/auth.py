from fastapi import APIRouter, Depends, HTTPException, Response, Cookie, status
import redis.asyncio as redis

from app.db.redis import get_redis
from app.core.dependencies import get_uow
from app.db.uow import UnitOfWork
from app.services.auth import AuthService
from app.schemas.auth import RefreshTokenRequest
from app.schemas.user import UserCreate, UserLogin
from app.utils.cookies import set_auth_cookies, clear_auth_cookies
from app.core.errors import (
    InvalidTokenError,
    InvalidTokenTypeError,
    InvalidPasswordError,
    EmailAlreadyUsedError,
    UserIsNotActiveError,
    UserNotFoundError,
)

router = APIRouter(prefix="/auth", tags=["auth"])
auth_service = AuthService()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    response: Response,
    data: UserCreate,
    uow: UnitOfWork = Depends(get_uow),
    redis_client: redis.Redis = Depends(get_redis),
):
    try:
        tokens = await auth_service.register(data, redis_client, uow)
    except EmailAlreadyUsedError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    set_auth_cookies(
        response=response,
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
    )

    return {"message": "Registered successfully"}


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    response: Response,
    data: UserLogin,
    redis_client: redis.Redis = Depends(get_redis),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        tokens = await auth_service.login(data, redis_client, uow)
    except InvalidPasswordError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except UserIsNotActiveError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    set_auth_cookies(
        response=response,
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
    )

    return {"message": "Logged in successfully"}


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    redis_client: redis.Redis = Depends(get_redis),
    uow: UnitOfWork = Depends(get_uow),
):
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not found"
        )
    try:
        tokens = await auth_service.refresh(
            RefreshTokenRequest(refresh_token=refresh_token), redis_client, uow
        )
    except (InvalidTokenError, UserNotFoundError, InvalidTokenTypeError) as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except UserIsNotActiveError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    if tokens.refresh_token is None or tokens.refresh_expires_in is None:
        clear_auth_cookies(response)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Refresh rotation failed",
        )

    set_auth_cookies(
        response=response,
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
    )

    return {"message": "Tokens refreshed"}


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    redis_client: redis.Redis = Depends(get_redis),
):
    try:
        if refresh_token is not None:
            await auth_service.logout(
                RefreshTokenRequest(refresh_token=refresh_token), redis_client
            )
    except (InvalidTokenError, InvalidTokenTypeError) as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    finally:
        clear_auth_cookies(response)

    return {"message": "Logged out successfully"}
