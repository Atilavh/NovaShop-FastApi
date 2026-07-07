from fastapi import Depends, APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.services.auth_service import get_current_user
from app.users.model.models import User
from app.users.schema.user_schema import UpdateProfileSchema
from app.db.session import get_db
from app.utils.jalali import to_jalali

router = APIRouter(tags=["User"])

@router.get("/me")
async def me(
    current_user: User = Depends(get_current_user),
):
    return JSONResponse(content={
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "phone_number": current_user.phone_number,
        "is_active": current_user.is_active,
        "role": current_user.role,
        "last_login": to_jalali(current_user.last_login),
        "created_at": to_jalali(current_user.created_at),
        "updated_at": to_jalali(current_user.updated_at),
    }, status_code=status.HTTP_200_OK)


@router.patch("/me")
async def update_profile(
    request: UpdateProfileSchema,
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
    ):

    current_user.first_name = request.first_name
    current_user.last_name = request.last_name

    await db.commit()
    await db.refresh(current_user)

    return JSONResponse(content={
        "error": False,
        "detail": "User profile updated!"
    }, status_code=status.HTTP_200_OK)