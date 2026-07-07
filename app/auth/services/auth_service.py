from app.auth.schemas.auth_schema import UserRegisterSchema, UserLoginSchema
from app.db.session import get_db
from app.auth.services.jwt_service import verify_token
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.users.model.models import User
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


security = HTTPBearer()



async def user_register(db: AsyncSession, request: UserRegisterSchema):
    stmt = select(User).where(User.phone_number == request.phone_number)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )

    new_user = User(phone_number=request.phone_number, is_active=True)

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



async def get_user_from_db(db: AsyncSession, user_id):
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    return user



async def get_current_user(auth: HTTPAuthorizationCredentials = Depends(security), db: AsyncSession = Depends(get_db)) -> User:
    token = auth.credentials
    payload = verify_token(token, "access")

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await get_user_from_db(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or account disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return user

