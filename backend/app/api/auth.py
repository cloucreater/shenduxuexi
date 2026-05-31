from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, get_current_user
from app.models.user import User
from app.api.captcha import validate_captcha
import os
import uuid
import shutil

router = APIRouter()

# 调试模式：设为 True 可跳过验证码验证（仅开发环境使用）
DEBUG_MODE = True


class LoginRequest(BaseModel):
    username: str
    password: str
    captcha: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str | None = None
    phone: str | None = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str | None = None
    phone: str | None = None
    avatar: str | None = None
    role: str


class TokenResponse(BaseModel):
    token: str
    user: UserResponse


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    # 验证码校验
    if not DEBUG_MODE:
        if not request.captcha or len(request.captcha) < 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="请输入验证码"
            )
        if not validate_captcha(request.captcha):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="验证码错误或已过期"
            )
    else:
        # 调试模式：至少输入4个字符
        if not request.captcha or len(request.captcha) < 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="请输入验证码（测试环境输入任意4位字符即可）"
            )

    user = db.query(User).filter(User.username == request.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名不存在"
        )

    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="密码错误"
        )

    token = create_access_token(data={"sub": str(user.id)})

    return TokenResponse(
        token=token,
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            phone=user.phone,
            avatar=user.avatar,
            role=user.role
        )
    )


@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == request.username).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    if request.email:
        existing_email = db.query(User).filter(User.email == request.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )

    if request.phone:
        existing_phone = db.query(User).filter(User.phone == request.phone).first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号已被注册"
            )

    user = User(
        username=request.username,
        password_hash=get_password_hash(request.password),
        email=request.email,
        phone=request.phone,
        role="user"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(data={"sub": str(user.id)})

    return TokenResponse(
        token=token,
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            phone=user.phone,
            avatar=user.avatar,
            role=user.role
        )
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        phone=current_user.phone,
        avatar=current_user.avatar,
        role=current_user.role
    )


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str


@router.put("/password")
async def change_password(
    request: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not verify_password(request.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="原密码错误")
    if len(request.new_password) < 6:
        raise HTTPException(status_code=400, detail="新密码长度不能少于6位")
    current_user.password_hash = get_password_hash(request.new_password)
    db.commit()
    return {"message": "密码修改成功"}


class ProfileUpdateRequest(BaseModel):
    email: str | None = None
    phone: str | None = None


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    request: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if request.email is not None:
        current_user.email = request.email
    if request.phone is not None:
        current_user.phone = request.phone
    db.commit()
    db.refresh(current_user)
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        phone=current_user.phone,
        avatar=current_user.avatar,
        role=current_user.role
    )


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "avatars")
    os.makedirs(upload_dir, exist_ok=True)
    ext = os.path.splitext(file.filename or "avatar.png")[1] or ".png"
    filename = f"avatar_{current_user.id}_{uuid.uuid4().hex[:8]}{ext}"
    filepath = os.path.join(upload_dir, filename)
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    # 保存头像URL到数据库
    avatar_url = f"/uploads/avatars/{filename}"
    
    # 重新查询用户对象并更新
    user = db.query(User).filter(User.id == current_user.id).first()
    if user:
        user.avatar = avatar_url
        db.commit()
        db.refresh(user)
        print(f"头像已保存到数据库: 用户ID={user.id}, 头像URL={user.avatar}")
    else:
        print(f"错误: 找不到用户ID={current_user.id}")
    
    return {"avatar_url": avatar_url}