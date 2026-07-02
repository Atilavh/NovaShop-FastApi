from app.auth.schemas.auth_schema import UserRegisterSchema, UserLoginSchema, UserVerifiedSchema
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.users.model.models import User
from fastapi import HTTPException, status





async def user_register(db: AsyncSession, request: UserRegisterSchema):
    stmt = select(User).where(User.phone_number == request.phone_number)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )

    new_user = User(phone_number=request.phone_number)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


async def user_login(db: AsyncSession, request: UserLoginSchema):
    stmt = select(User).where(User.phone_number == request.phone_number)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User already exists"
        )
    
    existing_user.is_active = True
    await db.commit()
    return existing_user