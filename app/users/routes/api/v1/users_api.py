from fastapi import Depends, APIRouter
from app.auth.services.auth_service import get_current_user
from app.users.model.models import User

router = APIRouter(tags=["User"])

@router.get("/me")
async def me(
    current_user: User = Depends(get_current_user),
):
    return current_user