from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from app.users.model.models import User, UserRole
from app.products.models.model import Product
from app.admin.schema.admin_crud_schema import AdminCreateProductSchema, AdminUpdateProductSchema

class AdminProductManager:
    @staticmethod
    async def r_products(db: AsyncSession):
        stmt = select(Product)
        result = await db.execute(stmt)
        return result.scalars().all()
    @staticmethod
    async def r_product(db: AsyncSession, prodcut_id):
        stmt = select(Product).where(Product.id == prodcut_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def c_product(
        db: AsyncSession,
        current_user: User,
        request: AdminCreateProductSchema
    ):
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(detail={
                "error": True,
                "detail": "Unauthorized access"
            }, status_code=status.HTTP_403_FORBIDDEN)
        try:
            data = request.model_dump()
            new_product = Product(**data)

            db.add(new_product)
            await db.commit()
            await db.refresh(new_product)

            return new_product
        except Exception as e:
            raise HTTPException(detail=f"Error {e}", status_code=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    async def u_product(
        db: AsyncSession,
        current_user: User,
        request: AdminUpdateProductSchema
    ):
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(detail={
                "error": True,
                "detail": "Unauthorized access"
            }, status_code=status.HTTP_403_FORBIDDEN)

        try:
            product_id = request.id
            stmt = select(Product).where(Product.id == product_id)
            result = await db.execute(stmt)
            product = result.scalar_one_or_none()
            if product is None:
                raise HTTPException(detail={
                    "error": True,
                    "detail": "product not found with this id"
                }, status_code=status.HTTP_400_BAD_REQUEST)
            data = request.model_dump(exclude_unset=True)
            for field, value in data.items():
                setattr(product, field, value)
            
            await db.commit()
            await db.refresh(product)

            return product
        except Exception as e:
            raise HTTPException(detail=f"Error {e}", status_code=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    async def d_product(db:AsyncSession, product_id, current_user):
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(detail={
                "error": True,
                "detail": "Unauthorized access"
            }, status_code=status.HTTP_403_FORBIDDEN)
        
        try:
            stmt = select(Product).where(Product.id == product_id)
            result = await db.execute(stmt)
            product = result.scalar_one_or_none()
            if product is None:
                raise HTTPException(detail={
                    "error": True,
                    "detail": "product not found with this id"
                }, status_code=status.HTTP_404_NOT_FOUND)
            
            await db.delete(product)
            await db.commit()
            return JSONResponse(content={
                "error": False,
                "detail": "product successfully deleted"
            })
        except Exception as e:
            raise HTTPException(detail=f"Error {e}", status_code=status.HTTP_400_BAD_REQUEST)