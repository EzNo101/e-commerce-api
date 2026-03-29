from fastapi import Response
from datetime import timedelta

from app.core.config import settings


# response = object of http response
def set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    response.set_cookie(  # add cookie to this response
        key="access_token",
        value=access_token,
        httponly=True,  # javascript in browser can't read that cookie (protection against XSS)
        secure=True,  # cookie only works with https
        samesite="lax",  # browser can't sent cookie to other sites (protection against CSRF)
        max_age=int(
            timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES).total_seconds()
        ),
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=int(timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAY).total_seconds()),
    )


def clear_auth_cookies(response: Response):
    response.delete_cookie("acess_token")
    response.delete_cookie("refresh_token")
