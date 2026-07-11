import uuid
from pydantic import BaseModel, field_validator, field_serializer
from fastapi import Body
from app.products.models.model import ProductStatus


class AdminCreateProductSchema(BaseModel):
    title: str = Body(..., description="Title of products", title="Title")
    slug: str = Body(..., description="Slug of products", title="Slug")
    description: str = Body(..., description="Description of products", title="Description")
    price: int = Body(..., description="Price of products", title="Price")
    stock: int = Body(..., description="Stock of products", title="Stock")
    status: ProductStatus = Body(..., description="Status of products", title="Status")

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: int):
        if v <= 0:
            raise ValueError("price invalid!")
        return v
        
    @field_validator("stock")
    @classmethod
    def validate_stock(cls, v: int):
        if v < 0:
            raise ValueError("stock invalid!")
        return v
    

class AdminUpdateProductSchema(AdminCreateProductSchema):
    id: uuid.UUID = Body(..., description="ID of products", title="ID")


class ProductResponse(BaseModel):
    id: uuid.UUID
    title: str
    slug: str
    description: str | None
    price: int
    stock: int

    model_config = {
        "from_attributes": True
    }
    @field_serializer("price")
    @classmethod
    def price_combine(cls, v:int):
        return f"{v:,}"