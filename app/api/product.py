from fastapi import APIRouter, HTTPException, status, Depends, Query
from redis.asyncio import Redis
from app.services.product import ProductService
from app.core.dependencies import (
    get_current_admin_user,
    get_uow,
)
from app.db.uow import UnitOfWork
from app.db.redis import get_redis
from app.core.cache import CacheService
from app.schemas.product import ProductResponse, ProductUpdate, ProductCreate
from app.models.user import User
from app.core.errors import (
    ProductNotFoundError,
    ProductAlreadyExistsError,
    ProductCreateError,
)

router = APIRouter(prefix="/products", tags=["products"])
product_service = ProductService()


def _product_item_key(product_id: int) -> str:
    return f"products:item:{product_id}"


def _product_name_key(product_name: str) -> str:
    normalize = product_name.lower().strip()
    return f"products:name:{normalize}"


def _products_list_key(limit: int, offset: int) -> str:
    return f"products:list:{limit}:{offset}"


async def _invalidate_product_cache(
    cache: CacheService, product_id: int | None
) -> None:
    if product_id is not None:
        await cache.delete(_product_item_key(product_id))
    await cache.delete_pattern("products:list:*")
    await cache.delete_pattern("products:name:*")


@router.get("/", response_model=list[ProductResponse], status_code=status.HTTP_200_OK)
async def get_all(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    uow: UnitOfWork = Depends(get_uow),
    redis_client: Redis = Depends(get_redis),
):
    cache = CacheService(redis_client)
    key = _products_list_key(limit, offset)

    cached = await cache.get(key)
    if cached is not None:
        return cached

    result = await product_service.get_all(limit, offset, uow)
    payload = [
        ProductResponse.model_validate(item).model_dump(mode="json") for item in result
    ]
    await cache.set(key, payload)
    return payload


@router.get(
    "/id/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK
)
async def get_by_id(
    product_id: int,
    uow: UnitOfWork = Depends(get_uow),
    redis_client: Redis = Depends(get_redis),
):
    cache = CacheService(redis_client)
    key = _product_item_key(product_id)

    cached = await cache.get(key)
    if cached is not None:
        return cached

    try:
        result = await product_service.get_by_id(product_id, uow)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    payload = ProductResponse.model_validate(result).model_dump(mode="json")
    await cache.set(key, payload)

    return payload


@router.get(
    "/name/{product_name}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
)
async def get_by_name(
    product_name: str,
    uow: UnitOfWork = Depends(get_uow),
    redis_client: Redis = Depends(get_redis),
):
    cache = CacheService(redis_client)
    key = _product_name_key(product_name)

    cached = await cache.get(key)
    if cached is not None:
        return cached

    try:
        result = await product_service.get_by_name(product_name, uow)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    payload = ProductResponse.model_validate(result).model_dump(mode="json")
    await cache.set(key, payload)

    return payload


@router.post(
    "/create", response_model=ProductResponse, status_code=status.HTTP_201_CREATED
)
async def create_product(
    data: ProductCreate,
    admin: User = Depends(get_current_admin_user),
    uow: UnitOfWork = Depends(get_uow),
    redis_client: Redis = Depends(get_redis),
):
    cache = CacheService(redis_client)
    try:
        result = await product_service.create_product(data, uow)
    except ProductAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ProductCreateError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

    await _invalidate_product_cache(cache, result.id)
    return result


@router.patch(
    "/update/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    admin: User = Depends(get_current_admin_user),
    uow: UnitOfWork = Depends(get_uow),
    redis_client: Redis = Depends(get_redis),
):
    cache = CacheService(redis_client)

    try:
        result = await product_service.update_product(product_id, data, uow)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    await _invalidate_product_cache(cache, result.id)
    return result


@router.delete("/delete/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(
    product_id: int,
    admin: User = Depends(get_current_admin_user),
    uow: UnitOfWork = Depends(get_uow),
    redis_client: Redis = Depends(get_redis),
):
    cache = CacheService(redis_client)
    try:
        await product_service.delete_product(product_id, uow)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    await _invalidate_product_cache(cache, product_id)
