"""
=============================================================================
数据预处理脚本
=============================================================================
功能:
  1. 图像统一 resize 到指定尺寸 (默认 640x640)
  2. 数据增强: 随机翻转、旋转、亮度/对比度调整、噪声
  3. 标签标准化: PlantVillage 类名 → 统一标签格式
  4. 生成增强后的训练集 (可选, 仅对 train 集增强)
  5. 数据集质量检查: 损坏图片检测、尺寸分布统计

用法:
  # 基础预处理 (resize + 验证)
  python scripts/preprocess_data.py

  # 包含数据增强
  python scripts/preprocess_data.py --augment --augment-factor 3

  # 指定目标尺寸
  python scripts/preprocess_data.py --size 416

  # 仅处理 tomato leaf 数据集
  python scripts/preprocess_data.py --dataset tomato

=============================================================================
"""
import sys
import io
import os
import json
import argparse
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import numpy as np
from PIL import Image, ImageOps, ImageEnhance, ImageFilter

# ============================================================================
# 配置
# ============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
DATASETS_DIR = BASE_DIR / "datasets"
PROCESSED_DIR = DATASETS_DIR / "processed"

# 默认配置
DEFAULT_IMAGE_SIZE = 640  # YOLO 推荐尺寸
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}

# 类名标准化映射
LABEL_NORMALIZE = {
    # PlantVillage tomato
    "Tomato___Bacterial_spot": "bacterial_spot",
    "Tomato___Early_blight": "early_blight",
    "Tomato___Late_blight": "late_blight",
    "Tomato___Leaf_Mold": "leaf_mold",
    "Tomato___Septoria_leaf_spot": "septoria_leaf_spot",
    "Tomato___healthy": "healthy",
    "Tomato___Target_Spot": "target_spot",
    "Tomato___Tomato_mosaic_virus": "mosaic_virus",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "yellow_leaf_curl",
    "Tomato___Spider_mites Two-spotted_spider_mite": "spider_mites",
    # CPSFR pepper
    "CPSFR_FUSAOX_fusarium": "fusarium_wilt",
    "CPSFR_LEVETA_Leveillula taurica": "powdery_mildew",
    "CPSFR_XANTAV_Xanthomonas campestris pv. vesicatoria": "bacterial_spot",
    "CPSFR_healthy leaves": "healthy",
}

# 中文标签
LABEL_CN = {
    "bacterial_spot": "细菌性斑点病",
    "early_blight": "早疫病",
    "late_blight": "晚疫病",
    "leaf_mold": "叶霉病",
    "septoria_leaf_spot": "斑枯病",
    "healthy": "健康",
    "target_spot": "靶斑病",
    "mosaic_virus": "花叶病毒病",
    "yellow_leaf_curl": "黄化曲叶病毒病",
    "spider_mites": "红蜘蛛危害",
    "fusarium_wilt": "枯萎病",
    "powdery_mildew": "白粉病",
}


def get_image_hash(filepath: Path) -> str:
    """计算图片 MD5 哈希 (用于去重)"""
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def is_valid_image(filepath: Path) -> bool:
    """验证图片文件是否完整可读"""
    try:
        with Image.open(filepath) as img:
            img.verify()
        # verify() 后需要重新打开才能读取像素
        with Image.open(filepath) as img:
            img.load()
        return True
    except Exception as e:
        return False


def resize_image(img: Image.Image, target_size: int = DEFAULT_IMAGE_SIZE) -> Image.Image:
    """
    等比缩放并填充到正方形

    策略:
      1. 按长边等比缩放
      2. 用黑色/镜像边缘填充到 target_size x target_size
      3. 保持原始宽高比，不裁剪
    """
    # 计算缩放比例
    w, h = img.size
    scale = target_size / max(w, h)
    new_w, new_h = int(w * scale), int(h * scale)

    # 等比缩放
    img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # 创建目标画布，居中粘贴
    canvas = Image.new("RGB", (target_size, target_size), (0, 0, 0))
    offset_x = (target_size - new_w) // 2
    offset_y = (target_size - new_h) // 2
    canvas.paste(img_resized, (offset_x, offset_y))

    return canvas


def apply_augmentation(img: Image.Image, methods: Optional[List[str]] = None) -> List[Tuple[Image.Image, str]]:
    """
    对单张图片应用数据增强

    返回: [(增强后的图片, 增强方法名称), ...]
    原始图片始终返回在列表第一个位置
    """
    if methods is None:
        methods = ["flip_h", "flip_v", "rotate_90", "rotate_180",
                    "brightness_up", "brightness_down", "contrast_up", "blur"]

    augmented = [(img, "original")]

    for method in methods:
        try:
            if method == "flip_h":
                aug = ImageOps.mirror(img)
            elif method == "flip_v":
                aug = ImageOps.flip(img)
            elif method == "rotate_90":
                aug = img.rotate(90, expand=True)
            elif method == "rotate_180":
                aug = img.rotate(180, expand=True)
            elif method == "rotate_270":
                aug = img.rotate(270, expand=True)
            elif method == "brightness_up":
                enhancer = ImageEnhance.Brightness(img)
                aug = enhancer.enhance(1.3)
            elif method == "brightness_down":
                enhancer = ImageEnhance.Brightness(img)
                aug = enhancer.enhance(0.7)
            elif method == "contrast_up":
                enhancer = ImageEnhance.Contrast(img)
                aug = enhancer.enhance(1.3)
            elif method == "contrast_down":
                enhancer = ImageEnhance.Contrast(img)
                aug = enhancer.enhance(0.7)
            elif method == "blur":
                aug = img.filter(ImageFilter.GaussianBlur(radius=1))
            elif method == "noise":
                arr = np.array(img)
                noise = np.random.normal(0, 10, arr.shape).astype(np.int16)
                noisy = np.clip(arr.astype(np.int16) + noise, 0, 255).astype(np.uint8)
                aug = Image.fromarray(noisy)
            elif method == "hue_shift":
                enhancer = ImageEnhance.Color(img)
                aug = enhancer.enhance(1.5)
            else:
                continue

            augmented.append((aug, method))
        except Exception as e:
            print(f"    ⚠️  增强方法 {method} 失败: {e}")
            continue

    return augmented


def process_dataset(
    src_dir: Path,
    dst_dir: Path,
    target_size: int = DEFAULT_IMAGE_SIZE,
    augment: bool = False,
    augment_factor: int = 2,
    check_quality: bool = True,
) -> Dict:
    """
    处理一个已划分的数据集 (包含 train/val/test 子目录)

    参数:
      src_dir: 源数据集目录 (包含 train/, val/, test/)
      dst_dir: 输出目录
      target_size: 目标图片尺寸
      augment: 是否对训练集进行增强
      augment_factor: 增强倍数 (每张图生成多少额外变体)
      check_quality: 是否进行质量检查

    返回: 处理报告
    """
    report = {
        "source": str(src_dir),
        "target_size": target_size,
        "augment": augment,
        "splits": {},
        "corrupted_files": [],
        "duplicates": [],
        "total_processed": 0,
        "total_original": 0,
    }

    all_hashes = {}  # hash -> filepath, 用于去重检查

    for split_name in ["train", "val", "test"]:
        src_split = src_dir / split_name
        if not src_split.exists():
            print(f"  ⚠️  {split_name}/ 不存在, 跳过")
            continue

        dst_split = dst_dir / split_name
        split_count_orig = 0
        split_count_proc = 0
        class_counts = {}

        for class_dir in sorted(src_split.iterdir()):
            if not class_dir.is_dir():
                continue

            class_name = class_dir.name
            normalized_name = LABEL_NORMALIZE.get(class_name, class_name.lower().replace(" ", "_"))
            dst_class_dir = dst_split / normalized_name
            dst_class_dir.mkdir(parents=True, exist_ok=True)

            orig_count = 0
            proc_count = 0

            for img_file in sorted(class_dir.iterdir()):
                if img_file.suffix.lower() not in ALLOWED_EXTENSIONS:
                    continue

                # ── 质量检查 ──────────────────────────
                if check_quality:
                    # 损坏检测
                    if not is_valid_image(img_file):
                        report["corrupted_files"].append(str(img_file))
                        print(f"    ❌ 损坏文件: {img_file}")
                        continue

                    # 去重检查
                    img_hash = get_image_hash(img_file)
                    if img_hash in all_hashes:
                        report["duplicates"].append({
                            "file": str(img_file),
                            "duplicate_of": str(all_hashes[img_hash]),
                        })
                        continue
                    all_hashes[img_hash] = img_file

                # ── 处理图片 ──────────────────────────
                try:
                    with Image.open(img_file) as img:
                        # 转 RGB
                        if img.mode not in ("RGB", "RGBA"):
                            img = img.convert("RGB")

                        # Resize
                        img_resized = resize_image(img, target_size)

                        # 获取增强参数
                        if augment and split_name == "train":
                            aug_methods = [
                                "flip_h", "flip_v", "rotate_90",
                                "brightness_up", "brightness_down",
                                "contrast_up", "blur",
                            ]
                            # 限制增强数量
                            num_aug = min(augment_factor, len(aug_methods))
                            selected_methods = aug_methods[:num_aug]

                            augmented = apply_augmentation(img_resized, selected_methods)
                        else:
                            augmented = [(img_resized, "original")]

                        # 保存处理后的图片
                        stem = img_file.stem
                        for aug_img, aug_method in augmented:
                            if aug_method == "original":
                                out_name = f"{stem}.jpg"
                            else:
                                out_name = f"{stem}_aug_{aug_method}.jpg"

                            out_path = dst_class_dir / out_name
                            aug_img.save(out_path, "JPEG", quality=95)
                            proc_count += 1

                    orig_count += 1

                except Exception as e:
                    print(f"    ⚠️  处理失败 {img_file.name}: {e}")
                    report["corrupted_files"].append(str(img_file))

            class_counts[normalized_name] = {
                "original": orig_count,
                "processed": proc_count,
            }
            split_count_orig += orig_count
            split_count_proc += proc_count

        report["splits"][split_name] = {
            "original": split_count_orig,
            "processed": split_count_proc,
            "augmentation_ratio": round(split_count_proc / split_count_orig, 2) if split_count_orig > 0 else 0,
            "classes": class_counts,
        }
        report["total_original"] += split_count_orig
        report["total_processed"] += split_count_proc

        print(f"  [{split_name}] {split_count_orig} → {split_count_proc} 张 "
              f"({split_count_proc - split_count_orig} 增强)")

    return report


def generate_labels_json(dst_dir: Path) -> Dict:
    """生成 labels.json 标签映射文件"""
    labels = {}
    labels_cn = {}

    # 从处理后的目录收集所有类名
    class_names = set()
    for split in ["train", "val", "test"]:
        split_dir = dst_dir / split
        if split_dir.exists():
            for d in split_dir.iterdir():
                if d.is_dir():
                    class_names.add(d.name)

    class_names = sorted(class_names)

    for i, name in enumerate(class_names):
        labels[i] = name
        labels_cn[i] = LABEL_CN.get(name, name)

    labels_json = {
        "num_classes": len(class_names),
        "labels": labels,
        "labels_cn": labels_cn,
        "generated": datetime.now().isoformat(),
    }

    labels_path = dst_dir / "labels.json"
    with open(labels_path, 'w', encoding='utf-8') as f:
        json.dump(labels_json, f, ensure_ascii=False, indent=2)

    return labels_json


def print_separator(title: str):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def main():
    parser = argparse.ArgumentParser(description="植物病害数据集预处理")
    parser.add_argument("--size", type=int, default=DEFAULT_IMAGE_SIZE,
                        help=f"目标图片尺寸 (默认: {DEFAULT_IMAGE_SIZE})")
    parser.add_argument("--augment", action="store_true",
                        help="启用数据增强")
    parser.add_argument("--augment-factor", type=int, default=2,
                        help="每张图片增强生成的变体数量 (默认: 2)")
    parser.add_argument("--dataset", type=str, default="all",
                        choices=["all", "tomato", "cpsfr"],
                        help="要处理的数据集 (默认: all)")
    parser.add_argument("--no-quality-check", action="store_true",
                        help="跳过质量检查")
    parser.add_argument("--dry-run", action="store_true",
                        help="仅统计不实际处理")
    args = parser.parse_args()

    print("=" * 60)
    print("  智慧农业病害防治系统 — 数据预处理")
    print("=" * 60)
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  目标尺寸: {args.size}x{args.size}")
    print(f"  数据增强: {'是' if args.augment else '否'}")
    if args.augment:
        print(f"  增强倍数: {args.augment_factor}x")
    print(f"  质量检查: {'否' if args.no_quality_check else '是'}")

    # ── 处理 YOLO Tomato 数据集 ───────────────────────────
    if args.dataset in ("all", "tomato"):
        print_separator("处理 Tomato Leaf 数据集 (PlantVillage)")

        tomato_src = DATASETS_DIR / "yolo_dataset"
        tomato_dst = PROCESSED_DIR / "tomato"

        if tomato_src.exists():
            if not args.dry_run:
                report = process_dataset(
                    tomato_src,
                    tomato_dst,
                    target_size=args.size,
                    augment=args.augment,
                    augment_factor=args.augment_factor,
                    check_quality=not args.no_quality_check,
                )

                # 生成标签文件
                labels_json = generate_labels_json(tomato_dst)

                # 保存报告
                report_path = PROCESSED_DIR / "tomato" / "preprocess_report.json"
                report_path.parent.mkdir(parents=True, exist_ok=True)
                with open(report_path, 'w', encoding='utf-8') as f:
                    json.dump(report, f, ensure_ascii=False, indent=2, default=str)

                print(f"\n  ✅ Tomato 数据集预处理完成")
                print(f"  原始图片: {report['total_original']}")
                print(f"  处理后: {report['total_processed']}")
                print(f"  损坏文件: {len(report['corrupted_files'])}")
                print(f"  重复文件: {len(report['duplicates'])}")
                print(f"  类别数: {labels_json['num_classes']}")
                print(f"  标签: {labels_json['labels']}")

                # 数据集划分比例
                train_pct = report['splits'].get('train', {}).get('processed', 0) / max(report['total_processed'], 1) * 100
                val_pct = report['splits'].get('val', {}).get('processed', 0) / max(report['total_processed'], 1) * 100
                test_pct = report['splits'].get('test', {}).get('processed', 0) / max(report['total_processed'], 1) * 100
                print(f"  划分比例: train={train_pct:.0f}% val={val_pct:.0f}% test={test_pct:.0f}%")
            else:
                print("  [DRY RUN] 跳过实际处理")
        else:
            print(f"  ⚠️  未找到 yolo_dataset, 请先运行: python scripts/setup_datasets.py")

    # ── 处理 CPSFR 数据集 ──────────────────────────────────
    if args.dataset in ("all", "cpsfr"):
        print_separator("处理 CPSFR 辣椒数据集")

        cpsfr_src = DATASETS_DIR / "yolo_cpsfr"
        cpsfr_dst = PROCESSED_DIR / "cpsfr"

        if cpsfr_src.exists():
            if not args.dry_run:
                report = process_dataset(
                    cpsfr_src,
                    cpsfr_dst,
                    target_size=args.size,
                    augment=args.augment,
                    augment_factor=args.augment_factor,
                    check_quality=not args.no_quality_check,
                )

                labels_json = generate_labels_json(cpsfr_dst)

                report_path = PROCESSED_DIR / "cpsfr" / "preprocess_report.json"
                report_path.parent.mkdir(parents=True, exist_ok=True)
                with open(report_path, 'w', encoding='utf-8') as f:
                    json.dump(report, f, ensure_ascii=False, indent=2, default=str)

                print(f"\n  ✅ CPSFR 数据集预处理完成")
                print(f"  原始图片: {report['total_original']}")
                print(f"  处理后: {report['total_processed']}")
                print(f"  类别数: {labels_json['num_classes']}")

                # 划分比例
                train_pct = report['splits'].get('train', {}).get('processed', 0) / max(report['total_processed'], 1) * 100
                val_pct = report['splits'].get('val', {}).get('processed', 0) / max(report['total_processed'], 1) * 100
                test_pct = report['splits'].get('test', {}).get('processed', 0) / max(report['total_processed'], 1) * 100
                print(f"  划分比例: train={train_pct:.0f}% val={val_pct:.0f}% test={test_pct:.0f}%")
            else:
                print("  [DRY RUN] 跳过实际处理")
        else:
            print(f"  ⚠️  未找到 yolo_cpsfr, 请先运行: python scripts/setup_datasets.py")

    # ── 最终总结 ──────────────────────────────────────────────
    print_separator("预处理完成")
    print(f"""
  📁 处理后数据集: {PROCESSED_DIR}/
    ├── tomato/                # 统一 640x640, 6 类
    │   ├── labels.json
    │   ├── train/
    │   ├── val/
    │   └── test/
    └── cpsfr/                 # 统一 640x640, 4 类
        ├── labels.json
        ├── train/
        ├── val/
        └── test/

  📋 下一步:
    1. 训练 YOLO 分类模型:
       yolo classify train \\
         data={PROCESSED_DIR}/tomato \\
         model=yolov8n-cls.pt \\
         epochs=50 imgsz={args.size}

    2. 使用处理后的数据集更新 detector.py:
       将模型路径指向训练好的 best.pt
""")


if __name__ == "__main__":
    main()
