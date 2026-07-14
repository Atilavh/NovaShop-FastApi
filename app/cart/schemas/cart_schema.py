import uuid
from pydantic import BaseModel, Field, field_serializer


class AddToCartSchema(BaseModel):
    product_id: uuid.UUID
    quantity: int = 1


class CartItemResponse(BaseModel):
    product_id: uuid.UUID
    title: str
    price: int
    quantity: int
    stock: int
    total_price: int

    @field_serializer("price", "total_price")
    @classmethod
    def format_price(cls, value: int):
        return f"{value:,}"

class GetCartSchema(BaseModel):
    products: list[CartItemResponse]
    total_price: int

    @field_serializer("total_price")
    @classmethod
    def format_total_price(cls, value: int):
        return f"{value:,}"

class UpdateCartItemSchema(BaseModel):
    quantity: int = Field(gt=0)