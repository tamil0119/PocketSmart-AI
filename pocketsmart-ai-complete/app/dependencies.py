from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from .database import get_db
from .models.db import User
from .services.auth import decode_access_token

def current_user_optional(request: Request, db: Session = Depends(get_db)) -> User | None:
    token=request.cookies.get("access_token")
    if not token: return None
    uid=decode_access_token(token)
    return db.get(User,uid) if uid else None

def current_user(user: User|None=Depends(current_user_optional)) -> User:
    if not user: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required")
    return user
