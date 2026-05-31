"""
CNN Disease Classifier — 基于 PlantVillage 数据集训练的病害分类模型
架构完全匹配 best_cnn_v2.pth 的 state_dict
"""
import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image
import os
from typing import Dict, Tuple, Optional

# 模型文件路径
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models")
CNN_V2_PATH = os.path.join(MODEL_DIR, "best_cnn_v2.pth")


class CNNClassifier(nn.Module):
    """
    CNN 病害分类器（与训练时架构完全一致）

    架构: 4个卷积块 → 全局平均池化 → Dropout → 全连接
    - Conv2d(3,32,3) → BN → ReLU → MaxPool
    - Conv2d(32,64,3) → BN → ReLU → MaxPool
    - Conv2d(64,128,3) → BN → ReLU → MaxPool
    - Conv2d(128,256,3) → BN → ReLU → AdaptiveAvgPool
    - Dropout(0.5) → Linear(256, 6)
    """

    CLASS_NAMES = [
        "Bacterial_spot",       # 细菌性斑点病
        "Early_blight",         # 早疫病
        "Late_blight",          # 晚疫病
        "Leaf_Mold",            # 叶霉病
        "Septoria_leaf_spot",   # 斑枯病
        "healthy",              # 健康
    ]

    CLASS_NAMES_CN = {
        "Bacterial_spot": "细菌性斑点病",
        "Early_blight": "早疫病",
        "Late_blight": "晚疫病",
        "Leaf_Mold": "叶霉病",
        "Septoria_leaf_spot": "斑枯病",
        "healthy": "健康",
    }

    CLASS_NAMES_EN = {
        "Bacterial_spot": "Bacterial Spot",
        "Early_blight": "Early Blight",
        "Late_blight": "Late Blight",
        "Leaf_Mold": "Leaf Mold",
        "Septoria_leaf_spot": "Septoria Leaf Spot",
        "healthy": "Healthy",
    }

    def __init__(self, num_classes: int = 6):
        super().__init__()

        self.features = nn.Sequential(
            # Block 1
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            # Block 2
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            # Block 3
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            # Block 4
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d(1),
        )

        self.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(256, num_classes),
        )

    def forward(self, x):
        x = self.features(x)
        x = torch.flatten(x, 1)
        x = self.classifier(x)
        return x

    # 图像预处理变换（与训练时一致）
    @staticmethod
    def get_transform():
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            ),
        ])


def load_cnn_classifier(device: str = "cpu") -> Optional[CNNClassifier]:
    """加载训练好的 CNN 分类器"""
    if not os.path.exists(CNN_V2_PATH):
        print(f"[CNN] 模型文件不存在: {CNN_V2_PATH}")
        return None

    try:
        checkpoint = torch.load(CNN_V2_PATH, map_location=device, weights_only=False)
        model = CNNClassifier(num_classes=6)
        model.load_state_dict(checkpoint["model_state_dict"])
        model.to(device)
        model.eval()

        print(f"[CNN] [OK] 已加载训练模型: best_cnn_v2.pth")
        print(f"[CNN]    类别数: {len(checkpoint['class_names'])}")
        print(f"[CNN]    验证准确率: {checkpoint.get('val_acc', 'N/A')}%")
        print(f"[CNN]    参数量: {checkpoint.get('n_params', 'N/A')}")
        print(f"[CNN]    类别: {checkpoint['class_names']}")
        return model
    except Exception as e:
        print(f"[CNN] [ERROR] 加载模型失败: {e}")
        return None


def predict_image(model: CNNClassifier, image: Image.Image,
                  device: str = "cpu") -> Dict:
    """用训练好的 CNN 对单张图片进行病害分类"""
    transform = CNNClassifier.get_transform()
    img_tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(img_tensor)
        probabilities = torch.softmax(outputs, dim=1)
        confidence, predicted = torch.max(probabilities, 1)

    class_en = CNNClassifier.CLASS_NAMES[predicted.item()]
    confidence_val = confidence.item()

    return {
        "label": CNNClassifier.CLASS_NAMES_CN.get(class_en, class_en),
        "label_en": class_en,
        "label_en_display": CNNClassifier.CLASS_NAMES_EN.get(class_en, class_en),
        "confidence": round(confidence_val, 4),
        "is_disease": class_en != "healthy",
        "all_probabilities": {
            CNNClassifier.CLASS_NAMES_CN.get(name, name): round(prob.item(), 4)
            for name, prob in zip(CNNClassifier.CLASS_NAMES, probabilities[0])
        }
    }
