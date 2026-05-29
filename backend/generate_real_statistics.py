"""
从真实数据库生成数据集统计信息
替代现有的dataset_statistics.json
"""
# -*- coding: utf-8 -*-
import sys
import io

# 强制标准输出使用 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import sqlite3
import json
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
from collections import Counter

class RealDatasetStatistics:
    def __init__(self, db_path: str = "smart_agriculture.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
    
    def generate_comprehensive_statistics(self) -> Dict:
        """从真实数据库生成综合统计信息"""
        print("🔍 分析真实数据库...")
        
        stats = {
            "生成时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "数据来源": "真实数据库记录",
            "数据库名称": self.db_path,
            "总览统计": {},
            "用户统计": {},
            "检测统计": {},
            "防治统计": {},
            "评估统计": {},
            "病害分析": {},
            "作物分析": {},
            "地区分析": {},
            "时间分析": {},
            "效果分析": {},
            "环境分析": {}
        }
        
        # 1. 总览统计
        print("📊 生成总览统计...")
        stats["总览统计"] = self._get_overview_stats()
        
        # 2. 用户统计
        print("👨‍🌾 生成用户统计...")
        stats["用户统计"] = self._get_user_stats()
        
        # 3. 检测统计
        print("🔍 生成检测统计...")
        stats["检测统计"] = self._get_detection_stats()
        
        # 4. 防治统计
        print("💊 生成防治统计...")
        stats["防治统计"] = self._get_treatment_stats()
        
        # 5. 评估统计
        print("📈 生成评估统计...")
        stats["评估统计"] = self._get_evaluation_stats()
        
        # 6. 病害分析
        print("🦠 生成病害分析...")
        stats["病害分析"] = self._get_disease_analysis()
        
        # 7. 作物分析
        print("🌾 生成作物分析...")
        stats["作物分析"] = self._get_crop_analysis()
        
        # 8. 地区分析
        print("📍 生成地区分析...")
        stats["地区分析"] = self._get_location_analysis()
        
        # 9. 时间分析
        print("📅 生成时间分析...")
        stats["时间分析"] = self._get_temporal_analysis()
        
        # 10. 效果分析
        print("🎯 生成效果分析...")
        stats["效果分析"] = self._get_effectiveness_analysis()
        
        # 11. 环境分析
        print("🌡️ 生成环境分析...")
        stats["环境分析"] = self._get_environmental_analysis()
        
        return stats
    
    def _get_overview_stats(self) -> Dict:
        """获取总览统计"""
        cursor = self.conn.cursor()
        
        total_users = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_detections = cursor.execute("SELECT COUNT(*) FROM detections").fetchone()[0]
        total_treatments = cursor.execute("SELECT COUNT(*) FROM treatments").fetchone()[0]
        total_evaluations = cursor.execute("SELECT COUNT(*) FROM evaluations").fetchone()[0]
        
        return {
            "总用户数": total_users,
            "总检测记录": total_detections,
            "总防治记录": total_treatments,
            "总评估记录": total_evaluations,
            "数据完整度": f"{min(100, (total_treatments / max(1, total_detections)) * 100):.1f}%"
        }
    
    def _get_user_stats(self) -> Dict:
        """获取用户统计"""
        cursor = self.conn.cursor()
        
        users = cursor.execute("SELECT location, farm_size, experience_years FROM users").fetchall()
        
        locations = Counter(user["location"] for user in users)
        farm_sizes = [user["farm_size"] for user in users]
        experience = [user["experience_years"] for user in users]
        
        return {
            "地区分布": dict(locations.most_common()),
            "农场规模统计": {
                "平均规模": round(sum(farm_sizes) / len(farm_sizes), 1) if farm_sizes else 0,
                "最小规模": min(farm_sizes) if farm_sizes else 0,
                "最大规模": max(farm_sizes) if farm_sizes else 0,
                "规模分布": {
                    "小型农场(<10亩)": sum(1 for size in farm_sizes if size < 10),
                    "中型农场(10-30亩)": sum(1 for size in farm_sizes if 10 <= size < 30),
                    "大型农场(>30亩)": sum(1 for size in farm_sizes if size >= 30)
                }
            },
            "种植经验统计": {
                "平均经验": round(sum(experience) / len(experience), 1) if experience else 0,
                "新手(<3年)": sum(1 for exp in experience if exp < 3),
                "熟练(3-10年)": sum(1 for exp in experience if 3 <= exp < 10),
                "专家(>10年)": sum(1 for exp in experience if exp >= 10)
            }
        }
    
    def _get_detection_stats(self) -> Dict:
        """获取检测统计"""
        cursor = self.conn.cursor()
        
        types = cursor.execute("SELECT type, COUNT(*) as count FROM detections GROUP BY type").fetchall()
        type_dist = {row["type"]: row["count"] for row in types}
        
        severities = cursor.execute("SELECT severity, COUNT(*) as count FROM detections GROUP BY severity").fetchall()
        severity_dist = {row["severity"]: row["count"] for row in severities}
        
        confidences = cursor.execute("SELECT confidence FROM detections").fetchall()
        conf_values = [row["confidence"] for row in confidences]
        
        return {
            "检测类型分布": type_dist,
            "严重程度分布": severity_dist,
            "置信度统计": {
                "平均置信度": round(sum(conf_values) / len(conf_values), 4) if conf_values else 0,
                "最高置信度": max(conf_values) if conf_values else 0,
                "最低置信度": min(conf_values) if conf_values else 0,
                "高置信度检测(>0.9)": sum(1 for conf in conf_values if conf > 0.9),
                "中等置信度检测(0.7-0.9)": sum(1 for conf in conf_values if 0.7 <= conf <= 0.9),
                "低置信度检测(<0.7)": sum(1 for conf in conf_values if conf < 0.7)
            }
        }
    
    def _get_treatment_stats(self) -> Dict:
        """获取防治统计"""
        cursor = self.conn.cursor()
        
        crops = cursor.execute("SELECT crop_type, COUNT(*) as count FROM treatments GROUP BY crop_type").fetchall()
        crop_dist = {row["crop_type"]: row["count"] for row in crops}
        
        diseases = cursor.execute("SELECT disease, COUNT(*) as count FROM treatments GROUP BY disease").fetchall()
        disease_dist = {row["disease"]: row["count"] for row in diseases}
        
        all_treatments = cursor.execute("SELECT treatment_plan FROM treatments").fetchall()
        methods = []
        for row in all_treatments:
            try:
                plan = json.loads(row["treatment_plan"])
                methods.append(plan.get("method", "未知"))
            except:
                methods.append("未知")
        
        method_dist = Counter(methods)
        
        costs = cursor.execute("SELECT cost FROM treatments").fetchall()
        cost_values = [row["cost"] for row in costs]
        
        return {
            "作物分布": crop_dist,
            "病害分布": disease_dist,
            "防治方法分布": dict(method_dist.most_common()),
            "成本统计": {
                "平均成本": round(sum(cost_values) / len(cost_values), 2) if cost_values else 0,
                "总成本": round(sum(cost_values), 2) if cost_values else 0,
                "成本区间": {
                    "低成本(<100元)": sum(1 for cost in cost_values if cost < 100),
                    "中等成本(100-200元)": sum(1 for cost in cost_values if 100 <= cost < 200),
                    "高成本(>200元)": sum(1 for cost in cost_values if cost >= 200)
                }
            }
        }
    
    def _get_evaluation_stats(self) -> Dict:
        """获取评估统计"""
        cursor = self.conn.cursor()
        
        levels = cursor.execute("SELECT evaluation_level, COUNT(*) as count FROM evaluations GROUP BY evaluation_level").fetchall()
        level_dist = {row["evaluation_level"]: row["count"] for row in levels}
        
        scores = cursor.execute("SELECT effectiveness_score FROM evaluations").fetchall()
        score_values = [row["effectiveness_score"] for row in scores]
        
        changes = cursor.execute("SELECT severity_change, COUNT(*) as count FROM evaluations GROUP BY severity_change").fetchall()
        change_dist = {row["severity_change"]: row["count"] for row in changes}
        
        cost_effects = cursor.execute("SELECT cost_effectiveness FROM evaluations").fetchall()
        ce_values = [row["cost_effectiveness"] for row in cost_effects]
        
        return {
            "评估等级分布": level_dist,
            "效果分数统计": {
                "平均效果分数": round(sum(score_values) / len(score_values), 2) if score_values else 0,
                "最高效果分数": max(score_values) if score_values else 0,
                "最低效果分数": min(score_values) if score_values else 0,
                "优秀效果(>0.85)": sum(1 for score in score_values if score > 0.85),
                "良好效果(0.7-0.85)": sum(1 for score in score_values if 0.7 <= score <= 0.85),
                "一般效果(0.55-0.7)": sum(1 for score in score_values if 0.55 <= score < 0.7),
                "较差效果(<0.55)": sum(1 for score in score_values if score < 0.55)
            },
            "严重程度变化": change_dist,
            "成本效益统计": {
                "平均成本效益": round(sum(ce_values) / len(ce_values), 2) if ce_values else 0,
                "高效益(>0.5)": sum(1 for ce in ce_values if ce > 0.5),
                "中等效益(0.3-0.5)": sum(1 for ce in ce_values if 0.3 <= ce <= 0.5),
                "低效益(<0.3)": sum(1 for ce in ce_values if ce < 0.3)
            }
        }
    
    def _get_disease_analysis(self) -> Dict:
        """获取病害分析"""
        cursor = self.conn.cursor()
        
        disease_crop = cursor.execute("""
            SELECT disease_label, crop_type, COUNT(*) as count 
            FROM detections 
            GROUP BY disease_label, crop_type
        """).fetchall()
        
        disease_crop_matrix = {}
        for row in disease_crop:
            disease = row["disease_label"]
            crop = row["crop_type"]
            if disease not in disease_crop_matrix:
                disease_crop_matrix[disease] = {}
            disease_crop_matrix[disease][crop] = row["count"]
        
        disease_severity = cursor.execute("""
            SELECT disease_label, severity, COUNT(*) as count 
            FROM detections 
            GROUP BY disease_label, severity
        """).fetchall()
        
        disease_severity_dist = {}
        for row in disease_severity:
            disease = row["disease_label"]
            severity = row["severity"]
            if disease not in disease_severity_dist:
                disease_severity_dist[disease] = {}
            disease_severity_dist[disease][severity] = row["count"]
        
        return {
            "病害-作物关联": disease_crop_matrix,
            "病害严重程度分布": disease_severity_dist
        }
    
    def _get_crop_analysis(self) -> Dict:
        """获取作物分析"""
        cursor = self.conn.cursor()
        
        crop_detections = cursor.execute("""
            SELECT crop_type, COUNT(*) as count,
                   AVG(confidence) as avg_confidence
            FROM detections 
            GROUP BY crop_type
        """).fetchall()
        
        crop_stats = {}
        for row in crop_detections:
            crop_stats[row["crop_type"]] = {
                "检测次数": row["count"],
                "平均置信度": round(row["avg_confidence"], 4) if row["avg_confidence"] else 0
            }
        
        crop_effectiveness = cursor.execute("""
            SELECT crop_type, AVG(effectiveness_score) as avg_effectiveness,
                   AVG(cost) as avg_cost
            FROM treatments 
            GROUP BY crop_type
        """).fetchall()
        
        for row in crop_effectiveness:
            crop = row["crop_type"]
            if crop not in crop_stats:
                crop_stats[crop] = {}
            crop_stats[crop]["平均防治效果"] = round(row["avg_effectiveness"], 2) if row["avg_effectiveness"] else 0
            crop_stats[crop]["平均防治成本"] = round(row["avg_cost"], 2) if row["avg_cost"] else 0
        
        return crop_stats
    
    def _get_location_analysis(self) -> Dict:
        """获取地区分析"""
        cursor = self.conn.cursor()
        
        location_detections = cursor.execute("""
            SELECT u.location, COUNT(d.id) as detection_count,
                   COUNT(t.id) as treatment_count
            FROM users u
            LEFT JOIN detections d ON u.id = d.user_id
            LEFT JOIN treatments t ON d.id = t.detection_id
            GROUP BY u.location
        """).fetchall()
        
        location_stats = {}
        for row in location_detections:
            location_stats[row["location"]] = {
                "检测次数": row["detection_count"],
                "防治次数": row["treatment_count"]
            }
        
        return location_stats
    
    def _get_temporal_analysis(self) -> Dict:
        """获取时间分析"""
        cursor = self.conn.cursor()
        
        monthly_detections = cursor.execute("""
            SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as count
            FROM detections
            GROUP BY month
            ORDER BY month
        """).fetchall()
        
        monthly_stats = {row["month"]: row["count"] for row in monthly_detections}
        
        return {
            "月度统计": monthly_stats
        }
    
    def _get_effectiveness_analysis(self) -> Dict:
        """获取效果分析"""
        cursor = self.conn.cursor()
        
        disease_effectiveness = cursor.execute("""
            SELECT disease, AVG(effectiveness_score) as avg_effectiveness,
                   COUNT(*) as treatment_count
            FROM treatments
            GROUP BY disease
            ORDER BY avg_effectiveness DESC
        """).fetchall()
        
        disease_effect_stats = {}
        for row in disease_effectiveness:
            disease_effect_stats[row["disease"]] = {
                "平均效果": round(row["avg_effectiveness"], 2) if row["avg_effectiveness"] else 0,
                "防治次数": row["treatment_count"]
            }
        
        severity_effectiveness = cursor.execute("""
            SELECT severity, AVG(effectiveness_score) as avg_effectiveness,
                   COUNT(*) as count
            FROM treatments
            GROUP BY severity
        """).fetchall()
        
        severity_effect_stats = {}
        for row in severity_effectiveness:
            severity_effect_stats[row["severity"]] = {
                "平均效果": round(row["avg_effectiveness"], 2) if row["avg_effectiveness"] else 0,
                "样本数量": row["count"]
            }
        
        return {
            "各病害防治效果": disease_effect_stats,
            "严重程度与效果关系": severity_effect_stats
        }
    
    def _get_environmental_analysis(self) -> Dict:
        """获取环境分析"""
        cursor = self.conn.cursor()
        
        all_weather = cursor.execute("SELECT weather_data FROM detections").fetchall()
        
        weather_conditions = []
        temperatures = []
        humidities = []
        
        for row in all_weather:
            try:
                weather = json.loads(row["weather_data"])
                weather_conditions.append(weather.get("condition", "未知"))
                temperatures.append(weather.get("temperature", 0))
                humidities.append(weather.get("humidity", 0))
            except:
                continue
        
        weather_dist = Counter(weather_conditions)
        
        all_soil = cursor.execute("SELECT soil_data FROM detections").fetchall()
        
        ph_values = []
        moisture_values = []
        
        for row in all_soil:
            try:
                soil = json.loads(row["soil_data"])
                ph_values.append(soil.get("ph", 0))
                moisture_values.append(soil.get("moisture", 0))
            except:
                continue
        
        return {
            "天气条件分布": dict(weather_dist.most_common()),
            "温度统计": {
                "平均温度": round(sum(temperatures) / len(temperatures), 1) if temperatures else 0,
                "最高温度": max(temperatures) if temperatures else 0,
                "最低温度": min(temperatures) if temperatures else 0
            },
            "湿度统计": {
                "平均湿度": round(sum(humidities) / len(humidities), 1) if humidities else 0,
                "最高湿度": max(humidities) if humidities else 0,
                "最低湿度": min(humidities) if humidities else 0
            },
            "土壤pH统计": {
                "平均pH": round(sum(ph_values) / len(ph_values), 1) if ph_values else 0,
                "pH范围": f"{min(ph_values):.1f}-{max(ph_values):.1f}" if ph_values else "未知"
            },
            "土壤湿度统计": {
                "平均湿度": round(sum(moisture_values) / len(moisture_values), 1) if moisture_values else 0,
                "湿度范围": f"{min(moisture_values):.1f}-{max(moisture_values):.1f}" if moisture_values else "未知"
            }
        }
    
    def save_statistics(self, stats: Dict, output_path: str = "datasets/dataset_statistics.json"):
        """保存统计信息"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 统计信息已保存到: {output_file}")
        return output_file
    
    def close(self):
        """关闭数据库连接"""
        self.conn.close()

def main():
    print("="*70)
    print("  📊 真实数据库统计信息生成器")
    print("="*70)
    
    analyzer = RealDatasetStatistics("smart_agriculture.db")
    
    try:
        print("\n🚀 开始生成统计信息...\n")
        stats = analyzer.generate_comprehensive_statistics()
        
        output_file = analyzer.save_statistics(stats)
        
        print("\n" + "="*70)
        print("  ✅ 统计信息生成完成！")
        print("="*70)
        print(f"\n📁 统计文件: {output_file}")
        
    finally:
        analyzer.close()

if __name__ == "__main__":
    main()