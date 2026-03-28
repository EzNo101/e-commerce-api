from pydantic import BaseModel, ConfigDict
from typing import Literal


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int  # seconds
    refresh_expires_in: int

    model_config = ConfigDict(extra="forbid")


class TokenPayload(BaseModel):
    sub: str  # user id or user email (better user id)
    exp: int  # unix timestamp,  when token expire
    iat: int  # time when token created (for diagnostic etc.)
    jti: str | None = (
        None  # unique id for token (revoke/blacklist in Redis, logout all sessions)
    )
    typ: Literal["access", "refresh"]

    model_config = ConfigDict(extra="forbid")


class RefreshTokenRequest(BaseModel):
    refresh_token: str

    model_config = ConfigDict(extra="forbid")


class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int  # access ttl in seconds
    refresh_token: str | None = None  # if rotation
    refresh_expires_in: int | None = None  # if new refresh
