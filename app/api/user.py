from fastapi import APIRouter, status, Depends, HTTPException

from app.core.dependencies import (
    get_uow,
    get_current_active_user,
)
from app.services.user import UserService
from app.db.uow import UnitOfWork
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate, ChangePasswordRequest
from app.core.errors import (
    InvalidPasswordError,
    EmailAlreadyUsedError,
    UsernameAlreadyUsedError,
)


router = APIRouter(prefix="/users", tags=["users"])
user_service = UserService()


@router.get("/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.patch("/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def update_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        updated_profile = await user_service.update_profile(current_user, data, uow)
    except EmailAlreadyUsedError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except UsernameAlreadyUsedError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return updated_profile


@router.patch(
    "/me/password", status_code=status.HTTP_200_OK, response_model=UserResponse
)
async def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        changed_password_user = await user_service.change_password(
            current_user, data, uow
        )
    except InvalidPasswordError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return changed_password_user
