import uuid
import enum
from app.db.base import Base
from datetime import datetime, timedelta, timezone
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String, ForeignKey, func, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship



class OtpStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    CANCEL = "cancel"



class OTP(Base):
    __tablename__ = "otps"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    phone_number: Mapped[str] = mapped_column(String, nullable=False)

    otp: Mapped[str] = mapped_column(String, nullable=False)

    status: Mapped[OtpStatus] = mapped_column(
        Enum(OtpStatus),
        default=OtpStatus.PENDING,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    expired_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc) + timedelta(minutes=1)
    )

    user = relationship("User", back_populates="otps")