from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.auth.routes.api.v1.auth_api import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("System Active!")
    yield
    print("System ShutDown")

app = FastAPI(lifespan=lifespan)

app.include_router(router, prefix="/api/v1/auth")
