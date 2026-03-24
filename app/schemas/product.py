from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class ProductCreate(BaseModel):
    name: str = Field(min_length=3, max_length=125)
    description: str | None = Field(default=None, max_length=1500)
    price: int = Field(gt=0)
    quantity: int = Field(ge=0)
    category_id: int

    model_config = ConfigDict(extra="forbid")


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=125)
    description: str | None = Field(default=None, max_length=1500)
    price: int | None = Field(default=None, gt=0)
    quantity: int | None = Field(default=None, ge=0)
    category_id: int | None = Field(default=None)

    model_config = ConfigDict(extra="forbid")


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: int
    quantity: int
    category_id: int
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
