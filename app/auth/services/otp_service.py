import json
from uuid import UUID
from app.users.model.models import User
from redis.asyncio import Redis
from app.auth.model.models import OTP, OtpStatus
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from random import randint
from datetime import datetime, timezone

# generate
async def generate_otp(user: User, db: AsyncSession, redis: Redis):
    stmt = select(OTP).where(OTP.user_id == user.id)
    result = await db.execute(stmt)
    existing_otp = result.scalars().first()

    random_code = str(randint(1000, 9999))
    now = datetime.now(timezone.utc)

    if existing_otp and existing_otp.status == OtpStatus.PENDING:
        if existing_otp.expired_at > now:
            return existing_otp.otp
        
        existing_otp.status = OtpStatus.CANCEL

    new_otp = OTP(
        user_id=user.id,
        phone_number=user.phone_number,
        otp=random_code,
    )


    db.add(new_otp)
    await db.commit()

    await redis.set(
        f"otp:{user.phone_number}",
        json.dumps({
            "otp": random_code,
            "user_id": str(user.id)
        }),
        ex=60
    )

    return random_code

# verified
async def  verified_otp(phone_number: str, input_otp: str, redis: Redis, db: AsyncSession):
    cached = await redis.get(f"otp:{phone_number}")
    if not cached:
        return False
    data = json.loads(cached)

    if data["otp"] != input_otp:
        return False
    user_id = UUID(data["user_id"])
    stmt = select(OTP).where(
        OTP.user_id == user_id,
        OTP.status == OtpStatus.PENDING
    )
    result = await db.execute(stmt)
    otp_request = result.scalars().first()
    if otp_request:
        otp_request.status = OtpStatus.VERIFIED
    await db.commit()
    await redis.delete(f"otp:{phone_number}")

    return True