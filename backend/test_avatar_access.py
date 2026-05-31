import requests

# 测试头像URL访问
avatar_url = "http://localhost:8000/uploads/avatars/avatar_1_7a5b22bb.jpg"
print(f"正在访问头像URL: {avatar_url}")

try:
    response = requests.get(avatar_url)
    print(f"状态码: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"Content-Length: {response.headers.get('Content-Length')}")
    
    if response.status_code == 200:
        print("✅ 头像URL可以正常访问")
    else:
        print(f"❌ 头像URL访问失败: {response.status_code}")
        
except Exception as e:
    print(f"❌ 访问出错: {e}")

# 测试用户信息API
me_url = "http://localhost:8000/api/auth/me"
print(f"\n正在获取用户信息: {me_url}")

try:
    # 先登录获取token
    login_url = "http://localhost:8000/api/auth/login"
    login_data = {
        "username": "admin",
        "password": "admin",
        "captcha": "1234"
    }
    login_response = requests.post(login_url, json=login_data)
    token = login_response.json().get("token")
    
    headers = {"Authorization": f"Bearer {token}"}
    me_response = requests.get(me_url, headers=headers)
    
    print(f"状态码: {me_response.status_code}")
    print(f"用户信息: {me_response.json()}")
    
except Exception as e:
    print(f"❌ 获取用户信息出错: {e}")