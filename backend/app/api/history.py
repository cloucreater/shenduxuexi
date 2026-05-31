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
from fastapi.responses import StreamingResponse
import csv
import io

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


# ── 导出接口 ──

@router.get("/export/json")
async def export_history_json(
    start_date: str = Query(""),
    end_date: str = Query(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Detection).filter(Detection.user_id == current_user.id)
    if start_date:
        from datetime import datetime
        query = query.filter(Detection.created_at >= datetime.strptime(start_date, "%Y-%m-%d"))
    if end_date:
        from datetime import datetime
        ed = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        query = query.filter(Detection.created_at <= ed)

    records = query.order_by(desc(Detection.created_at)).all()
    export = []
    for d in records:
        items = db.query(DetectionItem).filter(DetectionItem.detection_id == d.id).all()
        export.append({
            "id": d.id,
            "type": d.type,
            "source": d.source_path,
            "detections": [{"label": i.label, "label_en": i.label_en, "confidence": i.confidence} for i in items],
            "disease_count": len([i for i in items if i.label != "healthy"]),
            "created_at": d.created_at.strftime("%Y-%m-%d %H:%M:%S") if d.created_at else ""
        })
    return {"total": len(export), "records": export}


@router.get("/export/csv")
async def export_history_csv(
    start_date: str = Query(""),
    end_date: str = Query(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Detection).filter(Detection.user_id == current_user.id)
    if start_date:
        from datetime import datetime
        query = query.filter(Detection.created_at >= datetime.strptime(start_date, "%Y-%m-%d"))
    if end_date:
        from datetime import datetime
        ed = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        query = query.filter(Detection.created_at <= ed)

    records = query.order_by(desc(Detection.created_at)).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "类型", "来源", "病害", "置信度", "时间"])
    for d in records:
        items = db.query(DetectionItem).filter(DetectionItem.detection_id == d.id).all()
        for item in items:
            writer.writerow([
                d.id, d.type, d.source_path,
                item.label, item.confidence,
                d.created_at.strftime("%Y-%m-%d %H:%M:%S") if d.created_at else ""
            ])
        if not items:
            writer.writerow([d.id, d.type, d.source_path, "", "", d.created_at.strftime("%Y-%m-%d %H:%M:%S") if d.created_at else ""])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=history_export.csv"}
    )


@router.get("/share/{detection_id}")
async def share_detection(
    detection_id: int,
    db: Session = Depends(get_db)
):
    """生成可分享的检测结果（无鉴权）"""
    detection = db.query(Detection).filter(Detection.id == detection_id).first()
    if not detection:
        return {"error": "检测记录不存在"}

    items = db.query(DetectionItem).filter(DetectionItem.detection_id == detection.id).all()
    user = db.query(User).filter(User.id == detection.user_id).first()

    return {
        "id": detection.id,
        "type": detection.type,
        "detections": [
            {"label": i.label, "label_en": i.label_en, "confidence": i.confidence}
            for i in items
        ],
        "result_image": detection.result_image,
        "created_at": detection.created_at.strftime("%Y-%m-%d %H:%M:%S") if detection.created_at else "",
        "shared_by": user.username if user else "未知"
    }