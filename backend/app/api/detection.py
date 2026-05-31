from fastapi import APIRouter, Depends, UploadFile, File, WebSocket, WebSocketDisconnect, Form
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional
import base64
import json
import time
import cv2
import numpy as np
from PIL import Image
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.detection import Detection, DetectionItem
from app.ml.detector import YOLODetector
from app.ml.deep_model import deep_learning_engine

router = APIRouter()
detector = YOLODetector()

class DetectionResult(BaseModel):
    bbox: List[float]
    label: str
    label_en: str
    confidence: float

class DetectionResponse(BaseModel):
    image_id: str
    detections: List[DetectionResult]
    result_image: str
    detection_time: float

@router.post("/image", response_model=DetectionResponse)
async def detect_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    start_time = time.time()

    contents = await file.read()
    result = detector.detect_image(contents)

    detection = Detection(
        user_id=current_user.id,
        type="image",
        source_path=file.filename,
        result_image=result["result_image"]
    )
    db.add(detection)
    db.commit()
    db.refresh(detection)

    for item in result["detections"]:
        detection_item = DetectionItem(
            detection_id=detection.id,
            label=item["label"],
            label_en=item["label_en"],
            confidence=item["confidence"],
            bbox=json.dumps(item["bbox"])
        )
        db.add(detection_item)

    db.commit()

    detection_time = (time.time() - start_time) * 1000

    return DetectionResponse(
        image_id=str(detection.id),
        detections=[DetectionResult(**d) for d in result["detections"]],
        result_image=result["result_image"],
        detection_time=detection_time
    )


@router.post("/batch")
async def detect_images_batch(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """批量图片检测（最多20张）"""
    if len(files) > 20:
        return {"error": "一次性最多上传20张图片", "total": 0, "results": []}

    results = []
    total_start = time.time()

    for i, file in enumerate(files):
        try:
            contents = await file.read()
            result = detector.detect_image(contents)

            detection = Detection(
                user_id=current_user.id,
                type="image",
                source_path=file.filename,
                result_image=result["result_image"]
            )
            db.add(detection)
            db.commit()
            db.refresh(detection)

            for item in result["detections"]:
                detection_item = DetectionItem(
                    detection_id=detection.id,
                    label=item["label"],
                    label_en=item["label_en"],
                    confidence=item["confidence"],
                    bbox=json.dumps(item["bbox"])
                )
                db.add(detection_item)
            db.commit()

            results.append({
                "index": i,
                "filename": file.filename,
                "id": str(detection.id),
                "detections": result["detections"],
                "result_image": result["result_image"],
                "status": "success"
            })
        except Exception as e:
            results.append({
                "index": i,
                "filename": file.filename,
                "status": "error",
                "error": str(e)
            })

    total_time = (time.time() - total_start) * 1000

    return {
        "total": len(files),
        "success_count": sum(1 for r in results if r["status"] == "success"),
        "error_count": sum(1 for r in results if r["status"] == "error"),
        "results": results,
        "total_time_ms": round(total_time, 1)
    }

@router.post("/video")
async def detect_video(
    file: UploadFile = File(...),
    frame_rate: int = Form(30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contents = await file.read()
    basic_result = detector.detect_video(contents)

    temp_path = "temp_video_analysis.mp4"
    with open(temp_path, "wb") as f:
        f.write(contents)

    cap = cv2.VideoCapture(temp_path)
    frames = []
    frame_count = 0
    max_frames = 50

    while frame_count < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % 5 == 0:
            frames.append(frame)
        frame_count += 1

    cap.release()

    import os
    os.remove(temp_path)

    deep_analysis = None
    if frames:
        deep_analysis = deep_learning_engine.analyze_video_detection(frames, frame_rate)

    detection = Detection(
        user_id=current_user.id,
        type="video",
        source_path=file.filename,
        total_frames=basic_result["total_frames"],
        disease_frames=basic_result["disease_frames"],
        disease_rate=basic_result["disease_rate"]
    )
    db.add(detection)
    db.commit()
    db.refresh(detection)

    for i, item in enumerate(basic_result["top_frames"]):
        detection_item = DetectionItem(
            detection_id=detection.id,
            label=item["label"],
            label_en=item["label_en"],
            confidence=item["confidence"],
            frame_id=item["frame_id"]
        )
        db.add(detection_item)

    db.commit()

    return {
        **basic_result,
        "deep_analysis": deep_analysis
    }

@router.post("/video/realtime")
async def detect_video_realtime(
    file: UploadFile = File(...),
    sensitivity: str = Form("medium"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contents = await file.read()

    temp_path = "temp_video_realtime.mp4"
    with open(temp_path, "wb") as f:
        f.write(contents)

    cap = cv2.VideoCapture(temp_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    alert_frames = []
    disease_timeline = []
    frame_id = 0
    max_analysis_frames = 100

    sensitivity_threshold = {
        "low": 0.9,
        "medium": 0.7,
        "high": 0.5
    }.get(sensitivity, 0.7)

    while frame_id < min(total_frames, max_analysis_frames):
        ret, frame = cap.read()
        if not ret:
            break

        if frame_id % 10 == 0:
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            if detector.yolo_model:
                results = detector.model(image, verbose=False)
                frame_diseases = []

                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        cls = int(box.cls[0])
                        conf = float(box.conf[0])

                        if cls < len(detector.DISEASE_LABELS):
                            label_en, label_cn = detector.DISEASE_LABELS[cls]
                        else:
                            label_en, label_cn = f"class_{cls}", f"类别{cls}"

                        if conf >= sensitivity_threshold and label_en != "healthy":
                            frame_diseases.append({
                                "label": label_cn,
                                "label_en": label_en,
                                "confidence": conf,
                                "bbox": box.xyxy[0].tolist()
                            })

                if frame_diseases:
                    alert_frames.append({
                        "frame_id": frame_id,
                        "timestamp": frame_id / fps,
                        "diseases": frame_diseases,
                        "severity": "high" if any(d["confidence"] > 0.8 for d in frame_diseases) else "medium"
                    })

                disease_timeline.append({
                    "frame_id": frame_id,
                    "timestamp": frame_id / fps,
                    "disease_count": len(frame_diseases),
                    "max_confidence": max([d["confidence"] for d in frame_diseases]) if frame_diseases else 0
                })

        frame_id += 1

    cap.release()

    import os
    os.remove(temp_path)

    risk_assessment = "低风险"
    if len(alert_frames) > 5:
        risk_assessment = "高风险"
    elif len(alert_frames) > 2:
        risk_assessment = "中风险"

    recommendations = []
    if risk_assessment == "高风险":
        recommendations.append("检测到多处病害，建议立即进行防治")
        recommendations.append("病害呈扩散趋势，需加强监测频次")
    elif risk_assessment == "中风险":
        recommendations.append("检测到少量病害，建议关注病情发展")
        recommendations.append("可考虑预防性施药")
    else:
        recommendations.append("当前病害风险较低，保持正常管理")

    return {
        "total_frames_analyzed": frame_id,
        "alert_frames": alert_frames,
        "disease_timeline": disease_timeline,
        "risk_assessment": risk_assessment,
        "recommendations": recommendations,
        "sensitivity_level": sensitivity,
        "analysis_summary": {
            "total_alerts": len(alert_frames),
            "disease_frequency": len(alert_frames) / (frame_id / 10) if frame_id > 0 else 0,
            "avg_disease_per_frame": sum(dt["disease_count"] for dt in disease_timeline) / len(disease_timeline) if disease_timeline else 0
        }
    }

@router.websocket("/ws/camera")
async def camera_detection(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if "image" in message:
                image_data = base64.b64decode(message["image"].split(",")[1])
                result = detector.detect_image(image_data)

                await websocket.send_json({
                    "detections": result["detections"],
                    "result_image": result["result_image"]
                })
    except WebSocketDisconnect:
        pass