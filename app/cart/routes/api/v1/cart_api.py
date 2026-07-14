import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.cart.schemas.cart_schema import AddToCartSchema, UpdateCartItemSchema
from app.users.model.models import User
from app.db.session import get_db
from app.auth.services.auth_service import get_current_user
from app.cart.services.cart_service import CartManager



router = APIRouter(tags=['Cart'])

@router.post("/add_to_cart")
async def add_to_cart(
    data: AddToCartSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    return await CartManager.add_to_cart(
        db=db,
        data=data,
        current_user=current_user
    )

@router.get("/cart")
async def get_cart(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)):

    return await CartManager.get_cart(       
        db=db,
        current_user=current_user)


@router.patch("/cart/items/{product_id}")
async def update_qty_in_cart(
    product_id: uuid.UUID,
    data: UpdateCartItemSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):

    return await CartManager.update_qty(       
        db=db,
        data=data,
        current_user=current_user,
        product_id=product_id)

@router.post("/clear_cart")
async def clear_cart(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    
    return await CartManager.clear_cart(db=db, current_user=current_user)

@router.delete("/delete_item")
async def delete_item_from_cart(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)):

    return await CartManager.remove_item(db=db, current_user=current_user, product_id=product_id)
