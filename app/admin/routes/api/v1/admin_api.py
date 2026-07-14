import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, APIRouter, status, HTTPException, Path
from fastapi.responses import JSONResponse
from typing import List
from app.db.session import get_db
from app.auth.services.auth_service import get_current_user
from app.users.model.models import User
from app.products.models.model import Product
from app.admin.service.admin_services import AdminProductManager
from app.admin.schema.admin_crud_schema import AdminCreateProductSchema, AdminUpdateProductSchema, ProductResponse


router = APIRouter(tags=["Admin"])

class AdminProductApi:
    @staticmethod
    @router.post("/products", status_code=status.HTTP_201_CREATED)
    async def create_product(
        request: AdminCreateProductSchema,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        await AdminProductManager.c_product(db=db, request=request, current_user=current_user)
        return JSONResponse(content={ 
            "detail": "product created!"
        }, status_code=status.HTTP_201_CREATED)
    
    @staticmethod
    @router.put("/products", status_code=status.HTTP_200_OK)
    async def update_product(
        request: AdminUpdateProductSchema,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        await AdminProductManager.u_product(db=db, request=request, current_user=current_user)
        return JSONResponse(content={ 
            "detail": "product update successfully!"
        }, status_code=status.HTTP_200_OK)
    
    @staticmethod
    @router.get("/products", status_code=status.HTTP_200_OK, response_model=List[ProductResponse])
    async def retrive_products(
        db: AsyncSession = Depends(get_db)
    ):
       return await AdminProductManager.r_products(db=db)
    
    @staticmethod
    @router.get("/products/{product_id}", status_code=status.HTTP_200_OK, response_model=ProductResponse)
    async def retrive_product(
        db: AsyncSession = Depends(get_db),
        product_id: uuid.UUID = Path(...)
    ):
       return await AdminProductManager.r_product(db=db, prodcut_id=product_id)
    
    @staticmethod
    @router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_product(
        db: AsyncSession = Depends(get_db),
        product_id: uuid.UUID = Path(...),
        current_user: User = Depends(get_current_user)
    ):
       return await AdminProductManager.d_product(db=db, product_id=product_id, current_user=current_user)