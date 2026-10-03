import json
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..config import BASE_DIR
from ..database import get_db
from ..dependencies import current_user_optional
from ..models.db import Recommendation, User

router=APIRouter(); templates=Jinja2Templates(directory=str(BASE_DIR/"app"/"templates"))

def page(request: Request,name: str,user: User|None,**ctx):
    return templates.TemplateResponse(request=request,name=name,context={"user":user,**ctx})

@router.get("/",response_class=HTMLResponse)
def home(request: Request,user=Depends(current_user_optional)): return page(request,"index.html",user)
@router.get("/login",response_class=HTMLResponse)
def login_page(request: Request,user=Depends(current_user_optional)): return RedirectResponse("/dashboard") if user else page(request,"login.html",None,error=request.query_params.get("error"))
@router.get("/register",response_class=HTMLResponse)
def register_page(request: Request,user=Depends(current_user_optional)): return RedirectResponse("/dashboard") if user else page(request,"register.html",None,error=request.query_params.get("error"))
@router.get("/dashboard",response_class=HTMLResponse)
def dashboard(request: Request,user=Depends(current_user_optional),db:Session=Depends(get_db)):
    if not user:return RedirectResponse("/login",303)
    rows=db.query(Recommendation).filter(Recommendation.user_id==user.id).order_by(Recommendation.created_at.desc()).limit(5).all()
    return page(request,"dashboard.html",user,history=rows)
@router.get("/planner/home",response_class=HTMLResponse)
def home_planner(request:Request,user=Depends(current_user_optional)): return RedirectResponse("/login",303) if not user else page(request,"planner_home.html",user)
@router.get("/planner/party",response_class=HTMLResponse)
def party_planner(request:Request,user=Depends(current_user_optional)): return RedirectResponse("/login",303) if not user else page(request,"planner_party.html",user)
@router.get("/planner/jewelry",response_class=HTMLResponse)
def jewelry_planner(request:Request,user=Depends(current_user_optional)): return RedirectResponse("/login",303) if not user else page(request,"planner_jewelry.html",user)
@router.get("/history",response_class=HTMLResponse)
def history(request:Request,user=Depends(current_user_optional),db:Session=Depends(get_db)):
    if not user:return RedirectResponse("/login",303)
    rows=db.query(Recommendation).filter(Recommendation.user_id==user.id).order_by(Recommendation.created_at.desc()).all()
    return page(request,"history.html",user,history=rows)
@router.get("/recommendation/{rid}",response_class=HTMLResponse)
def recommendation_page(rid:int,request:Request,user=Depends(current_user_optional),db:Session=Depends(get_db)):
    if not user:return RedirectResponse("/login",303)
    row=db.query(Recommendation).filter(Recommendation.id==rid,Recommendation.user_id==user.id).first()
    if not row:return RedirectResponse("/history",303)
    return page(request,"recommendation.html",user,row=row,result=json.loads(row.response_json))
@router.get("/testimonials",response_class=HTMLResponse)
def testimonials(request:Request,user=Depends(current_user_optional)): return page(request,"testimonials.html",user)
