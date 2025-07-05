import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from core.config import settings

# This URL should point to the login endpoint of your Auth Service.
# The client (frontend) will use this to know where to get a token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user_id(token: str = Depends(oauth2_scheme)) -> uuid.UUID:
    """
    Decodes the JWT token to get the user's ID.
    Raises an exception if the token is invalid or missing.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id_str: str | None = payload.get("user_id")
        if user_id_str is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    return uuid.UUID(user_id_str)