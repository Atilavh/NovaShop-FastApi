import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Boolean, Enum, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.utils.time_stamp_for_model import TimestampMixin
from app.db.base import Base
from app.auth.model.models import OTP, RefreshToken
from app.products.models.model import Product


class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    SELLER = "seller"
    ADMIN = "admin"

class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column(String(30), nullable=True)
    last_name: Mapped[str] = mapped_column(String(30), nullable=True)
    phone_number: Mapped[str] = mapped_column(nullable=False, unique=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.CUSTOMER, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    otps = relationship(OTP, back_populates="user")
    refresh_tokens = relationship(RefreshToken, back_populates="user", cascade="all, delete-orphan")
    products = relationship(Product, back_populates="seller", cascade="all, delete-orphan")