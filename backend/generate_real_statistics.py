# -*- coding: utf-8 -*-
"""
从真实数据库生成数据集统计信息
适配现有表结构：users, detections, detection_items, histories
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import sqlite3
import json
from typing import Dict
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter


# 病害标签中英文映射
DISEASE_LABELS = {
    "healthy": "健康",
    "leaf_spot": "叶斑病",
    "rust": "锈病",
    "powdery_mildew": "白粉病",
    "early_blight": "早疫病",
    "late_blight": "晚疫病",
    "bacterial_spot": "细菌性斑点病",
    "leaf_mold": "叶霉病",
    "septoria": "斑枯病",
}


class RealDatasetStatistics:
    """从真实 SQLite 数据库生成统计"""

    def __init__(self, db_path: str = "smart_agriculture.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def _table_exists(self, name: str) -> bool:
        row = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (name,)
        ).fetchone()
        return row is not None

    def generate_comprehensive_statistics(self) -> Dict:
        print("🔍 分析真实数据库...")

        stats = {
            "生成时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "数据来源": "真实数据库记录",
            "数据库名称": self.db_path,
            "总览统计": {},
            "用户统计": {},
            "检测统计": {},
            "病害分析": {},
            "时间分析": {},
        }

        print("📊 生成总览统计...")
        stats["总览统计"] = self._get_overview_stats()

        print("👨‍🌾 生成用户统计...")
        stats["用户统计"] = self._get_user_stats()

        print("🔍 生成检测统计...")
        stats["检测统计"] = self._get_detection_stats()

        print("🦠 生成病害分析...")
        stats["病害分析"] = self._get_disease_analysis()

        print("📅 生成时间分析...")
        stats["时间分析"] = self._get_temporal_analysis()

        return stats

    def _get_overview_stats(self) -> Dict:
        cursor = self.conn.cursor()

        total_users = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]

        total_detections = 0
        if self._table_exists("detections"):
            total_detections = cursor.execute(
                "SELECT COUNT(*) FROM detections"
            ).fetchone()[0]

        total_items = 0
        if self._table_exists("detection_items"):
            total_items = cursor.execute(
                "SELECT COUNT(*) FROM detection_items"
            ).fetchone()[0]

        total_histories = 0
        if self._table_exists("histories"):
            total_histories = cursor.execute(
                "SELECT COUNT(*) FROM histories"
            ).fetchone()[0]

        return {
            "总用户数": total_users,
            "总检测记录": total_detections,
            "总检测条目": total_items,
            "总历史记录": total_histories,
            "数据完整度": f"{min(100, (total_items / max(1, total_detections)) * 100):.1f}%"
                        if total_detections > 0 else "0%"
        }

    def _get_user_stats(self) -> Dict:
        cursor = self.conn.cursor()

        roles = cursor.execute(
            "SELECT role, COUNT(*) as count FROM users GROUP BY role"
        ).fetchall()
        role_dist = {row["role"]: row["count"] for row in roles}

        active = cursor.execute(
            "SELECT COUNT(*) FROM users WHERE is_active = 1"
        ).fetchone()[0]
        inactive = cursor.execute(
            "SELECT COUNT(*) FROM users WHERE is_active = 0"
        ).fetchone()[0]

        # 按注册日期统计
        monthly = cursor.execute("""
            SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as count
            FROM users
            WHERE created_at IS NOT NULL
            GROUP BY month ORDER BY month
        """).fetchall()
        monthly_stats = {row["month"]: row["count"] for row in monthly}

        return {
            "角色分布": role_dist,
            "活跃用户": active,
            "停用用户": inactive,
            "月度注册": monthly_stats,
        }

    def _get_detection_stats(self) -> Dict:
        cursor = self.conn.cursor()

        # 检测类型分布
        if self._table_exists("detections"):
            types = cursor.execute(
                "SELECT type, COUNT(*) as count FROM detections GROUP BY type"
            ).fetchall()
            type_dist = {row["type"]: row["count"] for row in types}

            # 视频检测统计
            video_rows = cursor.execute(
                "SELECT total_frames, disease_frames, disease_rate FROM detections WHERE type='video'"
            ).fetchall()
            avg_rate = sum(r["disease_rate"] or 0 for r in video_rows) / max(1, len(video_rows))
        else:
            type_dist = {}
            avg_rate = 0

        # 置信度统计（从 detection_items）
        conf_stats = {}
        if self._table_exists("detection_items"):
            confidences = cursor.execute(
                "SELECT confidence FROM detection_items WHERE confidence IS NOT NULL"
            ).fetchall()
            conf_values = [r["confidence"] for r in confidences]
            if conf_values:
                conf_stats = {
                    "平均置信度": round(sum(conf_values) / len(conf_values), 4),
                    "最高置信度": max(conf_values),
                    "最低置信度": min(conf_values),
                    "高置信度(>0.9)": sum(1 for c in conf_values if c > 0.9),
                    "中等置信度(0.7-0.9)": sum(1 for c in conf_values if 0.7 <= c <= 0.9),
                    "低置信度(<0.7)": sum(1 for c in conf_values if c < 0.7),
                }

        return {
            "检测类型分布": type_dist,
            "视频平均病害率": round(avg_rate, 1),
            "置信度统计": conf_stats,
        }

    def _get_disease_analysis(self) -> Dict:
        cursor = self.conn.cursor()

        # 病害标签分布（从 detection_items）
        disease_dist = {}
        disease_by_type = {}

        if self._table_exists("detection_items"):
            labels = cursor.execute("""
                SELECT di.label, di.label_en, d.type
                FROM detection_items di
                JOIN detections d ON di.detection_id = d.id
            """).fetchall()

            label_counter = Counter()
            type_counter = {}  # {type: Counter}

            for row in labels:
                cn_label = DISEASE_LABELS.get(row["label_en"], row["label"] or "未知")
                label_counter[cn_label] += 1

                dtype = row["type"] or "unknown"
                if dtype not in type_counter:
                    type_counter[dtype] = Counter()
                type_counter[dtype][cn_label] += 1

            disease_dist = dict(label_counter.most_common())
            disease_by_type = {
                t: dict(c.most_common()) for t, c in type_counter.items()
            }

        return {
            "病害分布": disease_dist,
            "按检测类型分布": disease_by_type,
            "已知病害标签": DISEASE_LABELS,
        }

    def _get_temporal_analysis(self) -> Dict:
        cursor = self.conn.cursor()

        # 月度检测趋势
        monthly_detections = {}
        if self._table_exists("detections"):
            rows = cursor.execute("""
                SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as count
                FROM detections
                WHERE created_at IS NOT NULL
                GROUP BY month ORDER BY month
            """).fetchall()
            monthly_detections = {row["month"]: row["count"] for row in rows}

        # 近7天趋势
        today = datetime.now().date()
        daily_trend = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            day_str = day.strftime("%m-%d")
            if self._table_exists("detections"):
                count = cursor.execute("""
                    SELECT COUNT(*) FROM detections
                    WHERE date(created_at) = ?
                """, (day.isoformat(),)).fetchone()[0]
            else:
                count = 0
            daily_trend.append({"date": day_str, "count": count})

        return {
            "月度检测趋势": monthly_detections,
            "近7天趋势": daily_trend,
        }

    def save_statistics(self, stats: Dict, output_path: str = "datasets/dataset_statistics.json"):
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)

        print(f"✅ 统计信息已保存到: {output_file}")
        return output_file

    def close(self):
        self.conn.close()


def main():
    print("=" * 70)
    print("  📊 真实数据库统计信息生成器")
    print("=" * 70)

    db_path = "smart_agriculture.db"
    if not Path(db_path).exists():
        print(f"⚠️  数据库文件 {db_path} 不存在!")
        print("   请确保在 backend/ 目录下运行此脚本")
        return

    analyzer = RealDatasetStatistics(db_path)

    try:
        print("\n🚀 开始生成统计信息...\n")
        stats = analyzer.generate_comprehensive_statistics()

        output_file = analyzer.save_statistics(stats)

        print("\n" + "=" * 70)
        print("  ✅ 统计信息生成完成！")
        print("=" * 70)
        print(f"\n📁 统计文件: {output_file}")

        # 打印摘要
        print("\n📋 摘要:")
        overview = stats.get("总览统计", {})
        for k, v in overview.items():
            print(f"  • {k}: {v}")

    finally:
        analyzer.close()


if __name__ == "__main__":
    main()
