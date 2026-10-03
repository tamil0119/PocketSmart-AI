import json
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from ..config import get_settings
from ..database import get_db
from ..dependencies import current_user
from ..models.db import User, Recommendation
from ..models.schemas import HomeRequest, PartyRequest
from ..services.history import save_recommendation
from ..services.recommendation import home_recommendations, party_recommendations, jewelry_recommendations

router=APIRouter(prefix="/api",tags=["API"]); settings=get_settings()

@router.post("/generate-home")
def generate_home(payload: HomeRequest, user: User=Depends(current_user), db: Session=Depends(get_db)):
    req=payload.model_dump(); result=home_recommendations(req); row=save_recommendation(db,user.id,"home",req,result); return {**result,"id":row.id}

@router.post("/generate-party")
def generate_party(payload: PartyRequest, user: User=Depends(current_user), db: Session=Depends(get_db)):
    req=payload.model_dump(); result=party_recommendations(req); row=save_recommendation(db,user.id,"party",req,result); return {**result,"id":row.id}

@router.post("/generate-jewelry")
async def generate_jewelry(budget: float=Form(...), occasion: str=Form(...), style: str=Form("elegant"), outfit_color: str=Form(""), notes: str=Form(""), image: UploadFile|None=File(None), user: User=Depends(current_user), db: Session=Depends(get_db)):
    if budget<=0: raise HTTPException(422,"Budget must be greater than 0")
    req={"budget":budget,"occasion":occasion,"style":style,"outfit_color":outfit_color,"notes":notes}
    image_bytes=None; mime=None
    if image and image.filename:
        mime=image.content_type or "application/octet-stream"
        if not mime.startswith("image/"): raise HTTPException(400,"Only image uploads are allowed")
        image_bytes=await image.read()
        if len(image_bytes)>settings.max_upload_mb*1024*1024: raise HTTPException(413,"Image too large")
        req["image_filename"]=image.filename
    result=jewelry_recommendations(req,image_bytes,mime); row=save_recommendation(db,user.id,"jewelry",req,result); return {**result,"id":row.id}

@router.get("/recommendations-details/{recommendation_id}")
def details(recommendation_id: int, user: User=Depends(current_user), db: Session=Depends(get_db)):
    row=db.query(Recommendation).filter(Recommendation.id==recommendation_id,Recommendation.user_id==user.id).first()
    if not row: raise HTTPException(404,"Recommendation not found")
    return {"id":row.id,"category":row.category,"request":json.loads(row.request_json),"response":json.loads(row.response_json),"created_at":row.created_at.isoformat()}
