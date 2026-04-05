from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.uow import UnitOfWork
from app.models.user import User
from app.core.security import decode_token, ensure_token_type
from app.services.user import UserService
from app.core.errors import InvalidTokenTypeError, InvalidTokenError, UserNotFoundError


async def get_uow(session: AsyncSession = Depends(get_db)) -> UnitOfWork:
    return UnitOfWork(session)


async def get_current_user(
    access_token: str | None = Cookie(default=None), uow: UnitOfWork = Depends(get_uow)
) -> User:
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    try:
        payload = decode_token(access_token)
        ensure_token_type(payload, "access")

        if not payload.sub.isdigit():
            raise InvalidTokenError("Invalid token subject")

        user_id = int(payload.sub)
    except InvalidTokenTypeError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
        ) from e
    except InvalidTokenError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    user_service = UserService()

    try:
        user = await user_service.get_by_id(user_id, uow)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
        ) from e

    return user


async def get_current_active_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    return user


async def get_current_admin_user(user: User = Depends(get_current_active_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    return user
