from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional, Dict
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.detection import Detection, DetectionItem
from app.ml.deep_model import deep_learning_engine
import json

router = APIRouter()

class DetectionRecord(BaseModel):
    id: str
    image_url: Optional[str]
    result_image: Optional[str]
    detections: List[dict]
    detection_time: float
    created_at: str

@router.get("")
async def get_history(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    offset = (page - 1) * limit

    total = db.query(Detection).filter(
        Detection.user_id == current_user.id
    ).count()

    detections = db.query(Detection).filter(
        Detection.user_id == current_user.id
    ).order_by(desc(Detection.created_at)).offset(offset).limit(limit).all()

    records = []
    for d in detections:
        items = db.query(DetectionItem).filter(
            DetectionItem.detection_id == d.id
        ).all()

        records.append({
            "id": str(d.id),
            "image_url": d.source_path,
            "result_image": d.result_image,
            "detections": [
                {
                    "label": item.label,
                    "label_en": item.label_en,
                    "confidence": item.confidence,
                    "bbox": json.loads(item.bbox) if item.bbox else []
                }
                for item in items
            ],
            "detection_time": 0,
            "created_at": d.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    return {"records": records, "total": total}

@router.post("/compare")
async def compare_history(
    period1: dict,
    period2: dict,
    comparison_type: str = "disease",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from datetime import datetime

    p1_start = datetime.strptime(period1["start"], "%Y-%m-%d")
    p1_end = datetime.strptime(period1["end"], "%Y-%m-%d")
    p2_start = datetime.strptime(period2["start"], "%Y-%m-%d")
    p2_end = datetime.strptime(period2["end"], "%Y-%m-%d")

    def get_detection_data(start, end):
        detections = db.query(Detection).filter(
            Detection.user_id == current_user.id,
            Detection.created_at >= start,
            Detection.created_at <= end
        ).all()

        detection_data = []
        for d in detections:
            items = db.query(DetectionItem).filter(
                DetectionItem.detection_id == d.id
            ).all()
            for item in items:
                detection_data.append({
                    "label": item.label,
                    "label_en": item.label_en,
                    "confidence": item.confidence,
                    "created_at": d.created_at
                })
        return detection_data

    period1_data = get_detection_data(p1_start, p1_end)
    period2_data = get_detection_data(p2_start, p2_end)

    deep_analysis = deep_learning_engine.analyze_historical_comparison(
        period1_data, period2_data, comparison_type
    )

    def get_category_counts(start, end):
        detections = db.query(Detection).filter(
            Detection.user_id == current_user.id,
            Detection.created_at >= start,
            Detection.created_at <= end
        ).all()

        counts = {}
        for d in detections:
            items = db.query(DetectionItem).filter(
                DetectionItem.detection_id == d.id
            ).all()
            for item in items:
                counts[item.label] = counts.get(item.label, 0) + 1

        return counts

    p1_counts = get_category_counts(p1_start, p1_end)
    p2_counts = get_category_counts(p2_start, p2_end)

    all_categories = set(list(p1_counts.keys()) + list(p2_counts.keys()))

    categories = []
    period1_values = []
    period2_values = []
    details = []

    for cat in all_categories:
        if cat != "healthy":
            categories.append(cat)
            period1_values.append(p1_counts.get(cat, 0))
            period2_values.append(p2_counts.get(cat, 0))

            p1_count = p1_counts.get(cat, 0)
            p2_count = p2_counts.get(cat, 0)
            change = p2_count - p1_count
            change_rate = ((p2_count - p1_count) / p1_count * 100) if p1_count > 0 else (100 if p2_count > 0 else 0)

            details.append({
                "category": cat,
                "period1_count": p1_count,
                "period2_count": p2_count,
                "change": change,
                "change_rate": round(change_rate, 1)
            })

    return {
        "categories": categories,
        "period1_values": period1_values,
        "period2_values": period2_values,
        "details": details,
        "deep_analysis": deep_analysis
    }