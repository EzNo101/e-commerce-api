import redis.asyncio as redis
from uuid import uuid4
from datetime import timedelta

from app.db.uow import UnitOfWork
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserLogin
from app.schemas.auth import (
    RefreshTokenResponse,
    TokenResponse,
    RefreshTokenRequest,
)
from app.core.config import settings
from app.db.token_store import (
    delete_refresh_token,
    store_refresh_token,
    get_refresh_token_owner,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    decode_token,
    ensure_token_type,
)


class AuthService:
    def _get_access_token_ttl(self) -> int:
        return int(
            timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES).total_seconds()
        )

    def _get_refresh_token_ttl(self) -> int:
        return int(timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAY).total_seconds())

    async def _build_token_response(
        self, redis_client: redis.Redis, user_id: int
    ) -> TokenResponse:
        jti = str(uuid4())
        access_token = create_access_token(str(user_id))
        refresh_token = create_refresh_token(subject=str(user_id), jti=jti)

        await store_refresh_token(
            client=redis_client,
            jti=jti,
            user_id=user_id,
            expires_in=self._get_refresh_token_ttl(),
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=self._get_access_token_ttl(),
            refresh_expires_in=self._get_refresh_token_ttl(),
        )

    async def register(
        self, data: UserCreate, redis_client: redis.Redis, uow: UnitOfWork
    ) -> TokenResponse:
        repo = UserRepository(uow.session)
        exists = await repo.exists_by_email_or_username(data.email, data.username)
        if exists:
            raise ValueError("Username or Email already exists")
        hashed_password = get_password_hash(data.password)
        user = await repo.create_user(
            username=data.username,
            email=data.email,
            hashed_password=hashed_password,
            is_active=True,
            is_admin=False,
        )
        await uow.commit()
        await uow.refresh(user)
        return await self._build_token_response(redis_client, user.id)

    async def login(
        self, data: UserLogin, redis_client: redis.Redis, uow: UnitOfWork
    ) -> TokenResponse:
        repo = UserRepository(uow.session)
        user = await repo.get_by_email(data.email)
        if user is None:
            raise ValueError("Invalid email or password")
        verify = verify_password(data.password, user.hashed_password)
        if not verify:
            raise ValueError("Invalid email or password")
        if not user.is_active:
            raise ValueError("User is inactive")

        return await self._build_token_response(redis_client, user.id)

    async def refresh(
        self, data: RefreshTokenRequest, redis_client: redis.Redis, uow: UnitOfWork
    ) -> RefreshTokenResponse:
        payload = decode_token(data.refresh_token)
        ensure_token_type(payload, "refresh")

        if payload.jti is None:
            raise ValueError("Refresh token missing jti")

        stored_user_id = await get_refresh_token_owner(redis_client, payload.jti)
        if stored_user_id is None:
            raise ValueError("Refresh token is invalid or already used")
        if stored_user_id != payload.sub:
            raise ValueError("Token mismatch")
        repo = UserRepository(uow.session)
        user = await repo.get_by_id(int(payload.sub))
        if user is None:
            raise ValueError("User not found")
        if not user.is_active:
            raise ValueError("User is inactive")

        await delete_refresh_token(redis_client, payload.jti)
        new_jti = str(uuid4())
        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id), jti=new_jti)

        await store_refresh_token(
            client=redis_client,
            jti=new_jti,
            user_id=user.id,
            expires_in=self._get_refresh_token_ttl(),
        )

        return RefreshTokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=self._get_access_token_ttl(),
            refresh_token=refresh_token,
            refresh_expires_in=self._get_refresh_token_ttl(),
        )

    async def logout(
        self, data: RefreshTokenRequest, redis_client: redis.Redis
    ) -> None:
        payload = decode_token(data.refresh_token)
        ensure_token_type(payload, "refresh")

        if payload.jti is None:
            raise ValueError("Refresh token missing jti")

        await delete_refresh_token(redis_client, payload.jti)
