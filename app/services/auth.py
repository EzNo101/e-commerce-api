from app.db.uow import UnitOfWork
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserLogin
from app.schemas.auth import RefreshTokenResponse, TokenResponse, RefreshTokenRequest
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    decode_token,
    ensure_token_type,
)


class AuthService:
    def _build_token_response(self, user_id: int) -> TokenResponse:
        access_token = create_access_token(str(user_id))
        refresh_token = create_refresh_token(str(user_id))

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            refresh_expires_in=settings.REFRESH_TOKEN_EXPIRE_DAY * 24 * 60 * 60,
        )

    async def register(self, data: UserCreate, uow: UnitOfWork) -> TokenResponse:
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

        return self._build_token_response(user.id)

    async def login(self, data: UserLogin, uow: UnitOfWork) -> TokenResponse:
        repo = UserRepository(uow.session)
        user = await repo.get_by_email(data.email)
        if user is None:
            raise ValueError("Invalid email or password")
        verify = verify_password(data.password, user.hashed_password)
        if not verify:
            raise ValueError("Invalid email or password")
        if not user.is_active:
            raise ValueError("User is inactive")

        return self._build_token_response(user.id)

    # TODO: add rotation(whitelist method using redis)
    async def refresh(
        self, data: RefreshTokenRequest, uow: UnitOfWork
    ) -> RefreshTokenResponse:
        payload = decode_token(data.refresh_token)
        ensure_token_type(payload, "refresh")

        repo = UserRepository(uow.session)
        user = await repo.get_by_id(int(payload.sub))
        if user is None:
            raise ValueError("User not found")
        if not user.is_active:
            raise ValueError("User is inactive")

        access_token = create_access_token(subject=payload.sub)

        return RefreshTokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
