import uuid
import enum
from app.db.base import Base
from app.products.models.model import Product
from datetime import datetime, timedelta, timezone
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String, ForeignKey, func, DateTime, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.users.model.models import User
    from app.orders.models.model import OrderItem

class OrderStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class PaymentStatus(enum.Enum):
    UNPAID = "unpaid"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus),
        default=OrderStatus.PENDING,
    )

    payment_status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus),
        default=PaymentStatus.UNPAID,
    )

    subtotal_price: Mapped[int] = mapped_column(nullable=False)

    shipping_price: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    discount_price: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    final_price: Mapped[int] = mapped_column(nullable=False)

    user: Mapped["User"] = relationship(
        back_populates="orders"
    )

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
    )

    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(nullable=False)

    price: Mapped[int] = mapped_column(nullable=False)

    quantity: Mapped[int] = mapped_column(nullable=False)

    total_price: Mapped[int] = mapped_column(nullable=False)

    order: Mapped["Order"] = relationship(
        back_populates="items"
    )

    product: Mapped[Product] = relationship()