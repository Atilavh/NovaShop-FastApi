import jwt
import uuid
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from datetime import datetime, timezone, timedelta
from app.core.config import settings


def create_access_token(user_id, token_type: str = "access"):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": now,
        "iss": "NovaShop",
        "type": token_type
    }
    return jwt.encode(payload, settings.SECRET_KEY,algorithm=settings.ALGORITHM)

def create_refresh_token(user_id, token_type: str = "refresh"):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "exp": now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        "iat": now,
        "jti": str(uuid.uuid4()),
        "iss": "NovaShop",
        "type": token_type
    }
    return jwt.encode(payload, settings.SECRET_KEY,algorithm=settings.ALGORITHM)


def verify_token(token, token_type: str) -> dict | None:
    try: 
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=settings.ALGORITHM,
            issuer="NovaShop"
        )
        if payload.get("type") != token_type:
            return None
        
        return payload
    
    except ExpiredSignatureError:
        return None
    except InvalidTokenError:
        return None

