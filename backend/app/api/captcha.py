from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
import io
import random
import base64

router = APIRouter()

# 验证码存储（生产环境应使用 Redis）
captcha_store = {}

def generate_captcha_text(length: int = 4) -> str:
    """生成随机验证码文本"""
    chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789'
    return ''.join(random.choice(chars) for _ in range(length))

def generate_simple_captcha(text: str) -> bytes:
    """生成简单的验证码SVG图片"""
    # 创建简单的SVG验证码
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="120" height="40">
        <rect width="120" height="40" fill="#ffffff"/>
        <text x="15" y="28" font-size="20" fill="#1a1a1a" font-family="Arial, sans-serif" font-weight="bold">{text}</text>
        <line x1="0" y1="10" x2="120" y2="30" stroke="#cccccc" stroke-width="1"/>
        <line x1="0" y1="30" x2="120" y2="10" stroke="#cccccc" stroke-width="1"/>
        <circle cx="10" cy="10" r="2" fill="#666666" opacity="0.4"/>
        <circle cx="30" cy="35" r="1.5" fill="#666666" opacity="0.4"/>
        <circle cx="60" cy="5" r="1" fill="#666666" opacity="0.4"/>
        <circle cx="90" cy="25" r="2" fill="#666666" opacity="0.4"/>
        <circle cx="110" cy="5" r="1.5" fill="#666666" opacity="0.4"/>
    </svg>'''
    return svg.encode('utf-8')

@router.get("/captcha")
async def get_captcha():
    """获取验证码图片"""
    captcha_text = generate_captcha_text()
    svg_bytes = generate_simple_captcha(captcha_text)
    
    # 存储验证码（有效期5分钟）
    import time
    captcha_store[captcha_text.lower()] = time.time() + 300
    
    return Response(content=svg_bytes, media_type="image/svg+xml", headers={
        "X-Captcha-Text": captcha_text  # 用于调试
    })

def validate_captcha(captcha: str) -> bool:
    """验证验证码"""
    if not captcha:
        return False
    
    captcha = captcha.lower()
    import time
    current_time = time.time()
    
    # 调试：打印所有存储的验证码
    print(f"[DEBUG] Validating captcha: {captcha}, stored: {list(captcha_store.keys())}")
    
    if captcha in captcha_store:
        if captcha_store[captcha] > current_time:
            del captcha_store[captcha]  # 验证成功后立即删除
            print(f"[DEBUG] Captcha valid")
            return True
        else:
            del captcha_store[captcha]  # 过期删除
            print(f"[DEBUG] Captcha expired")
    
    print(f"[DEBUG] Captcha invalid")
    return False