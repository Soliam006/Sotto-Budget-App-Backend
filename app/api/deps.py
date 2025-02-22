from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import Session
from app.models.user import User, UserOut
from app.crud.user import get_user, get_user_by_id, get_user_by_username
from app.core.config import settings
from app.core.database import get_session
from app.core.security import ALGORITHM
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")


def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> UserOut:

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = get_user(session=session, user_id=user_id)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: UserOut = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user