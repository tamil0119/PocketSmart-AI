import json
from sqlalchemy.orm import Session
from ..models.db import Recommendation

def save_recommendation(db: Session, user_id: int, category: str, request_data: dict, response_data: dict) -> Recommendation:
    row=Recommendation(user_id=user_id, category=category, request_json=json.dumps(request_data), response_json=json.dumps(response_data))
    db.add(row); db.commit(); db.refresh(row); return row
