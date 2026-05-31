from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import datetime
from app.api import auth, detection, dashboard, treatment, evaluation, history, knowledge, admin, captcha
from app.core.database import engine, Base, SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.ml.detector import YOLODetector
from app.ml.deep_model import deep_learning_engine
import os

Base.metadata.create_all(bind=engine)

def init_default_admin():
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                password_hash=get_password_hash("admin"),
                role="admin"
            )
            db.add(admin_user)
            db.commit()
            print("[OK] Admin account created: admin / admin")
        else:
            # 更新密码为 admin
            admin_user.password_hash = get_password_hash("admin")
            admin_user.role = "admin"
            db.commit()
            print("[OK] Admin account updated: admin / admin")
    except Exception as e:
        print(f"[ERROR] Failed to init admin: {e}")
    finally:
        db.close()

init_default_admin()

app = FastAPI(
    title="智慧农害 - 农作物病虫害检测与防治系统",
    description="基于YOLOv11与LLM的农作物病虫害检测与防治系统API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174", "http://localhost:5175", "http://127.0.0.1:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploads
uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(os.path.join(uploads_dir, "avatars"), exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

app.include_router(captcha.router, prefix="/api", tags=["验证码"])
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["数据看板"])
app.include_router(detection.router, prefix="/api/detect", tags=["检测"])
app.include_router(treatment.router, prefix="/api/treatment", tags=["防治方案"])
app.include_router(evaluation.router, prefix="/api/evaluation", tags=["效果评估"])
app.include_router(history.router, prefix="/api/history", tags=["历史记录"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["知识库"])
app.include_router(admin.router, prefix="/api/admin", tags=["管理员"])

@app.get("/")
async def root():
    return {"message": "智慧农害 API 服务运行中"}

@app.get("/health/detailed")
async def health_detailed():
    """详细健康检查"""
    checks = {"status": "healthy", "timestamp": datetime.now().isoformat(), "checks": {}}

    # 数据库检查
    try:
        db = SessionLocal()
        db.execute(db.bind.execute("SELECT 1"))
        db.close()
        checks["checks"]["database"] = {"status": "healthy"}
    except Exception as e:
        checks["checks"]["database"] = {"status": "unhealthy", "error": str(e)}
        checks["status"] = "degraded"

    # 模型检查
    try:
        detector = YOLODetector()
        cnn_ok = detector.cnn_classifier is not None
        yolo_ok = detector.yolo_model is not None
        checks["checks"]["models"] = {
            "status": "healthy" if (cnn_ok or yolo_ok) else "degraded",
            "cnn": "loaded" if cnn_ok else "not_loaded",
            "yolo": "loaded" if yolo_ok else "not_loaded",
            "deep_treatment": "loaded" if deep_learning_engine.treatment_model is not None else "not_loaded",
            "deep_evaluation": "loaded" if deep_learning_engine.evaluation_model is not None else "not_loaded",
        }
    except Exception as e:
        checks["checks"]["models"] = {"status": "unhealthy", "error": str(e)}
        checks["status"] = "degraded"

    # 磁盘检查
    try:
        models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
        if os.path.exists(models_dir):
            files = os.listdir(models_dir)
            checks["checks"]["disk"] = {
                "status": "healthy",
                "model_count": len([f for f in files if f.endswith(('.pt', '.pth'))]),
                "model_files": files
            }
        else:
            checks["checks"]["disk"] = {"status": "degraded", "error": "models directory not found"}
    except Exception as e:
        checks["checks"]["disk"] = {"status": "unhealthy", "error": str(e)}

    # 系统运行时间
    checks["version"] = "1.0.0"
    checks["uptime"] = "running"

    return checks
