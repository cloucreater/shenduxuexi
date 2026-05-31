from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.ml.llm import TreatmentGenerator
from app.ml.deep_model import deep_learning_engine
from fastapi.responses import StreamingResponse
import asyncio
import json

router = APIRouter()
treatment_generator = TreatmentGenerator()

class TreatmentRequest(BaseModel):
    disease_name: str
    severity: str
    crop_type: str
    weather: Optional[Dict] = None
    env_conditions: Optional[Dict] = None

class Pesticide(BaseModel):
    name: str
    concentration: str
    method: str

class Recommendations(BaseModel):
    pesticides: List[Pesticide]
    farming_tips: List[str]
    safety_interval: str

class TreatmentResponse(BaseModel):
    disease: str
    severity: str
    recommendations: Recommendations
    ai_insights: List[str]
    weather_analysis: Dict
    environment_analysis: Dict

DISEASE_NAMES_CN = {
    "leaf_spot": "叶斑病",
    "rust": "锈病",
    "powdery_mildew": "白粉病",
    "early_blight": "早疫病",
    "late_blight": "晚疫病",
    "bacterial_spot": "细菌性斑点病",
    "leaf_mold": "叶霉病",
    "septoria_leaf_spot": "斑枯病",
}

SEVERITY_MAP = {
    "轻度": "light",
    "中度": "medium",
    "重度": "severe",
    "light": "light",
    "medium": "medium",
    "severe": "severe",
}

@router.post("/generate", response_model=TreatmentResponse)
async def generate_treatment(
    request: TreatmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
        disease_cn = DISEASE_NAMES_CN.get(request.disease_name, request.disease_name)
        severity_en = SEVERITY_MAP.get(request.severity, "medium")

        result = deep_learning_engine.generate_smart_treatment(
            disease=disease_cn,
            severity=severity_en,
            crop_type=request.crop_type,
            weather=request.weather or {"temperature": 25, "humidity": 60},
            env_conditions=request.env_conditions or {"ph": 7.0, "soil_moisture": 50}
        )

        return TreatmentResponse(
            disease=result["disease"],
            severity=result["severity"],
        recommendations=Recommendations(**result["recommendations"]),
        ai_insights=result["ai_insights"],
        weather_analysis=result["weather_analysis"],
environment_analysis=result["environment_analysis"]
    )


# ── SSE 流式生成接口 ──

@router.post("/generate/stream")
async def generate_treatment_stream(
    request: TreatmentRequest,
    current_user: User = Depends(get_current_user)
):
    disease_cn = DISEASE_NAMES_CN.get(request.disease_name, request.disease_name)
    severity_en = SEVERITY_MAP.get(request.severity, "medium")

    async def event_stream():
        # 阶段1: 分析中
        yield f"data: {json.dumps({'type': 'status', 'content': '正在分析病害特征...', 'progress': 10})}\n\n"
        await asyncio.sleep(0.5)

        # 阶段2: 生成方案
        result = deep_learning_engine.generate_smart_treatment(
            disease=disease_cn,
            severity=severity_en,
            crop_type=request.crop_type,
            weather=request.weather or {"temperature": 25, "humidity": 60},
            env_conditions=request.env_conditions or {"ph": 7.0, "soil_moisture": 50}
        )

        yield f"data: {json.dumps({'type': 'status', 'content': 'AI正在生成防治方案...', 'progress': 40})}\n\n"
        await asyncio.sleep(0.3)

        # 流式输出药剂推荐
        pesticides = result.get("recommendations", {}).get("pesticides", [])
        for i, p in enumerate(pesticides):
            chunk = f"**推荐药剂 {i+1}：{p['name']}**  \n用量：{p.get('concentration','按说明使用')}  \n方法：{p.get('method','叶面喷雾')}  \n\n"
            yield f"data: {json.dumps({'type': 'text', 'content': chunk, 'progress': 40 + i * 10})}\n\n"
            await asyncio.sleep(0.4)

        # 流式输出AI洞察
        insights = result.get("ai_insights", [])
        yield f"data: {json.dumps({'type': 'status', 'content': '生成AI分析建议...', 'progress': 70})}\n\n"
        await asyncio.sleep(0.3)
        for insight in insights:
            yield f"data: {json.dumps({'type': 'text', 'content': f'- {insight}\\n', 'progress': 70})}\n\n"
            await asyncio.sleep(0.3)

        # 农事建议
        tips = result.get("recommendations", {}).get("farming_tips", [])
        yield f"data: {json.dumps({'type': 'status', 'content': '整理农事管理建议...', 'progress': 85})}\n\n"
        await asyncio.sleep(0.2)
        for tip in tips:
            yield f"data: {json.dumps({'type': 'text', 'content': f'✓ {tip}\\n', 'progress': 85})}\n\n"
            await asyncio.sleep(0.2)

        # 天气与环境分析
        weather = result.get("weather_analysis", {})
        env = result.get("environment_analysis", {})
        weather_text = f"\\n**天气影响分析**：风险等级 {weather.get('risk_level','中')}，{weather.get('suggestion','')}\\n"
        env_text = f"**土壤环境分析**：pH {env.get('ph','7.0')}（{env.get('ph_status','适宜')}），湿度 {env.get('soil_moisture','50')}（{env.get('moisture_status','适宜')}）\\n"
        yield f"data: {json.dumps({'type': 'text', 'content': weather_text + env_text, 'progress': 95})}\n\n"
        await asyncio.sleep(0.3)

        # 完成
        safety = result.get("recommendations", {}).get("safety_interval", "7天")
        yield f"data: {json.dumps({'type': 'text', 'content': f'\\n---\\n安全间隔期：{safety}\\n'})}\n\n"
        yield f"data: {json.dumps({'type': 'complete', 'content': '方案生成完成！', 'progress': 100})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )