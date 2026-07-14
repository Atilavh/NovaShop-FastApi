from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.auth.routes.api.v1.auth_api import router as auth_router
from app.users.routes.api.v1.users_api import router as user_router
from app.admin.routes.api.v1.admin_api import router as admin_router
from app.cart.routes.api.v1.cart_api import router as cart_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("System Active!")
    yield
    print("System ShutDown")

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(user_router, prefix="/api/v1/user")
app.include_router(admin_router, prefix="/api/v1/admin")
app.include_router(cart_router, prefix="/api/v1/cart")