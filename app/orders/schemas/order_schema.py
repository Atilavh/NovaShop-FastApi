import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_serializer
from app.orders.models.model import OrderStatus, PaymentStatus


class OrderItemResponse(BaseModel):
    product_id: uuid.UUID
    title: str
    price: int
    quantity: int
    total_price: int

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("price", "total_price")
    @classmethod
    def format_price(cls, value: int):
        return f"{value:,}"


class OrderResponse(BaseModel):
    id: uuid.UUID
    status: OrderStatus
    payment_status: PaymentStatus
    subtotal_price: int
    shipping_price: int
    discount_price: int
    final_price: int
    created_at: datetime
    items: list[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)

    @field_serializer(
        "subtotal_price",
        "shipping_price",
        "discount_price",
        "final_price",
    )
    @classmethod
    def format_price(cls, value: int):
        return f"{value:,}"


class CreateOrderResponse(BaseModel):
    message: str
    order: OrderResponse


class OrderListResponse(BaseModel):
    orders: list[OrderResponse]
    total: int