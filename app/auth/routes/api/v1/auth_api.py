import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.auth.services.auth_service import user_register, user_login
from app.auth.services.jwt_service import (
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.utils.refresh_token_logic import RefreshTokenRepository
from datetime import datetime, timezone
from app.auth.schemas.auth_schema import UserRegisterSchema, UserLoginSchema, UserVerifiedSchema
from app.auth.services.otp_service import generate_otp, verified_otp
from app.db.redis import redis


router = APIRouter(tags=["Auth"])


@router.post('/register', status_code=status.HTTP_201_CREATED)
async def register(request: UserRegisterSchema, db: AsyncSession = Depends(get_db)):
   user = await user_register(db=db, request=request)
   otp = await generate_otp(user=user, db=db, redis=redis)

   return {
      "error": False,
      "message": "user registered successfully, otp sent",
      "otp": otp
   }


@router.post('/login')
async def login(request: UserLoginSchema, db: AsyncSession = Depends(get_db)):
   user = await user_login(db=db, request=request)
   otp = await generate_otp(user=user, db=db, redis=redis)

   return {
      "error": False,
      "message": "login successfully, otp sent",
      "otp": otp
   }

@router.post("/verified")
async def verified(request: UserVerifiedSchema, db: AsyncSession = Depends(get_db)):
    
    user = await verified_otp(
        phone_number=request.phone_number,
        input_otp=request.otp,
        redis=redis,
        db=db,
    )

    if not user:
        return {
            "error": True,
            "message": "otp invalid or expired",
        }

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    payload = verify_token(refresh_token, "refresh")

    await RefreshTokenRepository.create_refresh(
        db=db,
        user_id=user,
        jti=str(uuid.uuid4()),
        expires_at=datetime.fromtimestamp(
            payload["exp"],
            tz=timezone.utc,
        ),
    )

    await db.commit()

    return {
        "error": False,
        "message": "login successfully, Welcome",
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

@router.post("/logout")
async def logout(refresh_token: str, db: AsyncSession = Depends(get_db)):
    
    payload = verify_token(refresh_token, "refresh")

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
        )

    refresh = await RefreshTokenRepository.get_refresh_by_jti(
        db,
        payload["jti"],
    )

    if refresh:
        await RefreshTokenRepository.revoke_refresh(refresh)
        await db.commit()

    return {
        "message": "Logged out successfully",
    }


@router.post("/refresh")
async def refresh(token: str, db: AsyncSession = Depends(get_db)):
    
    payload = verify_token(token, "refresh")

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
        )

    refresh = await RefreshTokenRepository.get_refresh_by_jti(
        db,
        payload["jti"],
    )

    if refresh is None or refresh.is_revoked:
        raise HTTPException(
            status_code=401,
            detail="Refresh token revoked",
        )
    refresh.is_revoked = True

    await RefreshTokenRepository.create_refresh(
        db=db,
        user_id=payload["sub"],
        jti=str(uuid.uuid4()),
        expires_at=datetime.fromtimestamp(
            payload["exp"],
            tz=timezone.utc,
        ),
    )

    await db.commit()
    access_token = create_access_token(payload["sub"])
    refresh_token = create_refresh_token(payload["sub"])
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }