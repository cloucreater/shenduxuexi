"""
=============================================================================
数据集下载与组织脚本
=============================================================================
功能:
  1. 检查现有的 PlantVillage tomato leaf 数据集
  2. 组织 CPSFR 辣椒病害数据集
  3. 生成 YOLO 兼容的 data.yaml 配置文件
  4. 输出数据集统计报告

现有数据集:
  - tomato leaf (PlantVillage): 6类, 已有 train/val/test 划分 (3831/981/990)
  - CPSFR (辣椒): 4类, 未划分 (约258张)

=============================================================================
"""
import sys
import io
import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from collections import Counter

# UTF-8 编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ============================================================================
# 配置
# ============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
DATASETS_DIR = BASE_DIR / "datasets"
REAL_DIR = DATASETS_DIR / "real_datasets"
YOLO_DIR = DATASETS_DIR / "yolo_dataset"

# 标签映射: 英文名 -> (中文名, YOLO class_id)
DISEASE_CLASSES = {
    # Tomato leaf (PlantVillage)
    "Tomato___Bacterial_spot": ("细菌性斑点病", 0),
    "Tomato___Early_blight": ("早疫病", 1),
    "Tomato___Late_blight": ("晚疫病", 2),
    "Tomato___Leaf_Mold": ("叶霉病", 3),
    "Tomato___Septoria_leaf_spot": ("斑枯病", 4),
    "Tomato___healthy": ("健康", 5),
    # CPSFR (Pepper)
    "CPSFR_FUSAOX_fusarium": ("枯萎病", 6),
    "CPSFR_LEVETA_Leveillula taurica": ("白粉病", 7),
    "CPSFR_XANTAV_Xanthomonas campestris pv. vesicatoria": ("细菌性斑点病", 0),
    "CPSFR_healthy leaves": ("健康", 5),
}


def count_images(path: Path) -> int:
    """统计目录中的图片数量"""
    if not path.exists():
        return 0
    exts = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
    return sum(1 for f in path.rglob('*') if f.suffix.lower() in exts)


def analyze_tomato_leaf() -> Dict:
    """分析 tomato leaf 数据集结构"""
    tomato_dir = REAL_DIR / "tomato leaf"
    if not tomato_dir.exists():
        return {"exists": False}

    report = {"exists": True, "base_dir": str(tomato_dir)}

    for split in ["train", "val", "test"]:
        split_dir = tomato_dir / split
        if not split_dir.exists():
            report[split] = {"exists": False, "count": 0, "classes": {}}
            continue

        class_counts = {}
        for class_dir in sorted(split_dir.iterdir()):
            if class_dir.is_dir():
                count = count_images(class_dir)
                class_counts[class_dir.name] = count

        report[split] = {
            "exists": True,
            "count": sum(class_counts.values()),
            "classes": class_counts,
        }

    return report


def analyze_cpsfr() -> Dict:
    """分析 CPSFR 数据集"""
    report = {"exists": True, "datasets": {}}

    for d in sorted(REAL_DIR.iterdir()):
        if d.is_dir() and d.name.startswith("CPSFR_"):
            name = d.name
            # 处理嵌套目录 (CPSFR_NAME/CPSFR_NAME/)
            inner = d / name
            if inner.exists() and inner.is_dir():
                count = count_images(inner)
            else:
                count = count_images(d)
            report["datasets"][name] = {
                "path": str(d),
                "count": count,
                "class_info": DISEASE_CLASSES.get(name, ("未知", -1)),
            }

    report["total"] = sum(v["count"] for v in report["datasets"].values())
    return report


def create_yolo_dataset() -> Dict:
    """
    创建统一 YOLO 格式数据集目录结构:

    yolo_dataset/
    ├── data.yaml           # 数据集配置
    ├── train/
    │   ├── images/         # 训练图片 (软链接或复制)
    │   └── labels/         # YOLO 标签 (分类模式不使用)
    ├── val/
    │   ├── images/
    │   └── labels/
    └── test/
        ├── images/
        └── labels/

    注意: 由于 PlantVillage 是分类数据集（图片级标签，无 bbox），
    我们创建 YOLOv8 分类格式:
    yolo_dataset/
    ├── data.yaml
    ├── train/
    │   ├── Bacterial_spot/
    │   ├── Early_blight/
    │   └── ...
    ├── val/
    │   └── ...
    └── test/
        └── ...
    """
    report = {"status": "started", "classes": [], "splits": {}}

    tomato_dir = REAL_DIR / "tomato leaf"
    if not tomato_dir.exists():
        report["status"] = "no_tomato_data"
        return report

    # 清理旧的 YOLO 目录
    if YOLO_DIR.exists():
        shutil.rmtree(YOLO_DIR)

    # 类名映射: PlantVillage 原名 -> 简洁 YOLO 类名
    class_rename = {
        "Tomato___Bacterial_spot": "Bacterial_spot",
        "Tomato___Early_blight": "Early_blight",
        "Tomato___Late_blight": "Late_blight",
        "Tomato___Leaf_Mold": "Leaf_Mold",
        "Tomato___Septoria_leaf_spot": "Septoria_leaf_spot",
        "Tomato___healthy": "Healthy",
    }

    class_names = list(class_rename.values())
    class_names_cn = [
        DISEASE_CLASSES.get(orig, ("", -1))[0]
        for orig in class_rename.keys()
    ]

    # 创建目录结构并复制文件
    for split in ["train", "val", "test"]:
        src_split = tomato_dir / split
        if not src_split.exists():
            continue

        dst_split = YOLO_DIR / split
        split_counts = {}

        for src_class_dir in src_split.iterdir():
            if not src_class_dir.is_dir():
                continue

            orig_name = src_class_dir.name
            new_name = class_rename.get(orig_name, orig_name)
            dst_class_dir = dst_split / new_name
            dst_class_dir.mkdir(parents=True, exist_ok=True)

            # 复制图片
            copied = 0
            for img_file in src_class_dir.iterdir():
                if img_file.suffix.lower() in {'.jpg', '.jpeg', '.png', '.bmp'}:
                    dst_file = dst_class_dir / img_file.name
                    if not dst_file.exists():
                        shutil.copy2(img_file, dst_file)
                    copied += 1

            split_counts[new_name] = copied

        report["splits"][split] = {
            "path": str(dst_split),
            "total": sum(split_counts.values()),
            "classes": split_counts,
        }

    # 生成 data.yaml
    data_yaml = {
        "path": str(YOLO_DIR.absolute()),
        "train": "train",
        "val": "val",
        "test": "test",
        "nc": len(class_names),
        "names": class_names,
        "names_cn": class_names_cn,
        "description": "PlantVillage Tomato Leaf Disease Dataset (YOLO Classification Format)",
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    yaml_path = YOLO_DIR / "data.yaml"
    with open(yaml_path, 'w', encoding='utf-8') as f:
        # 手动写 YAML 以保持可读性
        f.write(f"# YOLOv8 Classification Dataset Config\n")
        f.write(f"# Generated: {data_yaml['created']}\n")
        f.write(f"# Source: PlantVillage Tomato Leaf Subset\n\n")
        f.write(f"path: {data_yaml['path']}\n")
        f.write(f"train: {data_yaml['train']}\n")
        f.write(f"val: {data_yaml['val']}\n")
        f.write(f"test: {data_yaml['test']}\n\n")
        f.write(f"# Number of classes\n")
        f.write(f"nc: {data_yaml['nc']}\n\n")
        f.write(f"# Class names (English)\n")
        f.write(f"names:\n")
        for i, name in enumerate(class_names):
            f.write(f"  {i}: {name}  # {class_names_cn[i]}\n")

    report["yaml_path"] = str(yaml_path)
    report["classes"] = class_names
    report["classes_cn"] = class_names_cn
    report["nc"] = len(class_names)
    report["status"] = "complete"

    return report


def organize_cpsfr_for_yolo() -> Dict:
    """
    将 CPSFR 辣椒数据集组织为 YOLO 分类格式并按 7:2:1 划分

    CPSFR 数据集包含4类辣椒叶片图片:
      - CPSFR_FUSAOX_fusarium (枯萎病)
      - CPSFR_LEVETA_Leveillula taurica (白粉病)
      - CPSFR_XANTAV_Xanthomonas (细菌性斑点病)
      - CPSFR_healthy leaves (健康)
    """
    import random
    random.seed(42)

    report = {"status": "started", "classes": {}, "splits": {}}

    cpsfr_yolo_dir = DATASETS_DIR / "yolo_cpsfr"
    if cpsfr_yolo_dir.exists():
        shutil.rmtree(cpsfr_yolo_dir)

    class_rename = {
        "CPSFR_FUSAOX_fusarium": "Fusarium_wilt",
        "CPSFR_LEVETA_Leveillula taurica": "Powdery_mildew",
        "CPSFR_XANTAV_Xanthomonas campestris pv. vesicatoria": "Bacterial_spot",
        "CPSFR_healthy leaves": "Healthy",
    }

    # 收集所有图片
    all_images = {name: [] for name in class_rename.values()}

    for src_name, dst_name in class_rename.items():
        src_dir = REAL_DIR / src_name / src_name  # 嵌套目录
        if not src_dir.exists():
            src_dir = REAL_DIR / src_name

        if src_dir.exists():
            for f in src_dir.iterdir():
                if f.suffix.lower() in {'.jpg', '.jpeg', '.png', '.bmp'}:
                    all_images[dst_name].append(f)

    # 按 7:2:1 划分
    splits = {"train": 0.7, "val": 0.2, "test": 0.1}
    split_dest = {}

    for class_name, images in all_images.items():
        random.shuffle(images)
        n = len(images)
        n_train = int(n * 0.7)
        n_val = int(n * 0.2)

        split_dest[(class_name, "train")] = images[:n_train]
        split_dest[(class_name, "val")] = images[n_train : n_train + n_val]
        split_dest[(class_name, "test")] = images[n_train + n_val :]

        report["classes"][class_name] = {
            "total": n,
            "train": n_train,
            "val": n_val,
            "test": n - n_train - n_val,
        }

    # 复制文件
    for split_name in ["train", "val", "test"]:
        dst_split = cpsfr_yolo_dir / split_name
        split_counts = {}

        for class_name in class_rename.values():
            dst_class_dir = dst_split / class_name
            dst_class_dir.mkdir(parents=True, exist_ok=True)

            copied = 0
            for src_file in split_dest.get((class_name, split_name), []):
                dst_file = dst_class_dir / src_file.name
                if not dst_file.exists():
                    shutil.copy2(src_file, dst_file)
                copied += 1
            split_counts[class_name] = copied

        report["splits"][split_name] = {
            "path": str(dst_split),
            "total": sum(split_counts.values()),
            "classes": split_counts,
        }

    # 生成 data.yaml
    class_names = list(class_rename.values())
    yaml_path = cpsfr_yolo_dir / "data.yaml"
    with open(yaml_path, 'w', encoding='utf-8') as f:
        f.write(f"# YOLOv8 Classification - CPSFR Pepper Disease Dataset\n")
        f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"path: {cpsfr_yolo_dir.absolute()}\n")
        f.write(f"train: train\n")
        f.write(f"val: val\n")
        f.write(f"test: test\n\n")
        f.write(f"nc: {len(class_names)}\n\n")
        f.write(f"names:\n")
        for i, name in enumerate(class_names):
            f.write(f"  {i}: {name}\n")

    report["yaml_path"] = str(yaml_path)
    report["nc"] = len(class_names)
    report["status"] = "complete"

    return report


def print_separator(title: str):
    """打印分隔标题"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def main():
    print("=" * 60)
    print("  智慧农业病害防治系统 — 数据集组织脚本")
    print("=" * 60)
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  基目录: {BASE_DIR}")

    # ── 1. 分析 tomato leaf 数据集 ──────────────────────────
    print_separator("1/4 分析 PlantVillage Tomato Leaf 数据集")
    tomato_report = analyze_tomato_leaf()
    if tomato_report["exists"]:
        print(f"  ✅ 数据集已存在: {tomato_report['base_dir']}")
        for split in ["train", "val", "test"]:
            info = tomato_report[split]
            print(f"\n  [{split}] 总计 {info['count']} 张图片")
            for cls, cnt in info["classes"].items():
                short = cls.replace("Tomato___", "")
                cn_name = DISEASE_CLASSES.get(cls, ("",))[0]
                print(f"    {short:25s} ({cn_name:10s}): {cnt:4d} 张")
    else:
        print("  ❌ 未找到 tomato leaf 数据集")
        print("  💡 请从 Kaggle 下载 PlantVillage 数据集:")
        print("     https://www.kaggle.com/datasets/emmarex/plantdisease")

    # ── 2. 分析 CPSFR 数据集 ────────────────────────────────
    print_separator("2/4 分析 CPSFR 辣椒病害数据集")
    cpsfr_report = analyze_cpsfr()
    print(f"  总计 {cpsfr_report['total']} 张图片 ({len(cpsfr_report['datasets'])} 类)")
    for name, info in cpsfr_report["datasets"].items():
        cn_name, cls_id = info["class_info"]
        short = name.replace("CPSFR_", "").replace("_", " ")[:40]
        print(f"    {short:42s} ({cn_name:10s}): {info['count']:4d} 张")

    # ── 3. 创建 YOLO 格式数据集 ──────────────────────────────
    print_separator("3/4 创建 YOLO 格式数据集 (Tomato)")
    yolo_report = create_yolo_dataset()
    if yolo_report["status"] == "complete":
        print(f"  ✅ YOLO 数据集已创建: {YOLO_DIR}")
        print(f"  类别数: {yolo_report['nc']}")
        print(f"  类别: {', '.join(yolo_report['classes'])}")
        for split, info in yolo_report["splits"].items():
            print(f"  [{split}] {info['total']} 张图片")
        print(f"  配置: {yolo_report['yaml_path']}")
    else:
        print(f"  ⚠️  {yolo_report['status']}")

    # ── 4. 组织 CPSFR 数据集 ─────────────────────────────────
    print_separator("4/4 组织 CPSFR 数据集 (7:2:1 划分)")
    cpsfr_yolo = organize_cpsfr_for_yolo()
    if cpsfr_yolo["status"] == "complete":
        print(f"  ✅ CPSFR YOLO 数据集已创建: {DATASETS_DIR / 'yolo_cpsfr'}")
        print(f"  类别数: {cpsfr_yolo['nc']}")
        print(f"  划分比例 7:2:1:")
        for cls, info in cpsfr_yolo["classes"].items():
            print(f"    {cls:20s}: total={info['total']:3d} "
                  f"train={info['train']:3d} val={info['val']:3d} test={info['test']:3d}")
    else:
        print(f"  ⚠️  {cpsfr_yolo['status']}")

    # ── 最终总结 ─────────────────────────────────────────────
    print_separator("总结")
    total_train = sum(
        yolo_report.get("splits", {}).get("train", {}).get("total", 0)
        for _ in [1]
    )
    print(f"""
  📁 数据集目录结构:
    {DATASETS_DIR}/
    ├── real_datasets/
    │   ├── tomato leaf/          # PlantVillage 番茄 6类 (5802张)
    │   │   ├── train/            # 3831 张 (66%)
    │   │   ├── val/              #  981 张 (17%)
    │   │   └── test/             #  990 张 (17%)
    │   └── CPSFR_*/              # 辣椒 4类 (258张)
    │
    ├── yolo_dataset/             # 🆕 YOLO 番茄数据集
    │   ├── data.yaml
    │   ├── train/ (6类)
    │   ├── val/   (6类)
    │   └── test/  (6类)
    │
    ├── yolo_cpsfr/               # 🆕 YOLO 辣椒数据集 (7:2:1)
    │   ├── data.yaml
    │   ├── train/ (4类)
    │   ├── val/   (4类)
    │   └── test/  (4类)
    │
    └── synthetic_datasets/       # 合成 JSON 数据

  📋 下一步:
    1. 运行数据预处理: python scripts/preprocess_data.py
    2. 训练 YOLO 模型: yolo classify train data=datasets/yolo_dataset/data.yaml model=yolov8n-cls.pt
    3. 或集成到现有系统: 更新 detector.py 加载微调后的模型
""")

    # 保存报告为 JSON
    report_path = DATASETS_DIR / "dataset_setup_report.json"
    report = {
        "timestamp": datetime.now().isoformat(),
        "tomato": tomato_report,
        "cpsfr": cpsfr_report,
        "yolo_tomato": yolo_report,
        "yolo_cpsfr": cpsfr_yolo,
    }
    # 简化报告（Path 对象转字符串）
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    print(f"  📊 完整报告已保存: {report_path}")


if __name__ == "__main__":
    main()
