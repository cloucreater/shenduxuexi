import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
import json
import os
from collections import defaultdict

class DiseaseTreatmentModel(nn.Module):
    def __init__(self, input_size=16, hidden_size=64, output_size=6):
        super(DiseaseTreatmentModel, self).__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.2)
        )
        self.treatment_head = nn.Sequential(
            nn.Linear(hidden_size // 2, output_size),
            nn.Softmax(dim=1)
        )
        self.severity_head = nn.Sequential(
            nn.Linear(hidden_size // 2, 3),
            nn.Softmax(dim=1)
        )

    def forward(self, x):
        encoded = self.encoder(x)
        treatment = self.treatment_head(encoded)
        severity = self.severity_head(encoded)
        return treatment, severity

class EffectEvaluationModel(nn.Module):
    def __init__(self, input_size=8, hidden_size=32):
        super(EffectEvaluationModel, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.BatchNorm1d(hidden_size),
            nn.Dropout(0.3),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Linear(hidden_size // 2, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.network(x)

class VideoAnalysisModel(nn.Module):
    def __init__(self, feature_size=256, hidden_size=128):
        super(VideoAnalysisModel, self).__init__()
        self.temporal_conv = nn.Sequential(
            nn.Conv1d(feature_size, hidden_size, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(hidden_size, hidden_size // 2, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(1)
        )
        self.classifier = nn.Sequential(
            nn.Linear(hidden_size // 2, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 6),
            nn.Softmax(dim=1)
        )

    def forward(self, x):
        features = self.temporal_conv(x)
        features = features.squeeze(-1)
        output = self.classifier(features)
        return output

class DeepLearningEngine:
    def __init__(self):
        self.treatment_model = None
        self.evaluation_model = None
        self.video_model = None
        self._load_models()

    def _load_models(self):
        """加载训练好的模型权重"""
        # 模型文件目录
        model_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "models"
        )

        try:
            # ━━━ 治疗方案模型 ━━━
            self.treatment_model = DiseaseTreatmentModel()
            treatment_path = os.path.join(model_dir, "best_treatment_model.pth")
            if os.path.exists(treatment_path):
                state = torch.load(treatment_path, map_location="cpu", weights_only=True)
                # 只加载匹配的键（避免 strict=False 可能漏掉的问题）
                model_state = self.treatment_model.state_dict()
                matched = {k: v for k, v in state.items() if k in model_state}
                model_state.update(matched)
                self.treatment_model.load_state_dict(model_state)
                print(f"[DEEP] [OK] 治疗方案模型已加载 ({len(matched)}/{len(state)} 参数匹配)")
            else:
                print(f"[DEEP] [WARN] 治疗方案模型文件不存在: {treatment_path}")
            self.treatment_model.eval()

            # ━━━ 效果评估模型 ━━━
            self.evaluation_model = EffectEvaluationModel()
            eval_path = os.path.join(model_dir, "best_evaluation_model.pth")
            if os.path.exists(eval_path):
                state = torch.load(eval_path, map_location="cpu", weights_only=True)
                # 修复键名: saved "net.X" -> model "network.X"
                remapped = {}
                for k, v in state.items():
                    new_k = k.replace("net.", "network.")
                    remapped[new_k] = v
                model_state = self.evaluation_model.state_dict()
                matched = {k: v for k, v in remapped.items() if k in model_state}
                model_state.update(matched)
                self.evaluation_model.load_state_dict(model_state)
                print(f"[DEEP] [OK] 效果评估模型已加载 ({len(matched)}/{len(remapped)} 参数匹配)")
            else:
                print(f"[DEEP] [WARN] 效果评估模型文件不存在: {eval_path}")
            self.evaluation_model.eval()

            # ━━━ 视频分析模型 ━━━
            self.video_model = VideoAnalysisModel()
            self.video_model.eval()
            print("[DEEP] [OK] 视频分析模型已初始化 (随机权重)")

        except Exception as e:
            print(f"[DEEP] [ERROR] 模型加载失败: {e}")
            import traceback
            traceback.print_exc()
            # 创建未训练的模型作为回退
            self.treatment_model = DiseaseTreatmentModel()
            self.treatment_model.eval()
            self.evaluation_model = EffectEvaluationModel()
            self.evaluation_model.eval()
            self.video_model = VideoAnalysisModel()
            self.video_model.eval()

    def encode_treatment_features(self, disease: str, severity: str, crop_type: str, 
                                   weather: Dict, env_conditions: Dict) -> torch.Tensor:
        disease_map = {
            "叶斑病": [1, 0, 0, 0, 0, 0],
            "锈病": [0, 1, 0, 0, 0, 0],
            "白粉病": [0, 0, 1, 0, 0, 0],
            "早疫病": [0, 0, 0, 1, 0, 0],
            "晚疫病": [0, 0, 0, 0, 1, 0],
            "健康": [0, 0, 0, 0, 0, 1]
        }

        severity_map = {
            "light": [1, 0, 0],
            "medium": [0, 1, 0],
            "severe": [0, 0, 1]
        }

        crop_map = {
            "番茄": [1, 0, 0],
            "黄瓜": [0, 1, 0],
            "其他": [0, 0, 1]
        }

        disease_vec = disease_map.get(disease, [0, 0, 0, 0, 0, 1])
        severity_vec = severity_map.get(severity, [0, 1, 0])
        crop_vec = crop_map.get(crop_type, [0, 0, 1])

        weather_temp = weather.get("temperature", 25) / 40.0
        weather_humidity = weather.get("humidity", 60) / 100.0
        env_ph = env_conditions.get("ph", 7.0) / 14.0
        env_moisture = env_conditions.get("soil_moisture", 50) / 100.0

        features = disease_vec + severity_vec + crop_vec + [weather_temp, weather_humidity, env_ph, env_moisture]
        return torch.tensor([features], dtype=torch.float32)

    def generate_smart_treatment(self, disease: str, severity: str, crop_type: str,
                                  weather: Dict = None, env_conditions: Dict = None) -> Dict[str, Any]:
        if weather is None:
            weather = {"temperature": 25, "humidity": 60}
        if env_conditions is None:
            env_conditions = {"ph": 7.0, "soil_moisture": 50}

        features = self.encode_treatment_features(disease, severity, crop_type, weather, env_conditions)

        # ━━━ 使用训练好的模型进行推理 ━━━
        model_prediction = None
        if self.treatment_model is not None:
            try:
                with torch.no_grad():
                    treatment_out, severity_out = self.treatment_model(features)
                treatment_probs = treatment_out[0].tolist()
                severity_probs = severity_out[0].tolist()
                pred_treatment_idx = treatment_probs.index(max(treatment_probs))
                pred_severity_idx = severity_probs.index(max(severity_probs))

                treatment_types = ["化学药剂", "生物防治", "物理防治", "综合防治", "预防措施", "无需处理"]
                severity_levels = ["轻度", "中度", "重度"]

                model_prediction = {
                    "recommended_type": treatment_types[pred_treatment_idx] if pred_treatment_idx < len(treatment_types) else "综合防治",
                    "confidence": round(max(treatment_probs), 4),
                    "severity_assessment": severity_levels[pred_severity_idx] if pred_severity_idx < len(severity_levels) else "中度",
                    "severity_confidence": round(max(severity_probs), 4),
                    "treatment_probs": {treatment_types[i]: round(p, 4) for i, p in enumerate(treatment_probs) if i < len(treatment_types)},
                }
                print(f"[DEEP] 模型推理: 推荐方案={model_prediction['recommended_type']} ({model_prediction['confidence']:.2%}), "
                      f"严重度评估={model_prediction['severity_assessment']}")
            except Exception as e:
                print(f"[DEEP] 模型推理出错: {e}")
                model_prediction = None

        treatment_recommendations = self._get_treatment_recommendations(disease, severity, crop_type)
        ai_insights = self._generate_ai_insights(disease, severity, weather, env_conditions)

        # 将模型预测结果融入 AI 洞察
        if model_prediction and model_prediction["confidence"] > 0.3:
            ai_insights.insert(0, f"AI模型推荐采用{model_prediction['recommended_type']}方案（置信度{model_prediction['confidence']:.1%}）")
            treatment_recommendations["model_analysis"] = model_prediction

        return {
            "disease": disease,
            "severity": severity,
            "crop_type": crop_type,
            "recommendations": treatment_recommendations,
            "ai_insights": ai_insights,
            "weather_analysis": self._analyze_weather_impact(weather, disease),
            "environment_analysis": self._analyze_environment_impact(env_conditions)
        }

    def _get_treatment_recommendations(self, disease: str, severity: str, crop_type: str) -> Dict:
        from app.ml.llm import TREATMENT_DATABASE, DEFAULT_TREATMENT

        treatment_db = TREATMENT_DATABASE
        disease_data = treatment_db.get(disease, {})

        if not disease_data:
            return DEFAULT_TREATMENT

        severity_data = disease_data.get(severity, disease_data.get("light", DEFAULT_TREATMENT))

        enhanced_tips = severity_data["farming_tips"].copy()
        if crop_type == "番茄":
            enhanced_tips.append("番茄需注意整枝打叉，保持通风")
        elif crop_type == "黄瓜":
            enhanced_tips.append("黄瓜需注意控制棚内湿度，避免霜霉病并发")

        return {
            "pesticides": severity_data["pesticides"],
            "farming_tips": enhanced_tips,
            "safety_interval": severity_data["safety_interval"]
        }

    def _generate_ai_insights(self, disease: str, severity: str, weather: Dict, env: Dict) -> List[str]:
        insights = []

        temp = weather.get("temperature", 25)
        humidity = weather.get("humidity", 60)

        if disease == "叶斑病":
            if humidity > 70:
                insights.append("高湿度环境有利于叶斑病菌繁殖，建议加强通风")
            if temp > 28:
                insights.append("高温高湿环境加速病情发展，需及时防治")

        elif disease == "锈病":
            if temp < 20 and humidity > 80:
                insights.append("低温高湿是锈病爆发的主要条件，建议提前预防")

        elif disease == "白粉病":
            if humidity < 50 and temp > 25:
                insights.append("干燥高温环境易诱发白粉病，需注意控温控湿")

        if severity == "severe":
            insights.append("病情严重，建议采用综合防治措施")
            insights.append("可考虑轮作换茬，减少病原积累")

        ph = env.get("ph", 7.0)
        if ph < 6.0:
            insights.append("土壤偏酸，建议施用石灰调节pH值")
        elif ph > 7.5:
            insights.append("土壤偏碱，建议施用硫磺粉调节pH值")

        return insights

    def _analyze_weather_impact(self, weather: Dict, disease: str) -> Dict:
        temp = weather.get("temperature", 25)
        humidity = weather.get("humidity", 60)

        risk_level = "低"
        if humidity > 70 or temp > 30:
            risk_level = "高"
        elif humidity > 60 or temp > 25:
            risk_level = "中"

        return {
            "temperature": temp,
            "humidity": humidity,
            "risk_level": risk_level,
            "suggestion": f"当前天气条件下病害风险为{risk_level}，建议{'加强防治' if risk_level == '高' else '正常监测'}"
        }

    def _analyze_environment_impact(self, env: Dict) -> Dict:
        ph = env.get("ph", 7.0)
        moisture = env.get("soil_moisture", 50)

        ph_status = "适宜" if 6.5 <= ph <= 7.5 else ("偏酸" if ph < 6.5 else "偏碱")
        moisture_status = "适宜" if 50 <= moisture <= 70 else ("偏干" if moisture < 50 else "偏湿")

        return {
            "ph": ph,
            "ph_status": ph_status,
            "soil_moisture": moisture,
            "moisture_status": moisture_status,
            "suggestion": f"土壤pH值{ph_status}，湿度{moisture_status}，建议{'调节土壤环境' if ph_status != '适宜' or moisture_status != '适宜' else '保持当前管理'}"
        }

    def evaluate_treatment_effect(self, before_data: List[Dict], after_data: List[Dict], 
                                   treatment_info: Dict) -> Dict[str, Any]:
        before_stats = self._calculate_detection_stats(before_data)
        after_stats = self._calculate_detection_stats(after_data)

        effectiveness = self._calculate_effectiveness(before_stats, after_stats)
        improvement_rate = self._calculate_improvement_rate(before_stats, after_stats)

        # ━━━ 使用训练好的评估模型进行推理 ━━━
        model_score = None
        if self.evaluation_model is not None and before_data and after_data:
            try:
                import numpy as np
                before_count = before_stats["disease_count"]
                after_count = after_stats["disease_count"]
                reduction_rate = effectiveness["disease_reduction"]
                severity_val = 1.0
                treatment_type_val = 1.0
                time_interval = 7.0
                confidence = before_stats["avg_confidence"] if before_stats["avg_confidence"] > 0 else 0.8
                env_factor = 0.5

                eval_features = torch.tensor([[
                    before_count / 100.0, after_count / 100.0, reduction_rate / 100.0,
                    severity_val / 3.0, treatment_type_val / 3.0,
                    time_interval / 30.0, confidence, env_factor
                ]], dtype=torch.float32)

                with torch.no_grad():
                    model_output = self.evaluation_model(eval_features)
                model_score = round(float(model_output[0][0]) * 100, 2)
                print(f"[DEEP] 评估模型推理: 效果评分={model_score}")
            except Exception as e:
                print(f"[DEEP] 评估模型推理出错: {e}")
                model_score = None

        evaluation_score = self._calculate_evaluation_score(effectiveness, improvement_rate, treatment_info)
        if model_score is not None:
            evaluation_score = round((evaluation_score + model_score) / 2, 2)

        recommendations = self._generate_evaluation_recommendations(evaluation_score, effectiveness)

        return {
            "before_stats": before_stats,
            "after_stats": after_stats,
            "effectiveness": effectiveness,
            "improvement_rate": improvement_rate,
            "evaluation_score": evaluation_score,
            "evaluation_level": self._get_evaluation_level(evaluation_score),
            "recommendations": recommendations,
            "treatment_analysis": self._analyze_treatment_impact(before_stats, after_stats, treatment_info)
        }

    def _calculate_detection_stats(self, detection_data: List[Dict]) -> Dict:
        if not detection_data:
            return {
                "total_detections": 0,
                "disease_count": 0,
                "healthy_count": 0,
                "avg_confidence": 0,
                "disease_distribution": {},
                "severity_distribution": {"light": 0, "medium": 0, "severe": 0}
            }

        total = len(detection_data)
        disease_count = sum(1 for d in detection_data if d.get("label_en") != "healthy")
        healthy_count = total - disease_count

        confidences = [d.get("confidence", 0) for d in detection_data]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        disease_dist = defaultdict(int)
        for d in detection_data:
            label = d.get("label", "未知")
            if label != "健康":
                disease_dist[label] += 1

        severity_dist = {"light": 0, "medium": 0, "severe": 0}
        for d in detection_data:
            conf = d.get("confidence", 0)
            if conf > 0.8:
                severity_dist["severe"] += 1
            elif conf > 0.5:
                severity_dist["medium"] += 1
            else:
                severity_dist["light"] += 1

        return {
            "total_detections": total,
            "disease_count": disease_count,
            "healthy_count": healthy_count,
            "avg_confidence": round(avg_confidence, 4),
            "disease_distribution": dict(disease_dist),
            "severity_distribution": severity_dist
        }

    def _calculate_effectiveness(self, before: Dict, after: Dict) -> Dict:
        disease_reduction = 0
        if before["disease_count"] > 0:
            disease_reduction = ((before["disease_count"] - after["disease_count"]) / 
                               before["disease_count"]) * 100

        healthy_increase = 0
        if before["healthy_count"] > 0:
            healthy_increase = ((after["healthy_count"] - before["healthy_count"]) / 
                              before["healthy_count"]) * 100

        return {
            "disease_reduction": round(disease_reduction, 2),
            "healthy_increase": round(healthy_increase, 2),
            "overall_effective": disease_reduction > 30
        }

    def _calculate_improvement_rate(self, before: Dict, after: Dict) -> Dict:
        improvements = {}
        for disease in before["disease_distribution"].keys():
            before_count = before["disease_distribution"].get(disease, 0)
            after_count = after["disease_distribution"].get(disease, 0)

            if before_count > 0:
                improvement = ((before_count - after_count) / before_count) * 100
                improvements[disease] = round(improvement, 2)
            else:
                improvements[disease] = 0

        return improvements

    def _calculate_evaluation_score(self, effectiveness: Dict, improvement_rate: Dict, 
                                     treatment_info: Dict) -> float:
        base_score = effectiveness["disease_reduction"] * 0.6

        avg_improvement = 0
        if improvement_rate:
            avg_improvement = sum(improvement_rate.values()) / len(improvement_rate)

        improvement_score = avg_improvement * 0.3

        severity_bonus = 0
        severity = treatment_info.get("severity", "medium")
        if severity == "severe":
            severity_bonus = 10
        elif severity == "medium":
            severity_bonus = 5

        total_score = base_score + improvement_score + severity_bonus
        return round(min(100, max(0, total_score)), 2)

    def _get_evaluation_level(self, score: float) -> str:
        if score >= 80:
            return "优秀"
        elif score >= 60:
            return "良好"
        elif score >= 40:
            return "一般"
        else:
            return "较差"

    def _generate_evaluation_recommendations(self, score: float, effectiveness: Dict) -> List[str]:
        recommendations = []

        if score >= 80:
            recommendations.append("防治效果显著，建议继续使用当前方案")
            recommendations.append("可适当延长防治间隔，降低成本")
        elif score >= 60:
            recommendations.append("防治效果良好，建议维持当前方案")
            recommendations.append("注意观察病情变化，及时调整")
        elif score >= 40:
            recommendations.append("防治效果一般，建议优化防治方案")
            recommendations.append("可考虑增加施药频次或更换药剂")
        else:
            recommendations.append("防治效果较差，建议重新评估方案")
            recommendations.append("建议咨询专业农技人员")

        if effectiveness["disease_reduction"] < 20:
            recommendations.append("病害减少不明显，需检查施药质量和时机")

        return recommendations

    def _analyze_treatment_impact(self, before: Dict, after: Dict, treatment: Dict) -> Dict:
        analysis = {
            "most_improved": None,
            "least_improved": None,
            "severity_change": {},
            "treatment_suitability": "中等"
        }

        before_severity = before["severity_distribution"]
        after_severity = after["severity_distribution"]

        analysis["severity_change"] = {
            "severe_reduction": before_severity["severe"] - after_severity["severe"],
            "medium_reduction": before_severity["medium"] - after_severity["medium"],
            "light_reduction": before_severity["light"] - after_severity["light"]
        }

        total_reduction = sum(analysis["severity_change"].values())
        if total_reduction > 5:
            analysis["treatment_suitability"] = "优秀"
        elif total_reduction > 2:
            analysis["treatment_suitability"] = "良好"

        return analysis

    def analyze_historical_comparison(self, period1_data: List[Dict], period2_data: List[Dict],
                                       comparison_type: str = "disease") -> Dict[str, Any]:
        period1_stats = self._calculate_detection_stats(period1_data)
        period2_stats = self._calculate_detection_stats(period2_data)

        trends = self._analyze_trends(period1_stats, period2_stats)

        patterns = self._detect_patterns(period1_data, period2_data)

        predictions = self._generate_predictions(trends, patterns)

        return {
            "period1_stats": period1_stats,
            "period2_stats": period2_stats,
            "trends": trends,
            "patterns": patterns,
            "predictions": predictions,
            "comparison_summary": self._generate_comparison_summary(trends, patterns)
        }

    def _analyze_trends(self, stats1: Dict, stats2: Dict) -> Dict:
        trends = {
            "disease_trend": "stable",
            "severity_trend": "stable",
            "confidence_trend": "stable",
            "changes": {}
        }

        disease_change = stats2["disease_count"] - stats1["disease_count"]
        if disease_change > 0:
            trends["disease_trend"] = "increasing"
        elif disease_change < 0:
            trends["disease_trend"] = "decreasing"

        trends["changes"]["disease_count_change"] = disease_change
        trends["changes"]["disease_change_rate"] = round(
            (disease_change / stats1["disease_count"] * 100) if stats1["disease_count"] > 0 else 0, 2
        )

        conf_change = stats2["avg_confidence"] - stats1["avg_confidence"]
        if conf_change > 0.05:
            trends["confidence_trend"] = "improving"
        elif conf_change < -0.05:
            trends["confidence_trend"] = "declining"

        trends["changes"]["confidence_change"] = round(conf_change, 4)

        return trends

    def _detect_patterns(self, data1: List[Dict], data2: List[Dict]) -> Dict:
        patterns = {
            "seasonal_patterns": [],
            "disease_hotspots": [],
            "recurring_diseases": [],
            "anomalies": []
        }

        all_data = data1 + data2
        disease_counts = defaultdict(int)
        for d in all_data:
            if d.get("label_en") != "healthy":
                disease_counts[d.get("label", "未知")] += 1

        sorted_diseases = sorted(disease_counts.items(), key=lambda x: x[1], reverse=True)
        patterns["disease_hotspots"] = [
            {"disease": name, "count": count} for name, count in sorted_diseases[:3]
        ]

        for disease, count in sorted_diseases:
            if count > 2:
                patterns["recurring_diseases"].append(disease)

        return patterns

    def _generate_predictions(self, trends: Dict, patterns: Dict) -> Dict:
        predictions = {
            "short_term": [],
            "medium_term": [],
            "risk_assessment": "中等"
        }

        if trends["disease_trend"] == "increasing":
            predictions["short_term"].append("预计短期内病害数量将继续增加")
            predictions["risk_assessment"] = "高"
        elif trends["disease_trend"] == "decreasing":
            predictions["short_term"].append("预计短期内病害数量将继续减少")
            predictions["risk_assessment"] = "低"
        else:
            predictions["short_term"].append("预计短期内病害数量将保持稳定")

        if patterns["disease_hotspots"]:
            top_disease = patterns["disease_hotspots"][0]["disease"]
            predictions["medium_term"].append(f"需重点关注{top_disease}的防控")

        if patterns["recurring_diseases"]:
            predictions["medium_term"].append("建议制定长期防治计划，针对反复出现的病害")

        return predictions

    def _generate_comparison_summary(self, trends: Dict, patterns: Dict) -> str:
        trend_desc = {
            "increasing": "上升",
            "decreasing": "下降",
            "stable": "稳定"
        }

        summary = f"对比分析显示，病害数量呈{trend_desc.get(trends['disease_trend'], '稳定')}趋势"

        if patterns["disease_hotspots"]:
            top_disease = patterns["disease_hotspots"][0]["disease"]
            summary += f"，{top_disease}为主要病害"

        return summary

    def analyze_video_detection(self, video_frames: List[np.ndarray], 
                                 frame_rate: int = 30) -> Dict[str, Any]:
        if not video_frames:
            return {
                "total_frames": 0,
                "disease_frames": 0,
                "disease_rate": 0,
                "temporal_analysis": {},
                "spatial_analysis": {},
                "recommendations": []
            }

        temporal_results = self._analyze_temporal_patterns(video_frames, frame_rate)
        spatial_results = self._analyze_spatial_distribution(video_frames)

        combined_analysis = self._combine_analyses(temporal_results, spatial_results)

        return {
            "total_frames": len(video_frames),
            "disease_frames": temporal_results["disease_frame_count"],
            "disease_rate": temporal_results["disease_rate"],
            "temporal_analysis": temporal_results,
            "spatial_analysis": spatial_results,
            "combined_analysis": combined_analysis,
            "recommendations": self._generate_video_recommendations(combined_analysis)
        }

    def _analyze_temporal_patterns(self, frames: List[np.ndarray], frame_rate: int) -> Dict:
        frame_interval = max(1, len(frames) // 10)
        sampled_frames = frames[::frame_interval]

        disease_progression = []
        disease_frame_count = 0

        for i, frame in enumerate(sampled_frames):
            frame_diseases = self._detect_frame_diseases(frame)
            disease_count = len(frame_diseases)

            if disease_count > 0:
                disease_frame_count += 1

            disease_progression.append({
                "frame_index": i * frame_interval,
                "timestamp": i * frame_interval / frame_rate,
                "disease_count": disease_count,
                "diseases": frame_diseases
            })

        disease_rate = disease_frame_count / len(sampled_frames) if sampled_frames else 0

        progression_trend = self._analyze_progression_trend(disease_progression)

        return {
            "disease_frame_count": disease_frame_count,
            "disease_rate": round(disease_rate, 4),
            "disease_progression": disease_progression,
            "progression_trend": progression_trend,
            "peak_disease_time": self._find_peak_disease_time(disease_progression)
        }

    def _detect_frame_diseases(self, frame: np.ndarray) -> List[Dict]:
        diseases = []

        frame_height, frame_width = frame.shape[:2]

        center_region = {
            "x": frame_width // 4,
            "y": frame_height // 4,
            "width": frame_width // 2,
            "height": frame_height // 2
        }

        diseases.append({
            "label": "模拟病害",
            "confidence": 0.75,
            "location": "center",
            "severity": "medium"
        })

        return diseases

    def _analyze_progression_trend(self, progression: List[Dict]) -> str:
        if len(progression) < 3:
            return "insufficient_data"

        first_half = progression[:len(progression)//2]
        second_half = progression[len(progression)//2:]

        first_avg = sum(p["disease_count"] for p in first_half) / len(first_half)
        second_avg = sum(p["disease_count"] for p in second_half) / len(second_half)

        if second_avg > first_avg * 1.2:
            return "worsening"
        elif second_avg < first_avg * 0.8:
            return "improving"
        else:
            return "stable"

    def _find_peak_disease_time(self, progression: List[Dict]) -> Dict:
        if not progression:
            return {"frame_index": -1, "timestamp": -1, "disease_count": 0}

        peak_frame = max(progression, key=lambda x: x["disease_count"])
        return peak_frame

    def _analyze_spatial_distribution(self, frames: List[np.ndarray]) -> Dict:
        if not frames:
            return {"hotspots": [], "distribution": "uniform"}

        frame_height, frame_width = frames[0].shape[:2]

        regions = {
            "top_left": 0,
            "top_right": 0,
            "bottom_left": 0,
            "bottom_right": 0,
            "center": 0
        }

        for frame in frames:
            h, w = frame.shape[:2]
            regions["center"] += 1

        total = sum(regions.values())
        distribution = {}
        for region, count in regions.items():
            distribution[region] = round(count / total, 4) if total > 0 else 0

        hotspots = sorted(distribution.items(), key=lambda x: x[1], reverse=True)[:2]

        return {
            "hotspots": [{"region": r, "intensity": i} for r, i in hotspots],
            "distribution": "concentrated" if hotspots[0][1] > 0.5 else "dispersed",
            "region_distribution": distribution
        }

    def _combine_analyses(self, temporal: Dict, spatial: Dict) -> Dict:
        severity = "low"
        if temporal["disease_rate"] > 0.7:
            severity = "high"
        elif temporal["disease_rate"] > 0.3:
            severity = "medium"

        urgency = "low"
        if temporal["progression_trend"] == "worsening" and severity in ["medium", "high"]:
            urgency = "high"
        elif temporal["progression_trend"] in ["worsening", "stable"] and severity == "medium":
            urgency = "medium"

        return {
            "overall_severity": severity,
            "urgency_level": urgency,
            "primary_concerns": self._identify_primary_concerns(temporal, spatial),
            "action_priority": self._determine_action_priority(severity, urgency)
        }

    def _identify_primary_concerns(self, temporal: Dict, spatial: Dict) -> List[str]:
        concerns = []

        if temporal["progression_trend"] == "worsening":
            concerns.append("病害呈加重趋势，需立即采取行动")

        if temporal["disease_rate"] > 0.5:
            concerns.append(f"病害发生率高达{temporal['disease_rate']*100:.1f}%，覆盖范围广")

        if spatial["distribution"] == "concentrated":
            concerns.append("病害呈集中分布，可能存在传染源")

        return concerns

    def _determine_action_priority(self, severity: str, urgency: str) -> str:
        if urgency == "high":
            return "立即处理"
        elif urgency == "medium":
            return "优先处理"
        elif severity == "high":
            return "尽快处理"
        else:
            return "正常处理"

    def _generate_video_recommendations(self, analysis: Dict) -> List[str]:
        recommendations = []

        if analysis["urgency_level"] == "high":
            recommendations.append("建议立即进行全田检查和防治")
            recommendations.append("考虑使用强效药剂，缩短施药间隔")
        elif analysis["urgency_level"] == "medium":
            recommendations.append("建议在未来3-5天内进行防治")
            recommendations.append("加强监测，密切关注病情变化")
        else:
            recommendations.append("建议按常规计划进行防治")
            recommendations.append("保持正常监测频次")

        for concern in analysis["primary_concerns"]:
            if "加重趋势" in concern:
                recommendations.append("需分析病情加重原因，调整防治策略")
            elif "集中分布" in concern:
                recommendations.append("重点处理病害集中区域，防止扩散")

        return recommendations

deep_learning_engine = DeepLearningEngine()