from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    is_active: bool = Field(default=True)

    model_config = ConfigDict(extra="forbid")


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=50)
    is_active: bool | None = Field(default=None)

    model_config = ConfigDict(extra="forbid")


class CategoryResponse(BaseModel):
    id: int
    name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
