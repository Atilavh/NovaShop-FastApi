from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # db configs
    DATABASE_URL: str
    DATABASE_SYNC_URL: str

    # jwt configs
    SECRET_KEY: str
    ALGORITHM: str = "HS256"  
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    model_config = SettingsConfigDict(env_file='.env', extra="ignore")


settings = Settings()