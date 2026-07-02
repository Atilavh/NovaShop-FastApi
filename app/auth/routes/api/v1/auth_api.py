from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.auth.services.auth_service import user_register, user_login
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

@router.post('/vreified')
async def verified(request: UserVerifiedSchema, db: AsyncSession = Depends(get_db)):
   result = await verified_otp(phone_number=request.phone_number, input_otp=request.otp, redis=redis, db=db)
   if not result:
      return {
         "error": True,
         "message": "otp invalid or expired",
      }
   return {
      "error": False,
      "message": "login successfully, Welcome",
      "access_token":"test",
      "refresh_token":"test"
   }