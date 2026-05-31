from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.knowledge import KnowledgeBase, Message

router = APIRouter()

class KnowledgeItem(BaseModel):
    id: int
    disease_name: str
    disease_name_en: str
    crop_type: str
    symptoms: str
    prevention: str
    treatment: str

class MessageResponse(BaseModel):
    id: int
    username: str
    content: str
    created_at: str

@router.get("")
async def get_knowledge(
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(KnowledgeBase)

    if keyword:
        query = query.filter(
            KnowledgeBase.disease_name.contains(keyword) |
            KnowledgeBase.disease_name_en.contains(keyword)
        )

    items = query.limit(20).all()

    return {
        "items": [
            {
                "id": item.id,
                "disease_name": item.disease_name,
                "disease_name_en": item.disease_name_en,
                "crop_type": item.crop_type,
                "symptoms": item.symptoms,
                "prevention": item.prevention,
                "treatment": item.treatment
            }
            for item in items
        ]
    }

@router.get("/messages")
async def get_messages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    messages = db.query(Message).order_by(Message.id.desc()).limit(50).all()

    return [
        {
            "id": m.id,
            "username": m.username,
            "content": m.content,
            "created_at": "刚刚" if not hasattr(m, 'created_at') else str(m.id)
        }
        for m in messages
    ]

class PostMessageRequest(BaseModel):
    content: str

@router.post("/messages")
async def post_message(
    request: PostMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    message = Message(
        user_id=current_user.id,
        username=current_user.username,
        content=request.content
    )
    db.add(message)
    db.commit()
    db.refresh(message)

    return {"id": message.id, "message": "发布成功"}
