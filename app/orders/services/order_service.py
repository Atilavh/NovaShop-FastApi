import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from app.products.models.model import Product
from app.users.model.models import User
from app.orders.models.model import Order, OrderItem
from app.cart.model.models import Cart, CartItem
from app.orders.schemas.order_schema import CreateOrderResponse, OrderItemResponse, OrderListResponse, OrderResponse


class OrderManagerRepository:
    @staticmethod
    async def create_order(
        db: AsyncSession, 
        current_user: User, 
        subtotal_price: int,
        shipping_price: int,
        discount_price: int,
        final_price: int) -> Order:
        new_order = Order(
            user_id=current_user.id,
            subtotal_price=subtotal_price,
            shipping_price=shipping_price,
            discount_price=discount_price,
            final_price=final_price,
        )

        db.add(new_order)
        await db.flush()
        await db.refresh(new_order)

        return new_order
    @staticmethod
    async def create_order_items(
        db: AsyncSession,
        order: Order,
        cart: Cart,
    ) -> list[OrderItem]:
        order_items: list[OrderItem] = []

        for item in cart.items:

            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product.id,
                title=item.product.title,
                price=item.product.price,
                quantity=item.quantity,
                total_price=item.product.price * item.quantity,
            )

            order_items.append(order_item)

        db.add_all(order_items)

        await db.flush()

        return order_items
        
    @staticmethod
    async def get_order_by_id():
        pass
    @staticmethod
    async def get_user_orders():
        pass
    @staticmethod
    async def update_order():
        pass
    @staticmethod
    async def delete_order():
        pass