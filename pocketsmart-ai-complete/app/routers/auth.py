from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.db import User
from ..services.auth import authenticate_user, create_access_token, hash_password
from ..dependencies import current_user

router=APIRouter()

def _redirect_with_token(url: str, token: str):
    r=RedirectResponse(url=url,status_code=303); r.set_cookie("access_token",token,httponly=True,samesite="lax",max_age=86400); return r

@router.post("/register")
def register(name: str=Form(...), email: str=Form(...), password: str=Form(...), db: Session=Depends(get_db)):
    email=email.lower().strip()
    if len(password)<8: return RedirectResponse("/register?error=Password+must+be+at+least+8+characters",303)
    if db.query(User).filter(User.email==email).first(): return RedirectResponse("/register?error=Email+already+registered",303)
    user=User(name=name.strip(),email=email,password_hash=hash_password(password)); db.add(user); db.commit(); db.refresh(user)
    return _redirect_with_token("/dashboard",create_access_token(user.id))

@router.post("/login")
def login(email: str=Form(...), password: str=Form(...), db: Session=Depends(get_db)):
    user=authenticate_user(db,email,password)
    if not user: return RedirectResponse("/login?error=Invalid+email+or+password",303)
    return _redirect_with_token("/dashboard",create_access_token(user.id))

@router.get("/logout")
def logout():
    r=RedirectResponse("/",303); r.delete_cookie("access_token"); return r

@router.post("/token")
def token(email: str=Form(...), password: str=Form(...), db: Session=Depends(get_db)):
    user=authenticate_user(db,email,password)
    if not user: return JSONResponse({"detail":"Invalid credentials"},status_code=401)
    return {"access_token":create_access_token(user.id),"token_type":"bearer"}

@router.get("/session-info")
def session_info(user: User=Depends(current_user)):
    return {"logged_in":True,"user_id":user.id,"name":user.name,"email":user.email}

@router.get("/session-data")
def session_data(user: User=Depends(current_user)):
    return {"user":{"id":user.id,"name":user.name,"email":user.email},"personalization":{"history_enabled":True}}
