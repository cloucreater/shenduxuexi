import requests

# 首先登录获取token
login_url = "http://localhost:8000/api/auth/login"
login_data = {
    "username": "admin",
    "password": "admin",
    "captcha": "1234"  # 测试环境任意4位字符
}

print("正在登录...")
login_response = requests.post(login_url, json=login_data)
print(f"登录状态码: {login_response.status_code}")
print(f"登录响应: {login_response.text}")

if login_response.status_code == 200:
    token = login_response.json().get("token")
    print(f"获取到token: {token}")
    
    # 测试头像上传
    avatar_url = "http://localhost:8000/api/auth/avatar"
    
    # 创建一个测试图片文件
    test_image_path = "test_avatar.jpg"
    with open(test_image_path, "wb") as f:
        # 写入一个简单的JPEG文件头
        f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x03\x02\x02\x03\x02\x02\x03\x03\x03\x03\x04\x03\x03\x04\x05\x08\x05\x05\x04\x04\x05\n\x07\x07\x06\x08\x0c\n\x0c\x0c\x0b\n\x0b\x0b\r\x0e\x12\x10\r\x0e\x11\x0e\x0b\x0b\x10\x16\x10\x11\x13\x14\x15\x15\x15\x0c\x0f\x17\x18\x16\x14\x18\x12\x14\x15\x14\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x08\x01\x01\x00\x00?\x00T\x9f\xff\xd9')
    
    try:
        with open(test_image_path, "rb") as f:
            files = {"file": ("test_avatar.jpg", f, "image/jpeg")}
            headers = {"Authorization": f"Bearer {token}"}
            
            print(f"\n正在上传头像到: {avatar_url}")
            upload_response = requests.post(avatar_url, files=files, headers=headers)
            
            print(f"上传状态码: {upload_response.status_code}")
            print(f"上传响应: {upload_response.text}")
            
            if upload_response.status_code == 200:
                print("✅ 头像上传成功！")
            else:
                print("❌ 头像上传失败！")
                
    except Exception as e:
        print(f"上传出错: {e}")
    finally:
        import os
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
else:
    print("❌ 登录失败！")