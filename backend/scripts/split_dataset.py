"""
=============================================================================
数据集划分与验证脚本
=============================================================================
功能:
  1. 验证现有 7:2:1 划分是否合理
  2. 检查类别平衡性
  3. 从原始数据重新按 7:2:1 划分（如需要）
  4. 生成 YOLO 训练配置参数推荐
  5. 输出完整的 dataset_summary.yaml 供训练使用

用法:
  # 验证现有划分
  python scripts/split_dataset.py --verify

  # 重新从原始数据按 7:2:1 划分
  python scripts/split_dataset.py --resplit --source "datasets/real_datasets/tomato leaf"

  # 生成训练配置
  python scripts/split_dataset.py --generate-config

=============================================================================
"""
import sys
import io
import os
import json
import random
import argparse
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import numpy as np

# ============================================================================
# 配置
# ============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATASETS_DIR = BASE_DIR / "datasets"
PROCESSED_DIR = DATASETS_DIR / "processed"

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}


def count_class_images(class_dir: Path) -> int:
    """统计一个类目录中的图片数量"""
    if not class_dir.is_dir():
        return 0
    return sum(1 for f in class_dir.iterdir()
               if f.suffix.lower() in ALLOWED_EXTENSIONS and f.is_file())


def get_dataset_summary(dataset_path: Path) -> Dict:
    """
    获取数据集的完整统计信息

    返回:
      {
        "classes": {class_name: {"train": N, "val": N, "test": N}},
        "total": {"train": N, "val": N, "test": N},
        "ratios": {"train": %, "val": %, "test": %},
        "class_balance": {"balanced": bool, "min_per_class": N, "max_per_class": N},
        "issues": [str, ...]
      }
    """
    summary = {
        "path": str(dataset_path),
        "classes": defaultdict(lambda: {"train": 0, "val": 0, "test": 0}),
        "total": {"train": 0, "val": 0, "test": 0},
        "ratios": {},
        "class_balance": {},
        "issues": [],
    }

    for split in ["train", "val", "test"]:
        split_dir = dataset_path / split
        if not split_dir.exists():
            summary["issues"].append(f"{split}/ 目录不存在")
            continue

        for class_dir in split_dir.iterdir():
            if not class_dir.is_dir():
                continue
            class_name = class_dir.name
            count = count_class_images(class_dir)
            summary["classes"][class_name][split] = count
            summary["total"][split] += count

    # 标准化 classes (defaultdict -> dict)
    summary["classes"] = dict(summary["classes"])

    # 计算比例
    total_all = sum(summary["total"].values())
    if total_all > 0:
        for split in ["train", "val", "test"]:
            summary["ratios"][split] = round(
                summary["total"][split] / total_all * 100, 1
            )

    # 检查类别平衡
    class_totals = {}
    for cls_name, splits in summary["classes"].items():
        class_totals[cls_name] = sum(splits.values())

    if class_totals:
        min_cls = min(class_totals, key=class_totals.get)
        max_cls = max(class_totals, key=class_totals.get)
        min_count = class_totals[min_cls]
        max_count = class_totals[max_cls]

        summary["class_balance"] = {
            "balanced": max_count <= min_count * 2,  # 最大不超过最小的2倍
            "min_class": min_cls,
            "min_count": min_count,
            "max_class": max_cls,
            "max_count": max_count,
            "mean": round(np.mean(list(class_totals.values())), 1),
            "std": round(np.std(list(class_totals.values())), 1),
        }

        if max_count > min_count * 2:
            summary["issues"].append(
                f"类别不平衡: {max_cls}({max_count}) 是 {min_cls}({min_count}) 的 "
                f"{max_count/min_count:.1f} 倍"
            )

    # 检查预期比例
    expected = {"train": 70, "val": 20, "test": 10}
    for split, exp_pct in expected.items():
        actual = summary["ratios"].get(split, 0)
        if abs(actual - exp_pct) > 10:  # 容忍 10% 偏差
            summary["issues"].append(
                f"{split} 比例偏差: 预期 {exp_pct}%, 实际 {actual}%"
            )

    return summary


def resplit_dataset(
    src_dir: Path,
    dst_dir: Path,
    ratios: Tuple[float, float, float] = (0.7, 0.2, 0.1),
    seed: int = 42,
) -> Dict:
    """
    从原始分类图片目录重新按比例划分

    参数:
      src_dir: 源目录 (包含按类名组织的子目录)
      dst_dir: 输出目录
      ratios: (train, val, test) 比例
      seed: 随机种子

    期望 src_dir 结构:
      src_dir/
      ├── class_A/
      │   ├── img1.jpg
      │   └── img2.jpg
      ├── class_B/
      │   └── ...
      └── class_C/
          └── ...
    """
    random.seed(seed)

    report = {
        "source": str(src_dir),
        "destination": str(dst_dir),
        "ratios": {"train": ratios[0], "val": ratios[1], "test": ratios[2]},
        "seed": seed,
        "classes": {},
    }

    # 收集所有图片
    all_images = defaultdict(list)
    for item in sorted(src_dir.iterdir()):
        if item.is_dir():
            class_name = item.name
            for img_file in item.iterdir():
                if img_file.suffix.lower() in ALLOWED_EXTENSIONS:
                    all_images[class_name].append(img_file)

    if not all_images:
        report["error"] = "未找到任何图片"
        return report

    # 对每个类分别划分
    for class_name, images in sorted(all_images.items()):
        random.shuffle(images)
        n = len(images)
        n_train = int(n * ratios[0])
        n_val = int(n * ratios[1])
        # n_test = n - n_train - n_val

        report["classes"][class_name] = {
            "total": n,
            "train": n_train,
            "val": n_val,
            "test": n - n_train - n_val,
        }

        # 创建目录并复制文件
        for split_name, split_images in [
            ("train", images[:n_train]),
            ("val", images[n_train:n_train + n_val]),
            ("test", images[n_train + n_val:]),
        ]:
            dst_split = dst_dir / split_name / class_name
            dst_split.mkdir(parents=True, exist_ok=True)

            for src_file in split_images:
                dst_file = dst_split / src_file.name
                if not dst_file.exists():
                    shutil.copy2(src_file, dst_file)

    # 汇总
    report["total"] = {
        "train": sum(c["train"] for c in report["classes"].values()),
        "val": sum(c["val"] for c in report["classes"].values()),
        "test": sum(c["test"] for c in report["classes"].values()),
    }
    total_all = sum(report["total"].values())
    report["actual_ratios"] = {
        "train": round(report["total"]["train"] / total_all * 100, 1),
        "val": round(report["total"]["val"] / total_all * 100, 1),
        "test": round(report["total"]["test"] / total_all * 100, 1),
    }

    return report


def generate_training_config(dataset_path: Path, output_path: Path) -> Dict:
    """生成 YOLO 训练配置文件"""
    summary = get_dataset_summary(dataset_path)

    # 收集类名
    all_classes = set()
    for split in ["train", "val", "test"]:
        split_dir = dataset_path / split
        if split_dir.exists():
            for d in split_dir.iterdir():
                if d.is_dir():
                    all_classes.add(d.name)

    class_names = sorted(all_classes)

    # 计算推荐参数
    total_images = sum(summary["total"].values())
    class_counts = [sum(summary["classes"].get(c, {"train": 0, "val": 0, "test": 0}).values()) for c in class_names]
    min_class_count = min(class_counts) if class_counts else 0

    # 训练配置推荐
    config = {
        "dataset": {
            "path": str(dataset_path.absolute()),
            "train": "train",
            "val": "val",
            "test": "test",
            "nc": len(class_names),
            "names": class_names,
        },
        "training_recommendations": {
            "model": "yolov8n-cls.pt" if total_images < 5000 else "yolov8s-cls.pt",
            "epochs": 50 if total_images > 1000 else 100,
            "batch_size": 16 if total_images > 2000 else 8,
            "imgsz": 640,
            "optimizer": "AdamW",
            "lr0": 0.001,
            "weight_decay": 0.0005,
            "warmup_epochs": 3,
            "patience": 10,  # early stopping
            "augment": total_images < 3000,  # 小数据集启用增强
            "notes": [],
        },
        "dataset_stats": summary,
    }

    # 根据数据集特征给出建议
    if total_images < 1000:
        config["training_recommendations"]["notes"].append(
            "数据集较小 (<1000张), 建议使用更强的数据增强和迁移学习"
        )
        config["training_recommendations"]["augment"] = True
        config["training_recommendations"]["epochs"] = 100

    if not summary["class_balance"].get("balanced", True):
        config["training_recommendations"]["notes"].append(
            "类别不平衡, 建议使用 class_weights 或 oversampling"
        )

    if min_class_count < 20:
        config["training_recommendations"]["notes"].append(
            f"最少类别仅 {min_class_count} 张, 建议收集更多数据"
        )

    # 保存配置
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# YOLOv8 训练配置\n")
        f.write(f"# 自动生成于: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# 数据集: {dataset_path}\n")
        f.write(f"# 总图片数: {total_images}\n")
        f.write(f"# 类别数: {len(class_names)}\n\n")

        f.write(f"# 数据路径\n")
        f.write(f"path: {config['dataset']['path']}\n")
        f.write(f"train: {config['dataset']['train']}\n")
        f.write(f"val: {config['dataset']['val']}\n")
        f.write(f"test: {config['dataset']['test']}\n\n")

        f.write(f"# 类别\n")
        f.write(f"nc: {len(class_names)}\n")
        f.write(f"names:\n")
        for i, name in enumerate(class_names):
            f.write(f"  {i}: {name}\n")

        f.write(f"\n# 训练推荐参数\n")
        f.write(f"# model: {config['training_recommendations']['model']}\n")
        f.write(f"# epochs: {config['training_recommendations']['epochs']}\n")
        f.write(f"# batch: {config['training_recommendations']['batch_size']}\n")
        f.write(f"# imgsz: {config['training_recommendations']['imgsz']}\n")
        f.write(f"#\n")
        f.write(f"# 命令行:\n")
        f.write(f"# yolo classify train \\\n")
        f.write(f"#   data={config['dataset']['path']} \\\n")
        f.write(f"#   model={config['training_recommendations']['model']} \\\n")
        f.write(f"#   epochs={config['training_recommendations']['epochs']} \\\n")
        f.write(f"#   batch={config['training_recommendations']['batch_size']} \\\n")
        f.write(f"#   imgsz={config['training_recommendations']['imgsz']}\n")

    return config


def print_separator(title: str):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def main():
    parser = argparse.ArgumentParser(description="数据集划分与验证")
    parser.add_argument("--verify", action="store_true", default=True,
                        help="验证现有划分 (默认)")
    parser.add_argument("--resplit", action="store_true",
                        help="重新划分数据集")
    parser.add_argument("--source", type=str,
                        help="重新划分时的源目录")
    parser.add_argument("--dst", type=str,
                        help="重新划分时的目标目录")
    parser.add_argument("--generate-config", action="store_true",
                        help="生成 YOLO 训练配置")
    parser.add_argument("--all", action="store_true",
                        help="执行所有操作 (验证+配置生成)")
    args = parser.parse_args()

    print("=" * 60)
    print("  智慧农业病害防治系统 — 数据集划分与验证")
    print("=" * 60)
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    datasets_to_check = []

    # 检查 tomato 数据集
    tomato_orig = DATASETS_DIR / "real_datasets" / "tomato leaf"
    tomato_yolo = DATASETS_DIR / "yolo_dataset"
    tomato_proc = PROCESSED_DIR / "tomato"

    # 检查 cpsfr 数据集
    cpsfr_yolo = DATASETS_DIR / "yolo_cpsfr"
    cpsfr_proc = PROCESSED_DIR / "cpsfr"

    # 确定要验证的数据集
    if tomato_proc.exists():
        datasets_to_check.append(("Tomato (Processed)", tomato_proc))
    elif tomato_yolo.exists():
        datasets_to_check.append(("Tomato (YOLO)", tomato_yolo))
    elif tomato_orig.exists():
        datasets_to_check.append(("Tomato (Original)", tomato_orig))

    if cpsfr_proc.exists():
        datasets_to_check.append(("CPSFR (Processed)", cpsfr_proc))
    elif cpsfr_yolo.exists():
        datasets_to_check.append(("CPSFR (YOLO)", cpsfr_yolo))

    # ── 1. 验证划分 ──────────────────────────────────────
    if args.verify or args.all:
        print_separator("数据集划分验证")

        for name, path in datasets_to_check:
            print(f"\n  📊 {name}: {path}")
            summary = get_dataset_summary(path)

            total = sum(summary["total"].values())
            print(f"  总图片: {total}")
            print(f"  类别数: {len(summary['classes'])}")

            # 划分比例
            print(f"  划分比例:")
            for split, ratio in summary["ratios"].items():
                bar = "█" * int(ratio / 2)
                count = summary["total"][split]
                expected = {"train": 70, "val": 20, "test": 10}.get(split, 0)
                status = "✅" if abs(ratio - expected) <= 10 else "⚠️"
                print(f"    {status} {split:5s}: {ratio:5.1f}% ({count:4d} 张) {bar}")

            # 每类详情
            print(f"  各类详情:")
            for cls, counts in sorted(summary["classes"].items()):
                cls_total = sum(counts.values())
                t, v, te = counts["train"], counts["val"], counts["test"]
                print(f"    {cls:25s}: total={cls_total:4d}  "
                      f"train={t:4d}({t/max(cls_total,1)*100:.0f}%)  "
                      f"val={v:4d}  test={te:4d}")

            # 类别平衡
            if summary["class_balance"]:
                cb = summary["class_balance"]
                balance_status = "✅ 平衡" if cb["balanced"] else "⚠️ 不平衡"
                print(f"  类别平衡: {balance_status}")
                print(f"    最少: {cb['min_class']} ({cb['min_count']} 张)")
                print(f"    最多: {cb['max_class']} ({cb['max_count']} 张)")
                print(f"    均值: {cb['mean']}, 标准差: {cb['std']}")

            # 问题
            if summary["issues"]:
                print(f"  ⚠️  发现问题:")
                for issue in summary["issues"]:
                    print(f"    - {issue}")
            else:
                print(f"  ✅ 无问题")

    # ── 2. 重新划分 ───────────────────────────────────────
    if args.resplit:
        if not args.source:
            print("\n  ❌ --resplit 需要指定 --source")
            return

        print_separator("重新划分数据集 (7:2:1)")

        src = Path(args.source)
        dst = Path(args.dst) if args.dst else DATASETS_DIR / f"{src.name}_resplit"

        if not src.exists():
            print(f"  ❌ 源目录不存在: {src}")
            return

        # 智能检测目录结构: 可能已经是分类子目录，也可能是嵌套的
        # 检查是否包含直接的类子目录
        has_class_dirs = any(
            item.is_dir() and any(
                f.suffix.lower() in ALLOWED_EXTENSIONS for f in item.iterdir()
            )
            for item in src.iterdir()
        )

        if not has_class_dirs:
            # 检查是否是嵌套结构 (如 CPSFR_NAME/CPSFR_NAME/)
            for item in src.iterdir():
                if item.is_dir():
                    inner = item / item.name
                    if inner.exists() and inner.is_dir():
                        # 使用内层目录
                        src = inner.parent
                        break

        print(f"  源目录: {src}")
        print(f"  目标目录: {dst}")
        print(f"  比例: 70:20:10")

        report = resplit_dataset(src, dst, ratios=(0.7, 0.2, 0.1))

        if "error" in report:
            print(f"  ❌ {report['error']}")
        else:
            print(f"\n  ✅ 划分完成!")
            print(f"  总图片: {sum(report['total'].values())}")
            print(f"  类别数: {len(report['classes'])}")
            print(f"  实际比例:")
            for split, ratio in report["actual_ratios"].items():
                print(f"    {split}: {ratio}% ({report['total'][split]} 张)")
            print(f"\n  各类划分:")
            for cls, counts in report["classes"].items():
                print(f"    {cls}: total={counts['total']} → "
                      f"train={counts['train']} val={counts['val']} test={counts['test']}")

    # ── 3. 生成训练配置 ────────────────────────────────────
    if args.generate_config or args.all:
        print_separator("生成 YOLO 训练配置")

        for name, path in datasets_to_check:
            config_path = path / "training_config.yaml"
            config = generate_training_config(path, config_path)
            rec = config["training_recommendations"]

            print(f"\n  📝 {name}: {config_path}")
            print(f"  推荐模型: {rec['model']}")
            print(f"  推荐 epochs: {rec['epochs']}")
            print(f"  推荐 batch_size: {rec['batch_size']}")
            print(f"  图像尺寸: {rec['imgsz']}")
            print(f"  数据增强: {'是' if rec['augment'] else '否'}")
            if rec["notes"]:
                print(f"  备注:")
                for note in rec["notes"]:
                    print(f"    💡 {note}")

            print(f"\n  训练命令:")
            print(f"    yolo classify train \\")
            print(f"      data={config['dataset']['path']} \\")
            print(f"      model={rec['model']} \\")
            print(f"      epochs={rec['epochs']} \\")
            print(f"      batch={rec['batch_size']} \\")
            print(f"      imgsz={rec['imgsz']}")

    # ── 4. 保存综合报告 ────────────────────────────────────
    print_separator("保存综合报告")

    full_report = {
        "timestamp": datetime.now().isoformat(),
        "datasets": {},
    }

    for name, path in datasets_to_check:
        summary = get_dataset_summary(path)
        full_report["datasets"][name] = {
            "path": str(path),
            "summary": summary,
        }

    report_path = DATASETS_DIR / "split_validation_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(full_report, f, ensure_ascii=False, indent=2, default=str)

    print(f"  📊 报告已保存: {report_path}")

    # 最终总结
    print_separator("总结")
    print(f"""
  📋 数据集状态概览:
""")
    for name, path in datasets_to_check:
        summary = get_dataset_summary(path)
        total = sum(summary["total"].values())
        classes = len(summary["classes"])
        ratios = summary["ratios"]
        balanced = "✅" if summary["class_balance"].get("balanced", False) else "⚠️"

        print(f"  {name:25s}: {total:5d} 张 | {classes} 类 | "
              f"train={ratios.get('train',0):.0f}% val={ratios.get('val',0):.0f}% "
              f"test={ratios.get('test',0):.0f}% | {balanced}")

    print(f"""
  📁 所有报告文件:
    {DATASETS_DIR}/dataset_setup_report.json       - 数据集组织报告
    {DATASETS_DIR}/split_validation_report.json     - 划分验证报告
    {PROCESSED_DIR}/*/preprocess_report.json        - 预处理报告
    {PROCESSED_DIR}/*/training_config.yaml          - 训练配置
""")


if __name__ == "__main__":
    main()
