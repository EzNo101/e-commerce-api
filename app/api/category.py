from fastapi import APIRouter, status, Depends, HTTPException

from app.services.category import CategoryService
from app.models.user import User
from app.schemas.category import CategoryResponse, CategoryCreate, CategoryUpdate
from app.core.dependencies import (
    get_current_admin_user,
    get_uow,
)
from app.db.uow import UnitOfWork
from app.core.errors import (
    CategoryAlreadyExistsError,
    CategoryNotFoundError,
    CategoryCreateError,
)

router = APIRouter(prefix="/category", tags=["categories"])
category_service = CategoryService()


@router.get("/", response_model=list[CategoryResponse], status_code=status.HTTP_200_OK)
async def get_all(uow: UnitOfWork = Depends(get_uow)):
    return await category_service.get_all(uow)


@router.get(
    "/{category_id}", response_model=CategoryResponse, status_code=status.HTTP_200_OK
)
async def get_by_id(category_id: int, uow: UnitOfWork = Depends(get_uow)):
    try:
        result = await category_service.get_by_id(category_id, uow)
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return result


@router.get(
    "/by-name/{category_name}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
)
async def get_by_name(category_name: str, uow: UnitOfWork = Depends(get_uow)):
    try:
        result = await category_service.get_by_name(category_name, uow)
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return result


@router.post(
    "/create", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED
)
async def create(
    data: CategoryCreate,
    current_admin_user: User = Depends(get_current_admin_user),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        category = await category_service.create_category(data, uow)
    except CategoryAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except CategoryCreateError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

    return category


@router.patch(
    "/update/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    current_admin_user: User = Depends(get_current_admin_user),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        result = await category_service.update_category(category_id, data, uow)
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except CategoryAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return result


@router.delete("/delete/{category_id}", status_code=status.HTTP_200_OK)
async def delete_category(
    category_id: int,
    current_admin_user: User = Depends(get_current_admin_user),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        await category_service.delete_category(category_id, uow)
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
