import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from app.products.models.model import Product
from app.users.model.models import User
from app.cart.schemas.cart_schema import AddToCartSchema, GetCartSchema, CartItemResponse, UpdateCartItemSchema
from app.cart.model.models import Cart, CartItem

class CartManager:
    @staticmethod
    async def add_to_cart(db: AsyncSession, data: AddToCartSchema, current_user: User):
        product = await db.get(Product, data.product_id)
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": True,
                    "detail": "Product not found"
                }
            )
        
        if product.stock < data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": True,
                    "detail": "Not enough stoc"
                }
            )
        
        result = await db.execute(select(Cart).where(Cart.user_id == current_user.id))
        cart = result.scalar_one_or_none()
        if cart is None:
            cart = Cart(
                user_id=current_user.id
            )

            db.add(cart)

            await db.flush()

        result = await db.execute(
            select(CartItem).where(
                CartItem.cart_id == cart.id,
                CartItem.product_id == product.id
            )
        )

        cart_item = result.scalar_one_or_none()
        if cart_item:
            if product.stock < cart_item.quantity + data.quantity:
                raise HTTPException(
                    status_code=400,
                    detail="Not enough stock"
                )
            cart_item.quantity += data.quantity
        else:
             cart_item = CartItem(
                cart_id=cart.id,
                product_id=product.id,
                quantity=data.quantity,
                price=product.price
            )
        db.add(cart_item)

        await db.commit()

        return {
            "success": True,
            "message": "Product added to cart."
        }
    
    @staticmethod
    async def get_cart(db: AsyncSession, current_user: User):
        stmt = (
            select(Cart)
            .options(
                selectinload(Cart.items).selectinload(CartItem.product)
            )
            .where(Cart.user_id == current_user.id)
        )

        result = await db.execute(stmt)
        cart = result.scalar_one_or_none()

        if cart is None:
            return GetCartSchema(
                products=[],
                total_price=0,
            )
        total_price_of_cart = sum(
            item.price * item.quantity
            for item in cart.items
        )

        return GetCartSchema(
            products=[
                CartItemResponse(
                    product_id=item.product.id,
                    title=item.product.title,
                    price=item.price,
                    quantity=item.quantity,
                    stock=item.product.stock,
                    total_price=item.price * item.quantity,
                )
                for item in cart.items
            ],
            total_price=total_price_of_cart,
        )
        

    @staticmethod
    async def update_qty(db: AsyncSession, data: AddToCartSchema, current_user: User, product_id: uuid.UUID):
        stmt = select(CartItem).join(Cart).where(Cart.user_id == current_user.id, CartItem.product_id == product_id)
        result = await db.execute(stmt)
        cart_item = result.scalar_one_or_none()

        if cart_item is None:
            raise HTTPException(
                status_code=404,
                detail="Product not found in cart."
            )
        
        product = await db.get(Product, product_id)
        if data.quantity > product.stock:
            raise HTTPException(
                status_code=400,
                detail="Not enough stock."
            )

        cart_item.quantity = data.quantity

        await db.commit()
        await db.refresh(cart_item)

        return {
            "error": False,
            "message": "Quantity updated."
        }


    @staticmethod
    async def clear_cart(db: AsyncSession, current_user: User):
        stmt = (select(Cart).where(Cart.user_id == current_user.id))
        result = await db.execute(stmt)
        cart = result.scalar_one_or_none()
        if cart is None:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "error": False,
                    "detail": "cart already empty"
                }
            )

        await db.execute(delete(CartItem).where(CartItem.cart_id == cart.id))
        await db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "error": False,
                "detail": "Cart cleared."
            }
        )



    @staticmethod
    async def remove_item(db: AsyncSession, product_id: uuid.UUID, current_user: User):
        stmt = (select(CartItem).join(Cart).where(Cart.user_id == current_user.id, CartItem.product_id == product_id))
        result = await db.execute(stmt)
        cart_item = result.scalar_one_or_none()

        if cart_item is None:
            raise HTTPException(
                status_code=404,
                detail="Product not found in cart."
            )

        await db.delete(cart_item)
        await db.commit()

        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content={
                "error": True,
                "detail": "item deleted from cart"
            }
        )

    @staticmethod
    async def get_cart_model(
        db: AsyncSession,
        current_user: User,
    ) -> Cart | None:

        stmt = (
            select(Cart)
            .options(
                selectinload(Cart.items)
                .selectinload(CartItem.product)
            )
            .where(Cart.user_id == current_user.id)
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()
