"""
病虫害检测器 — 集成 YOLOv8 目标检测 + 训练好的 CNN 分类器
"""
import base64
import io
import os
from PIL import Image
import cv2
import numpy as np
from typing import Dict, List, Any

# 导入训练好的 CNN 分类器
from app.ml.cnn_classifier import load_cnn_classifier, predict_image, CNNClassifier


class YOLODetector:
    # 中文标签映射
    DISEASE_LABELS = {
        0: ("healthy", "健康"),
        1: ("leaf_spot", "叶斑病"),
        2: ("rust", "锈病"),
        3: ("powdery_mildew", "白粉病"),
        4: ("early_blight", "早疫病"),
        5: ("late_blight", "晚疫病"),
    }

    def __init__(self):
        self.yolo_model = None
        self.cnn_classifier = None  # 训练好的 CNN 分类器
        self.use_cnn = False
        self._load_models()

    def _load_models(self):
        """加载所有可用模型"""
        # 1. 尝试加载 YOLOv8
        try:
            from ultralytics import YOLO
            yolo_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "yolov8n.pt"
            )
            if os.path.exists(yolo_path):
                self.yolo_model = YOLO(yolo_path)
                print(f"[DETECTOR] [OK] YOLOv8 已加载: {yolo_path}")
            else:
                self.yolo_model = YOLO("yolov8n.pt")
                print("[DETECTOR] [OK] YOLOv8 已加载 (下载)")
        except Exception as e:
            print(f"[DETECTOR] [WARN] YOLOv8 加载失败: {e}")
            self.yolo_model = None

        # 2. 加载训练好的 CNN 分类器（真实模型！）
        self.cnn_classifier = load_cnn_classifier()
        if self.cnn_classifier is not None:
            self.use_cnn = True
            print("[DETECTOR] [OK] CNN 分类器已就绪，将使用真实模型推理")
        else:
            print("[DETECTOR] [WARN] CNN 分类器未加载，将使用模拟数据")

    def detect_image(self, image_data: bytes) -> Dict[str, Any]:
        """图片检测 — 使用真实 CNN 模型 + YOLO 定位"""
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        detections = []

        # ━━━ 方案一：使用训练好的 CNN 进行全图分类 ━━━
        if self.use_cnn and self.cnn_classifier is not None:
            try:
                result = predict_image(self.cnn_classifier, image)
                detections.append({
                    "bbox": [10, 10, image.width - 10, image.height - 10],
                    "label": result["label"],
                    "label_en": result["label_en"],
                    "confidence": result["confidence"],
                    "source": "CNN_v2_trained",
                    "all_probabilities": result.get("all_probabilities", {}),
                })
            except Exception as e:
                print(f"[DETECTOR] CNN 推理出错: {e}")

        # ━━━ 方案二：YOLO 定位 + 区域 CNN 分类（增强检测） ━━━
        if self.yolo_model is not None and len(detections) == 0:
            try:
                results = self.yolo_model(image, verbose=False)
                for result in results:
                    boxes = result.boxes
                    if boxes is not None:
                        for box in boxes:
                            cls = int(box.cls[0])
                            conf = float(box.conf[0])

                            if cls < len(self.DISEASE_LABELS):
                                label_en, label_cn = self.DISEASE_LABELS[cls]
                            else:
                                label_en, label_cn = f"class_{cls}", f"类别{cls}"

                            detections.append({
                                "bbox": box.xyxy[0].tolist(),
                                "label": label_cn,
                                "label_en": label_en,
                                "confidence": round(conf, 4),
                                "source": "YOLOv8",
                            })
            except Exception as e:
                print(f"[DETECTOR] YOLO 推理出错: {e}")

        # ━━━ 方案三：CNN 存在但 YOLO 也检测到物体 → 合并结果 ━━━
        if self.use_cnn and self.yolo_model is not None and len(detections) > 0:
            try:
                results = self.yolo_model(image, verbose=False)
                yolo_classes = set()
                for result in results:
                    boxes = result.boxes
                    if boxes is not None:
                        for box in boxes:
                            cls = int(box.cls[0])
                            if cls < len(self.DISEASE_LABELS):
                                yolo_classes.add(self.DISEASE_LABELS[cls][0])

                # 如果 YOLO 检测到不同类别，补充标注（但不重复 CNN 的分类结果）
                if yolo_classes:
                    detections[0]["yolo_confirmation"] = list(yolo_classes)
            except Exception:
                pass

        # ━━━ 绘制结果图 ━━━
        result_image = self._draw_boxes(image, detections)
        buffered = io.BytesIO()
        result_image.save(buffered, format="JPEG", quality=90)
        result_base64 = base64.b64encode(buffered.getvalue()).decode()

        print(f"[DETECTOR] 检测完成: {len(detections)} 个结果")
        for d in detections:
            print(f"  - {d['label']} ({d.get('source', 'unknown')}): {d['confidence']:.2%}")

        return {
            "detections": detections,
            "result_image": result_base64,
        }

    def detect_video(self, video_data: bytes) -> Dict[str, Any]:
        """视频检测 — 逐帧 CNN 分类"""
        temp_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "temp_video.mp4"
        )

        with open(temp_path, "wb") as f:
            f.write(video_data)

        cap = cv2.VideoCapture(temp_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        category_counts: Dict[str, int] = {}
        disease_frames = 0
        top_frames: List[Dict] = []
        sampled_frames = 0

        frame_id = 0
        sample_interval = max(1, total_frames // 20)  # 采样 ~20 帧

        while frame_id < min(total_frames, 200):
            ret, frame = cap.read()
            if not ret:
                break

            if frame_id % sample_interval == 0 and sampled_frames < 20:
                image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

                # 使用训练好的 CNN 分类
                if self.use_cnn and self.cnn_classifier is not None:
                    try:
                        result = predict_image(self.cnn_classifier, image)
                        label_cn = result["label"]
                        label_en = result["label_en"]
                        conf = result["confidence"]

                        if label_en != "healthy":
                            category_counts[label_cn] = category_counts.get(label_cn, 0) + 1
                            disease_frames += 1

                            if len(top_frames) < 10:
                                top_frames.append({
                                    "frame_id": frame_id,
                                    "label": label_cn,
                                    "label_en": label_en,
                                    "confidence": round(conf, 4),
                                    "source": "CNN_v2_trained",
                                })
                    except Exception as e:
                        print(f"[DETECTOR] 视频帧 CNN 推理出错: {e}")
                elif self.yolo_model is not None:
                    results = self.yolo_model(image, verbose=False)
                    for result in results:
                        boxes = result.boxes
                        if boxes is not None:
                            for box in boxes:
                                cls = int(box.cls[0])
                                conf = float(box.conf[0])
                                if cls < len(self.DISEASE_LABELS):
                                    label_en, label_cn = self.DISEASE_LABELS[cls]
                                    if label_en != "healthy":
                                        category_counts[label_cn] = category_counts.get(label_cn, 0) + 1
                                        disease_frames += 1
                                        if len(top_frames) < 10:
                                            top_frames.append({
                                                "frame_id": frame_id,
                                                "label": label_cn,
                                                "label_en": label_en,
                                                "confidence": round(conf, 4),
                                                "source": "YOLOv8",
                                            })

                sampled_frames += 1

            frame_id += 1

        cap.release()
        if os.path.exists(temp_path):
            os.remove(temp_path)

        categories = []
        for name, count in category_counts.items():
            categories.append({
                "name": name,
                "count": count,
                "frame_count": count,
                "percentage": round(count / sampled_frames * 100, 1) if sampled_frames > 0 else 0,
                "avg_confidence": round(
                    sum(f["confidence"] for f in top_frames if f["label"] == name) /
                    max(1, sum(1 for f in top_frames if f["label"] == name)), 4
                ),
            })

        return {
            "total_frames": total_frames,
            "disease_frames": disease_frames,
            "disease_rate": round(disease_frames / sampled_frames, 4) if sampled_frames > 0 else 0,
            "categories": categories,
            "top_frames": top_frames,
            "model_used": "CNN_v2_trained" if self.use_cnn else "YOLOv8",
        }

    def _draw_boxes(self, image: Image.Image, detections: List[Dict]) -> Image.Image:
        """在图片上绘制检测框和标签"""
        img_array = np.array(image)
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

        # 每个类别的颜色
        class_colors = {
            "healthy": (0, 180, 0),
            "健康": (0, 180, 0),
            "Bacterial_spot": (0, 0, 255),
            "细菌性斑点病": (0, 0, 255),
            "Early_blight": (0, 140, 255),
            "早疫病": (0, 140, 255),
            "Late_blight": (0, 100, 255),
            "晚疫病": (0, 100, 255),
            "Leaf_Mold": (180, 0, 180),
            "叶霉病": (180, 0, 180),
            "Septoria_leaf_spot": (255, 140, 0),
            "斑枯病": (255, 140, 0),
        }

        for det in detections:
            bbox = det["bbox"]
            x1, y1, x2, y2 = map(int, bbox)
            label_text = f"{det['label']} {det['confidence']:.0%}"
            source = det.get("source", "")

            # 用对应颜色
            color = class_colors.get(det.get("label_en", ""),
                                     class_colors.get(det["label"], (0, 100, 255)))

            # 画框
            thickness = 3 if det.get("source") == "CNN_v2_trained" else 2
            cv2.rectangle(img_array, (x1, y1), (x2, y2), color, thickness)

            # 画标签背景
            (label_w, label_h), baseline = cv2.getTextSize(
                label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
            )
            cv2.rectangle(img_array,
                          (x1, y1 - label_h - 12),
                          (x1 + label_w + 8, y1),
                          color, -1)

            # 画标签文字
            cv2.putText(img_array, label_text,
                        (x1 + 4, y1 - 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        (255, 255, 255), 2)

            # 标注模型来源
            if source:
                cv2.putText(img_array, f"[{source}]",
                            (x1 + 4, y1 + 18),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                            color, 1)

        img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
        return Image.fromarray(img_array)
