from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from typing import Optional, Dict
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.detection import Detection, DetectionItem
from app.ml.detector import YOLODetector
from app.ml.deep_model import deep_learning_engine
import json

router = APIRouter()
detector = YOLODetector()

class EvaluationResponse(BaseModel):
    previous_count: int
    current_count: int
    change: float
    evaluation: str
    deep_analysis: Optional[Dict] = None

class DetailedEvaluationRequest(BaseModel):
    treatment_info: Dict
    before_detection_id: Optional[str] = None

@router.post("/compare")
async def evaluate_effect(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contents = await file.read()
    result = detector.detect_image(contents)

    current_detections = result["detections"]
    current_count = len([d for d in current_detections if d["label"] != "healthy"])

    last_detection = db.query(Detection).filter(
        Detection.user_id == current_user.id,
        Detection.type == "evaluation"
    ).order_by(desc(Detection.created_at)).first()

    before_data = []
    if last_detection:
        items = db.query(DetectionItem).filter(
            DetectionItem.detection_id == last_detection.id
        ).all()
        previous_count = len([item for item in items if item.label != "healthy"])
        before_data = [{
            "label": item.label,
            "label_en": item.label_en,
            "confidence": item.confidence
        } for item in items]
    else:
        previous_count = current_count

    if previous_count > 0:
        change = ((current_count - previous_count) / previous_count) * 100
    else:
        change = 0 if current_count == 0 else 100

    evaluation = "有效" if change <= -20 else ("一般" if change <= 20 else "无效")

    detection = Detection(
        user_id=current_user.id,
        type="evaluation",
        source_path=file.filename,
        result_image=result["result_image"]
    )
    db.add(detection)
    db.commit()
    db.refresh(detection)

    # 保存检测项到数据库
    current_data = []
    for d in current_detections:
        detection_item = DetectionItem(
            detection_id=detection.id,
            label=d["label"],
            label_en=d["label_en"],
            confidence=d["confidence"],
            bbox=json.dumps(d.get("bbox", []))
        )
        db.add(detection_item)
        current_data.append({
            "label": d["label"],
            "label_en": d["label_en"],
            "confidence": d["confidence"]
        })

    db.commit()

    deep_analysis = deep_learning_engine.evaluate_treatment_effect(
        before_data=before_data,
        after_data=current_data,
        treatment_info={"severity": "medium", "type": "chemical"}
    )

    return EvaluationResponse(
        previous_count=previous_count,
        current_count=current_count,
        change=round(change, 1),
        evaluation=evaluation,
        deep_analysis=deep_analysis
    )

@router.post("/detailed")
async def detailed_evaluation(
    request: DetailedEvaluationRequest,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contents = await file.read()
    result = detector.detect_image(contents)

    current_detections = result["detections"]
    current_data = [{
        "label": d["label"],
        "label_en": d["label_en"],
        "confidence": d["confidence"]
    } for d in current_detections]

    before_data = []
    if request.before_detection_id:
        before_detection = db.query(Detection).filter(
            Detection.id == request.before_detection_id,
            Detection.user_id == current_user.id
        ).first()
        if before_detection:
            items = db.query(DetectionItem).filter(
                DetectionItem.detection_id == before_detection.id
            ).all()
            before_data = [{
                "label": item.label,
                "label_en": item.label_en,
                "confidence": item.confidence
            } for item in items]

    deep_analysis = deep_learning_engine.evaluate_treatment_effect(
        before_data=before_data,
        after_data=current_data,
        treatment_info=request.treatment_info
    )

    detection = Detection(
        user_id=current_user.id,
        type="evaluation",
        source_path=file.filename,
        result_image=result["result_image"]
    )
    db.add(detection)
    db.commit()

    return {
        "current_detections": current_detections,
        "deep_analysis": deep_analysis
    }