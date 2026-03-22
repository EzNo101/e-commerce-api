from datetime import datetime, timezone, timedelta
from uuid import uuid4  # for jti(JWT ID)

from jose import jwt, JWTError
from passlib.context import CryptContext  # password manager for hashing

from app.core.config import settings
from app.schemas.auth import TokenPayload


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def _create_token(
    subject: str,
    token_type: str,
    expires_delta: timedelta,
    jti: str | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    expire = now + expires_delta

    payload: dict[str, str | int] = {
        "sub": subject,
        "typ": token_type,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "jti": jti or str(uuid4()),
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(subject: str) -> str:
    return _create_token(
        subject=subject,
        token_type=ACCESS_TOKEN_TYPE,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(subject: str, jti: str | None = None) -> str:
    return _create_token(
        subject=subject,
        token_type=REFRESH_TOKEN_TYPE,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAY),
        jti=jti,
    )


def decode_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return TokenPayload(**payload)
    except JWTError as e:
        raise ValueError("Invalid or expired token") from e


# refresh cannot be access and access cannot be refresh
def ensure_token_type(payload: TokenPayload, expected_type: str) -> None:
    if payload.typ != expected_type:
        raise ValueError(f"Invalid token type: expected {expected_type}")
