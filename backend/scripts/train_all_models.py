"""
=============================================================================
统一模型训练脚本 — 训练 2 个深度学习模型
=============================================================================

模型 1: CNN 病害分类器 (病害图像检测)
  功能: 将叶片图像分类为 6 种病害类别
  数据: PlantVillage Tomato Leaf (5802 张真实图片)
  输出: 混淆矩阵 + 分类报告 + best_cnn_classifier.pth

模型 2: DiseaseTreatmentModel (防治方案推荐)
  功能: 根据病害/严重度/环境推荐防治方案
  数据: 合成农业数据 (1000条)
  输出: 混淆矩阵 + 分类报告 + best_treatment_model.pth

用法:
  python scripts/train_all_models.py                # 完整训练
  python scripts/train_all_models.py --cnn-only      # 仅 CNN
  python scripts/train_all_models.py --torch-only    # 仅 PyTorch
  python scripts/train_all_models.py --cnn-epochs 30

=============================================================================
"""
import sys
import io
import os
import json
import argparse
import time
import shutil
import warnings
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from collections import Counter, defaultdict

# UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
warnings.filterwarnings("ignore")

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# ============================================================================
# 路径配置
# ============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
DATASETS_DIR = BASE_DIR / "datasets"
REPORTS_DIR = BASE_DIR / "training_reports"

MODELS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# ============================================================================
# 通用工具函数
# ============================================================================

def plot_confusion_matrix(cm: np.ndarray, class_names: List[str],
                          title: str, save_path: Path, normalize: bool = True):
    """绘制混淆矩阵"""
    if normalize:
        cm_norm = cm.astype('float') / (cm.sum(axis=1, keepdims=True) + 1e-9)
    else:
        cm_norm = cm

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=class_names, yticklabels=class_names,
                ax=axes[0], cbar_kws={'label': 'Count'})
    axes[0].set_title(f'{title} — Confusion Matrix (Count)', fontsize=13, fontweight='bold')
    axes[0].set_xlabel('Predicted')
    axes[0].set_ylabel('True')

    sns.heatmap(cm_norm, annot=True, fmt='.2f', cmap='YlOrRd',
                xticklabels=class_names, yticklabels=class_names,
                ax=axes[1], cbar_kws={'label': 'Proportion'})
    axes[1].set_title(f'{title} — Confusion Matrix (Normalized)', fontsize=13, fontweight='bold')
    axes[1].set_xlabel('Predicted')
    axes[1].set_ylabel('True')

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  📊 混淆矩阵已保存: {save_path}")


def plot_training_curves(history: Dict, title: str, save_path: Path):
    """绘制训练曲线"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    if 'train_loss' in history and 'val_loss' in history:
        axes[0].plot(history['train_loss'], 'o-', label='Train Loss', markersize=3)
        axes[0].plot(history['val_loss'], 's-', label='Val Loss', markersize=3)
    axes[0].set_title(f'{title} — Loss', fontweight='bold')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Loss')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    acc_keys = [k for k in history if 'acc' in k.lower()]
    if acc_keys:
        for k in acc_keys:
            axes[1].plot(history[k], 'o-', label=k, markersize=3)
    elif 'train_mae' in history:
        axes[1].plot(history['train_mae'], 'o-', label='Train MAE', markersize=3)
        axes[1].plot(history['val_mae'], 's-', label='Val MAE', markersize=3)
    axes[1].set_title(f'{title} — Metrics', fontweight='bold')
    axes[1].set_xlabel('Epoch')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  📈 训练曲线已保存: {save_path}")


def print_classification_report(report_dict: Dict, class_names_: List[str], title: str):
    """打印格式化的分类报告"""
    print(f"\n  {'=' * 65}")
    print(f"  {title} — Classification Report")
    print(f"  {'=' * 65}")
    print(f"  {'Class':<25s} {'Precision':>10s} {'Recall':>10s} {'F1':>10s} {'Support':>10s}")
    print(f"  {'-' * 65}")

    for name in class_names_:
        if name in report_dict:
            r = report_dict[name]
            support_val = int(r['support'])
            print(f"  {name:<25s} {r['precision']:>10.4f} {r['recall']:>10.4f} "
                  f"{r['f1-score']:>10.4f} {support_val:>10d}")

    for avg_type in ['macro avg', 'weighted avg']:
        if avg_type in report_dict:
            r = report_dict[avg_type]
            support_val = int(r['support'])
            print(f"  {'-' * 65}")
            print(f"  {avg_type:<25s} {r['precision']:>10.4f} {r['recall']:>10.4f} "
                  f"{r['f1-score']:>10.4f} {support_val:>10d}")

    if 'accuracy' in report_dict:
        acc = report_dict['accuracy']
        print(f"  {'-' * 65}")
        print(f"  {'Accuracy':<25s} {'':>10s} {'':>10s} {'':>10s} {acc:>10.4f}")


# ============================================================================
# 模型 1: CNN 病害分类器
# ============================================================================

class PlantDiseaseCNN(nn.Module):
    """4 层 CNN 植物病害分类器"""

    def __init__(self, num_classes: int = 6):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(inplace=True),
            nn.MaxPool2d(2),

            nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(inplace=True),
            nn.MaxPool2d(2),

            nn.Conv2d(64, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(inplace=True),
            nn.MaxPool2d(2),

            nn.Conv2d(128, 256, 3, padding=1), nn.BatchNorm2d(256), nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d(1),
        )
        self.classifier = nn.Sequential(
            nn.Dropout(0.4),
            nn.Linear(256, num_classes),
        )

    def forward(self, x):
        feats = self.features(x)
        return self.classifier(feats.view(feats.size(0), -1))


class ImageFolderDataset(Dataset):
    """从分类文件夹加载图片"""

    def __init__(self, root_dir: Path, transform=None, target_size: int = 224):
        self.samples = []
        self.class_names = sorted([d.name for d in root_dir.iterdir() if d.is_dir()])
        self.class_to_idx = {name: i for i, name in enumerate(self.class_names)}

        for class_dir in root_dir.iterdir():
            if not class_dir.is_dir():
                continue
            cls_idx = self.class_to_idx[class_dir.name]
            for img_file in class_dir.iterdir():
                if img_file.suffix.lower() in {'.jpg', '.jpeg', '.png', '.bmp'}:
                    self.samples.append((str(img_file), cls_idx))

        self.transform = transform
        self.target_size = target_size

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        try:
            img = Image.open(path).convert('RGB')
            if self.transform:
                img = self.transform(img)
            return img, label
        except Exception:
            return torch.zeros(3, self.target_size, self.target_size), label


def train_cnn_classifier(args) -> Dict:
    """训练 CNN 病害分类模型"""
    from torchvision import transforms
    from sklearn.metrics import classification_report, confusion_matrix

    print("\n" + "=" * 70)
    print("  模型 1/2: CNN 植物病害分类检测模型")
    print("=" * 70)

    device = torch.device('cpu')

    # 数据路径
    data_root = DATASETS_DIR / "processed" / "tomato"
    if not data_root.exists():
        data_root = DATASETS_DIR / "yolo_dataset"

    print(f"  数据集: {data_root}")

    # 数据转换
    train_tf = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    val_tf = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # 加载数据
    train_ds = ImageFolderDataset(data_root / "train", train_tf)
    val_ds = ImageFolderDataset(data_root / "val", val_tf) if (data_root / "val").exists() else None
    test_ds = ImageFolderDataset(data_root / "test", val_tf) if (data_root / "test").exists() else None

    n_train = len(train_ds)
    if val_ds is None:
        n_val = int(0.2 * n_train)
        n_train2 = n_train - n_val
        train_ds, val_ds = torch.utils.data.random_split(
            train_ds, [n_train2, n_val],
            generator=torch.Generator().manual_seed(42))
        val_ds = val_ds  # subset
        n_train = n_train2
        n_val = len(val_ds)

    class_names = train_ds.dataset.class_names if hasattr(train_ds, 'dataset') else train_ds.class_names
    n_val = len(val_ds)
    n_test = len(test_ds) if test_ds else 0

    print(f"  类别数: {len(class_names)}")
    print(f"  类别: {class_names}")
    print(f"  训练: {n_train} | 验证: {n_val} | 测试: {n_test}")

    # DataLoaders
    train_loader = DataLoader(train_ds, batch_size=args.cnn_batch, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=args.cnn_batch, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=args.cnn_batch, shuffle=False, num_workers=0) if test_ds else None

    # 模型
    model = PlantDiseaseCNN(num_classes=len(class_names)).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"  架构: 4-Conv CNN ({n_params:,} 参数)")

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=5, factor=0.5)

    best_val_acc = 0.0
    history = {'train_loss': [], 'val_loss': [], 'train_acc': [], 'val_acc': []}
    epochs = args.cnn_epochs

    print(f"\n  🚀 开始训练 ({epochs} epochs)...")
    t0 = time.time()

    for epoch in range(epochs):
        model.train()
        tloss, tcorrect = 0.0, 0
        for imgs, lbls in train_loader:
            imgs, lbls = imgs.to(device), lbls.to(device)
            optimizer.zero_grad()
            loss = criterion(model(imgs), lbls)
            loss.backward()
            optimizer.step()
            tloss += loss.item() * imgs.size(0)
            tcorrect += (model(imgs).argmax(1) == lbls).sum().item()

        model.eval()
        vloss, vcorrect = 0.0, 0
        with torch.no_grad():
            for imgs, lbls in val_loader:
                imgs, lbls = imgs.to(device), lbls.to(device)
                outs = model(imgs)
                vloss += criterion(outs, lbls).item() * imgs.size(0)
                vcorrect += (outs.argmax(1) == lbls).sum().item()

        tloss /= len(train_loader.dataset)
        vloss /= len(val_loader.dataset)
        tacc = 100 * tcorrect / len(train_loader.dataset)
        vacc = 100 * vcorrect / len(val_loader.dataset)

        history['train_loss'].append(round(tloss, 6))
        history['val_loss'].append(round(vloss, 6))
        history['train_acc'].append(round(tacc, 2))
        history['val_acc'].append(round(vacc, 2))

        scheduler.step(vloss)

        if vacc > best_val_acc:
            best_val_acc = vacc
            torch.save({
                'model_state_dict': model.state_dict(),
                'class_names': class_names,
                'val_acc': vacc,
            }, str(MODELS_DIR / 'best_cnn_classifier.pth'))

        if (epoch + 1) % 5 == 0 or epoch == 0:
            print(f"  Epoch {epoch+1:3d}/{epochs} | "
                  f"Train Loss: {tloss:.4f} | Val Loss: {vloss:.4f} | "
                  f"Train Acc: {tacc:.1f}% | Val Acc: {vacc:.1f}%")

    train_time = time.time() - t0
    print(f"\n  ✅ 训练完成! 耗时: {train_time/60:.1f} 分钟 | 最佳 Val Acc: {best_val_acc:.1f}%")

    # ═══ 验证集评估 ═══
    print(f"\n  📊 验证集评估...")
    model.eval()
    all_preds, all_labels = [], []
    with torch.no_grad():
        for imgs, lbls in val_loader:
            all_preds.extend(model(imgs.to(device)).argmax(1).cpu().numpy())
            all_labels.extend(lbls.numpy())

    cm = confusion_matrix(all_labels, all_preds)
    report_dict = classification_report(all_labels, all_preds, target_names=class_names,
                                        output_dict=True, zero_division=0)

    # 打印
    print(f"\n  📊 混淆矩阵:")
    print(f"  {'':>25s}" + "".join(f"{n[:8]:>10s}" for n in class_names))
    for i, n in enumerate(class_names):
        print(f"  {n:>25s}" + "".join(f"{cm[i][j]:>10d}" for j in range(len(class_names))))

    print_classification_report(report_dict, class_names, "CNN Disease Classifier")

    # 图表
    cm_path = REPORTS_DIR / "cnn_confusion_matrix.png"
    plot_confusion_matrix(cm, class_names, "CNN — Tomato Disease Classification", cm_path)
    curve_path = REPORTS_DIR / "cnn_training_curves.png"
    plot_training_curves(history, "CNN Disease Classifier", curve_path)

    # ═══ 测试集评估 ═══
    test_acc = None
    if test_loader:
        print(f"\n  📊 测试集评估...")
        model.eval()
        test_correct, test_preds, test_labels = 0, [], []
        with torch.no_grad():
            for imgs, lbls in test_loader:
                outs = model(imgs.to(device))
                preds = outs.argmax(1)
                test_correct += (preds == lbls.to(device)).sum().item()
                test_preds.extend(preds.cpu().numpy())
                test_labels.extend(lbls.numpy())
        test_acc = 100 * test_correct / len(test_loader.dataset)
        print(f"  测试集准确率: {test_acc:.1f}%")
        test_cm = confusion_matrix(test_labels, test_preds)
        test_cm_path = REPORTS_DIR / "cnn_test_confusion_matrix.png"
        plot_confusion_matrix(test_cm, class_names, "CNN — Test Set", test_cm_path)

    # 报告
    eval_data = {
        "model": "PlantDiseaseCNN",
        "num_params": n_params,
        "best_val_accuracy": round(best_val_acc, 2),
        "test_accuracy": round(test_acc, 2) if test_acc else None,
        "train_samples": n_train, "val_samples": n_val, "test_samples": n_test,
        "confusion_matrix": cm.tolist(),
        "classification_report": report_dict,
        "training_history": history,
        "train_time_minutes": round(train_time / 60, 1),
    }
    with open(REPORTS_DIR / "cnn_evaluation.json", 'w', encoding='utf-8') as f:
        json.dump(eval_data, f, ensure_ascii=False, indent=2)
    print(f"  📄 报告已保存")

    return eval_data


# ============================================================================
# 模型 2: DiseaseTreatmentModel (PyTorch)
# ============================================================================

class DiseaseTreatmentModel(nn.Module):
    """多任务: 治疗方案分类 + 严重程度分类"""

    def __init__(self, input_size=16, hidden_size=64, output_size=6):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_size, hidden_size), nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size // 2), nn.ReLU(), nn.Dropout(0.2),
        )
        self.treatment_head = nn.Sequential(nn.Linear(hidden_size // 2, output_size), nn.Softmax(dim=1))
        self.severity_head = nn.Sequential(nn.Linear(hidden_size // 2, 3), nn.Softmax(dim=1))

    def forward(self, x):
        e = self.encoder(x)
        return self.treatment_head(e), self.severity_head(e)


class EffectEvaluationModel(nn.Module):
    """回归模型: 预测防治效果评分"""

    def __init__(self, input_size=8, hidden_size=32):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, hidden_size), nn.ReLU(), nn.BatchNorm1d(hidden_size),
            nn.Dropout(0.3),
            nn.Linear(hidden_size, hidden_size // 2), nn.ReLU(),
            nn.Linear(hidden_size // 2, 1), nn.Sigmoid(),
        )

    def forward(self, x):
        return self.net(x)


class DiseaseDataset(Dataset):
    DISEASE_NAMES = ["叶斑病", "锈病", "白粉病", "早疫病", "晚疫病", "健康"]
    SEVERITY_NAMES = ["light", "medium", "severe"]
    CROP_NAMES = ["番茄", "黄瓜", "其他"]

    def __init__(self, data: List[Dict]):
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        dmap = {n: [1 if i == j else 0 for j in range(6)] for i, n in enumerate(self.DISEASE_NAMES)}
        smap = {n: [1 if i == j else 0 for j in range(3)] for i, n in enumerate(self.SEVERITY_NAMES)}
        cmap = {n: [1 if i == j else 0 for j in range(3)] for i, n in enumerate(self.CROP_NAMES)}

        dv = dmap.get(item.get('disease', '健康'), [0]*5+[1])
        sv = smap.get(item.get('severity', 'medium'), [0, 1, 0])
        cv = cmap.get(item.get('crop_type', '其他'), [0, 0, 1])
        w = item.get('weather', {})
        e = item.get('env_conditions', {})
        feats = dv + sv + cv + [
            w.get('temperature', 25) / 40.0, w.get('humidity', 60) / 100.0,
            e.get('ph', 7.0) / 14.0, e.get('soil_moisture', 50) / 100.0,
        ]
        return (torch.tensor(feats, dtype=torch.float32),
                torch.tensor(item.get('treatment_type', 0), dtype=torch.long),
                torch.tensor(item.get('severity_level', 1), dtype=torch.long))


class EvalDataset(Dataset):
    def __init__(self, data: List[Dict]):
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        feats = torch.tensor([
            item.get('before_count', 0) / 100.0, item.get('after_count', 0) / 100.0,
            item.get('reduction_rate', 0) / 100.0, item.get('severity', 1) / 3.0,
            item.get('treatment_type', 0) / 3.0, item.get('time_interval', 7) / 30.0,
            item.get('confidence', 0.8), item.get('environmental_factor', 0.5),
        ], dtype=torch.float32)
        return feats, torch.tensor([item.get('effectiveness_score', 0.5)], dtype=torch.float32)


def gen_synthetic_data(n: int = 1000):
    diseases = ["叶斑病", "锈病", "白粉病", "早疫病", "晚疫病", "健康"]
    dt_map = {
        "叶斑病": [0, 1, 2], "锈病": [2, 3, 5], "白粉病": [2, 3, 4],
        "早疫病": [0, 3, 5], "晚疫病": [1, 5], "健康": [4, 5],
    }

    dd = []
    for _ in range(n):
        disease = np.random.choice(diseases)
        severity = np.random.choice(["light", "medium", "severe"])
        tt = np.random.choice(dt_map[disease]) if np.random.random() < 0.8 else np.random.randint(0, 6)
        sev_map = {"light": 0, "medium": 1, "severe": 2}
        sl = sev_map[severity] if np.random.random() < 0.85 else np.random.randint(0, 3)

        dd.append({
            'disease': disease, 'severity': severity,
            'crop_type': np.random.choice(["番茄", "黄瓜", "其他"]),
            'weather': {'temperature': float(np.random.uniform(15, 35)),
                        'humidity': float(np.random.uniform(40, 90))},
            'env_conditions': {'ph': float(np.random.uniform(5.5, 8.5)),
                               'soil_moisture': float(np.random.uniform(30, 80))},
            'treatment_type': tt, 'severity_level': sl,
        })

    ed = []
    for _ in range(n // 2):
        bc = np.random.randint(10, 100)
        eff = float(np.random.uniform(0, 1))
        ac = int(bc * (1 - eff * 0.8))
        rr = ((bc - ac) / bc * 100) if bc > 0 else 0
        ed.append({
            'before_count': int(bc), 'after_count': int(ac),
            'reduction_rate': float(rr), 'severity': np.random.randint(0, 3),
            'treatment_type': np.random.randint(0, 4),
            'time_interval': np.random.randint(3, 21),
            'confidence': float(np.random.uniform(0.6, 0.95)),
            'environmental_factor': float(np.random.uniform(0, 1)),
            'effectiveness_score': float(eff),
        })
    return dd, ed


def train_treatment_model_fn(model, train_ldr, val_ldr, epochs=50, lr=0.001, patience=10):
    device = torch.device('cpu')
    model.to(device)
    ct = nn.CrossEntropyLoss()
    cs = nn.CrossEntropyLoss()
    opt = optim.Adam(model.parameters(), lr=lr)
    sch = optim.lr_scheduler.ReduceLROnPlateau(opt, 'min', patience=5)

    hist = {'train_loss': [], 'val_loss': [], 'train_acc': [], 'val_acc': []}
    best_vl, pc = float('inf'), 0

    for ep in range(epochs):
        model.train()
        tl, tc, tt = 0.0, 0, 0
        for f, tlbl, slbl in train_ldr:
            opt.zero_grad()
            to, so = model(f)
            loss = ct(to, tlbl) + 0.5 * cs(so, slbl)
            loss.backward()
            opt.step()
            tl += loss.item()
            tc += (to.argmax(1) == tlbl).sum().item()
            tt += tlbl.size(0)

        model.eval()
        vl, vc, vt = 0.0, 0, 0
        with torch.no_grad():
            for f, tlbl, slbl in val_ldr:
                to, so = model(f)
                vl += (ct(to, tlbl) + 0.5 * cs(so, slbl)).item()
                vc += (to.argmax(1) == tlbl).sum().item()
                vt += tlbl.size(0)

        tl /= len(train_ldr)
        vl /= len(val_ldr)
        ta = 100 * tc / tt
        va = 100 * vc / vt

        hist['train_loss'].append(round(tl, 6))
        hist['val_loss'].append(round(vl, 6))
        hist['train_acc'].append(round(ta, 2))
        hist['val_acc'].append(round(va, 2))

        sch.step(vl)
        if vl < best_vl:
            best_vl = vl
            pc = 0
            torch.save(model.state_dict(), str(MODELS_DIR / 'best_treatment_model.pth'))
        else:
            pc += 1
        if pc >= patience:
            break
        if (ep + 1) % 10 == 0:
            print(f"  Epoch {ep+1:3d}/{epochs} | Train Loss: {tl:.4f} | Val Loss: {vl:.4f} | "
                  f"Train Acc: {ta:.1f}% | Val Acc: {va:.1f}%")
    return hist


def train_torch_models(args) -> Dict:
    from sklearn.metrics import classification_report, confusion_matrix, mean_squared_error, mean_absolute_error, r2_score

    print("\n" + "=" * 70)
    print("  模型 2/2: PyTorch 防治方案 & 效果评估模型")
    print("=" * 70)

    dd, ed = gen_synthetic_data(1000)
    print(f"  合成数据: {len(dd)} 条病害 / {len(ed)} 条评估")

    # 划分
    sp = int(0.8 * len(dd))
    tr_ds = DiseaseDataset(dd[:sp])
    vl_ds = DiseaseDataset(dd[sp:])
    tr_ldr = DataLoader(tr_ds, batch_size=32, shuffle=True)
    vl_ldr = DataLoader(vl_ds, batch_size=32, shuffle=False)

    sp2 = int(0.8 * len(ed))
    tre_ds = EvalDataset(ed[:sp2])
    vle_ds = EvalDataset(ed[sp2:])
    tre_ldr = DataLoader(tre_ds, batch_size=32, shuffle=True)
    vle_ldr = DataLoader(vle_ds, batch_size=32, shuffle=False)

    report = {}

    # ═══ 模型 2a ═══════════════════════
    print(f"\n  {'─'*55}")
    print(f"  模型 2a: DiseaseTreatmentModel (防治方案推荐)")
    print(f"  {'─'*55}")

    tm = DiseaseTreatmentModel()
    t_hist = train_treatment_model_fn(tm, tr_ldr, vl_ldr, epochs=args.torch_epochs)

    tm.load_state_dict(torch.load(str(MODELS_DIR / 'best_treatment_model.pth'), map_location='cpu'))
    tm.eval()
    all_p, all_l = [], []
    with torch.no_grad():
        for f, tlbl, _ in vl_ldr:
            all_p.extend(tm(f)[0].argmax(1).cpu().numpy())
            all_l.extend(tlbl.numpy())

    acc = np.mean(np.array(all_p) == np.array(all_l))
    cls_names = DiseaseDataset.DISEASE_NAMES
    present = sorted(set(all_l) | set(all_p))
    pnames = [cls_names[i] for i in present if i < len(cls_names)]

    cm = confusion_matrix(all_l, all_p, labels=present)
    cr = classification_report(all_l, all_p, target_names=pnames, output_dict=True, zero_division=0)

    print(f"\n  Accuracy: {acc:.4f} ({acc*100:.1f}%)")
    print_classification_report(cr, pnames, "DiseaseTreatmentModel")

    plot_confusion_matrix(cm, pnames, "DiseaseTreatmentModel", REPORTS_DIR / "treatment_cm.png")
    plot_training_curves(t_hist, "DiseaseTreatmentModel", REPORTS_DIR / "treatment_curves.png")

    report['treatment_model'] = {'accuracy': round(acc, 4), 'cm': cm.tolist(), 'cr': cr, 'history': t_hist}

    # ═══ 模型 2b ═══════════════════════
    print(f"\n  {'─'*55}")
    print(f"  模型 2b: EffectEvaluationModel (效果评估)")
    print(f"  {'─'*55}")

    em = EffectEvaluationModel()
    device = torch.device('cpu')
    em.to(device)
    crit = nn.MSELoss()
    opt = optim.Adam(em.parameters(), lr=0.001)
    sch = optim.lr_scheduler.ReduceLROnPlateau(opt, 'min', patience=5)

    ehist = {'train_loss': [], 'val_loss': [], 'train_mae': [], 'val_mae': []}
    best_vl, pc = float('inf'), 0

    for ep in range(args.torch_epochs):
        em.train()
        tl, tmae = 0.0, 0.0
        for f, tgt in tre_ldr:
            opt.zero_grad()
            loss = crit(em(f), tgt)
            loss.backward()
            opt.step()
            tl += loss.item()
            tmae += torch.abs(em(f) - tgt).mean().item()

        em.eval()
        vl, vmae = 0.0, 0.0
        with torch.no_grad():
            for f, tgt in vle_ldr:
                out = em(f)
                vl += crit(out, tgt).item()
                vmae += torch.abs(out - tgt).mean().item()

        tl /= len(tre_ldr)
        vl /= len(vle_ldr)
        tmae /= len(tre_ldr)
        vmae /= len(vle_ldr)

        ehist['train_loss'].append(round(tl, 6))
        ehist['val_loss'].append(round(vl, 6))
        ehist['train_mae'].append(round(tmae, 6))
        ehist['val_mae'].append(round(vmae, 6))

        sch.step(vl)
        if vl < best_vl:
            best_vl = vl
            pc = 0
            torch.save(em.state_dict(), str(MODELS_DIR / 'best_evaluation_model.pth'))
        else:
            pc += 1
        if pc >= 10:
            break
        if (ep + 1) % 10 == 0:
            print(f"  Epoch {ep+1:3d}/{args.torch_epochs} | "
                  f"Train Loss: {tl:.4f} | Val Loss: {vl:.4f} | "
                  f"Train MAE: {tmae:.4f} | Val MAE: {vmae:.4f}")

    # 评估
    em.load_state_dict(torch.load(str(MODELS_DIR / 'best_evaluation_model.pth'), map_location='cpu'))
    em.eval()
    ap_reg, at_reg = [], []
    with torch.no_grad():
        for f, tgt in vle_ldr:
            ap_reg.extend(em(f).cpu().numpy().flatten())
            at_reg.extend(tgt.numpy().flatten())

    mse = mean_squared_error(at_reg, ap_reg)
    mae = mean_absolute_error(at_reg, ap_reg)
    r2 = r2_score(at_reg, ap_reg)

    print(f"\n  MSE: {mse:.6f} | MAE: {mae:.6f} | RMSE: {np.sqrt(mse):.6f} | R²: {r2:.4f}")

    # 散点图
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(at_reg, ap_reg, alpha=0.5, c='green', edgecolors='darkgreen')
    ax.plot([0, 1], [0, 1], 'r--', label='Perfect')
    ax.set_xlabel('True'); ax.set_ylabel('Predicted')
    ax.set_title('EffectEvaluationModel — Predictions vs True')
    ax.legend(); ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "evaluation_scatter.png", dpi=150)
    plt.close()

    plot_training_curves(ehist, "EffectEvaluationModel", REPORTS_DIR / "evaluation_curves.png")

    report['evaluation_model'] = {'mse': round(mse, 6), 'mae': round(mae, 6),
                                  'rmse': round(np.sqrt(mse), 6), 'r2': round(r2, 4),
                                  'history': ehist}
    return report


# ============================================================================
# 主函数
# ============================================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cnn-only', action='store_true')
    parser.add_argument('--torch-only', action='store_true')
    parser.add_argument('--cnn-epochs', type=int, default=15)
    parser.add_argument('--cnn-batch', type=int, default=16)
    parser.add_argument('--torch-epochs', type=int, default=50)
    args = parser.parse_args()

    print("=" * 70)
    print("  智慧农业病害防治系统 — 深度学习模型训练")
    print("=" * 70)
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  设备: CPU | PyTorch: {torch.__version__}")

    all_reports = {"timestamp": datetime.now().isoformat()}

    # 模型 1: CNN
    if not args.torch_only:
        try:
            all_reports['cnn_classifier'] = train_cnn_classifier(args)
        except Exception as e:
            print(f"\n  ❌ CNN 训练失败: {e}")
            import traceback; traceback.print_exc()

    # 模型 2: PyTorch
    if not args.cnn_only:
        try:
            all_reports['pytorch_models'] = train_torch_models(args)
        except Exception as e:
            print(f"\n  ❌ PyTorch 训练失败: {e}")
            import traceback; traceback.print_exc()

    # ── 总结 ──
    print(f"\n{'=' * 70}")
    print(f"  训练完成!")
    print(f"{'=' * 70}")
    print(f"\n  📁 模型文件 ({MODELS_DIR}):")
    for f in sorted(MODELS_DIR.glob("*.pth")):
        print(f"    📦 {f.name} ({f.stat().st_size/1024:.1f} KB)")
    print(f"\n  📊 报告图表 ({REPORTS_DIR}):")
    for f in sorted(REPORTS_DIR.glob("*.png")):
        print(f"    📊 {f.name}")
    for f in sorted(REPORTS_DIR.glob("*.json")):
        print(f"    📄 {f.name}")

    with open(REPORTS_DIR / "training_summary.json", 'w', encoding='utf-8') as f:
        json.dump(all_reports, f, ensure_ascii=False, indent=2, default=str)

    print(f"\n  ✅ 结束: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
