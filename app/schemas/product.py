from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal


class ProductCreate(BaseModel):
    name: str = Field(min_length=3, max_length=125)
    description: str | None = Field(default=None, max_length=1500)
    price: Decimal = Field(gt=0)
    quantity: int = Field(ge=0)
    category_id: int

class ProductUpdate(BaseModel):
    name: str | None = Field(min_length=3, max_length=125)
    description: str | None = Field(default=None, max_length=1500)
    price: Decimal | None = Field(default=None, gt=0)
    quantity: int | None = Field(default=None, ge=0)
    category_id: int | None = Field(default=None)

class ProductResponse(BaseModel):
    name: str
    description: str | None
    price: Decimal
    quantity: int
    category_id: int

    model_config = ConfigDict(from_attributes=True)