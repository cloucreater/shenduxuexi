from typing import Dict, List, Any

TREATMENT_DATABASE = {
    "叶斑病": {
        "light": {
            "pesticides": [
                {"name": "多菌灵", "concentration": "50% 可湿性粉剂 800-1000倍液", "method": "叶面喷雾"},
                {"name": "百菌清", "concentration": "75% 可湿性粉剂 600-800倍液", "method": "叶面喷雾"}
            ],
            "farming_tips": [
                "加强通风透光，降低田间湿度",
                "及时清除病叶，减少病原基数",
                "避免大水漫灌，提倡滴灌"
            ],
            "safety_interval": "施药后7-10天方可采收"
        },
        "medium": {
            "pesticides": [
                {"name": "苯醚甲环唑", "concentration": "10% 水分散粒剂 1500-2000倍液", "method": "叶面喷雾"},
                {"name": "戊唑醇", "concentration": "43% 悬浮剂 3000-4000倍液", "method": "叶面喷雾"}
            ],
            "farming_tips": [
                "立即摘除严重病叶",
                "加强肥水管理，增强植株抗病力",
                "避免偏施氮肥，适当增施磷钾肥"
            ],
            "safety_interval": "施药后10-14天方可采收"
        },
        "severe": {
            "pesticides": [
                {"name": "氟硅唑", "concentration": "40% 乳油 8000-10000倍液", "method": "叶面喷雾"},
                {"name": "咪鲜胺", "concentration": "25% 乳油 1000-1500倍液", "method": "叶面喷雾"}
            ],
            "farming_tips": [
                "拔除严重病株，带出田外销毁",
                "全田喷雾处理，防止蔓延",
                "考虑轮作换茬，减少病原积累"
            ],
            "safety_interval": "施药后14-21天方可采收"
        }
    },
    "锈病": {
        "light": {
            "pesticides": [
                {"name": "粉锈宁", "concentration": "20% 乳油 1500-2000倍液", "method": "叶面喷雾"},
                {"name": "三唑酮", "concentration": "15% 可湿性粉剂 1000-1200倍液", "method": "叶面喷雾"}
            ],
            "farming_tips": [
                "及时浇水，保证田间湿度适宜",
                "增施有机肥，提高植株抗病能力"
            ],
            "safety_interval": "施药后7天方可采收"
        },
        "medium": {
            "pesticides": [
                {"name": "丙环唑", "concentration": "25% 乳油 2000-2500倍液", "method": "叶面喷雾"},
                {"name": "烯唑醇", "concentration": "12.5% 可湿性粉剂 2000-3000倍液", "method": "叶面喷雾"}
            ],
            "farming_tips": [
                "摘除底部老叶，改善通风条件",
                "避免在早晨露水未干时进行农事操作"
            ],
            "safety_interval": "施药后10-14天方可采收"
        },
        "severe": {
            "pesticides": [
                {"name": "腈菌唑", "concentration": "12.5% 乳油 1500-2000倍液", "method": "叶面喷雾"},
                {"name": "氟环唑", "concentration": "50% 悬浮剂 1500-2000倍液", "method": "叶面喷雾"}
            ],
            "farming_tips": [
                "严重病田块考虑提前收获",
                "收获后彻底清除残体",
                "与非寄主作物轮作2-3年"
            ],
            "safety_interval": "施药后14-21天方可采收"
        }
    },
    "白粉病": {
        "light": {
            "pesticides": [
                {"name": "多抗霉素", "concentration": "10% 可湿性粉剂 500-800倍液", "method": "叶面喷雾"},
                {"name": "武夷菌素", "concentration": "2% 水剂 150-200倍液", "method": "叶面喷雾"}
            ],
            "farming_tips": [
                "加强通风，降低棚内湿度",
                "适当控水，避免叶面结露"
            ],
            "safety_interval": "施药后5-7天方可采收"
        },
        "medium": {
            "pesticides": [
                {"name": "翠贝", "concentration": "50% 干悬浮剂 3000-4000倍液", "method": "叶面喷雾"},
                {"name": "凯润", "concentration": "25% 乳油 1500-2000倍液", "method": "叶面喷雾"}
            ],
            "farming_tips": [
                "及时整枝打叉，摘除病叶",
                "增施钙硅肥，增强细胞壁厚度"
            ],
            "safety_interval": "施药后7-10天方可采收"
        },
        "severe": {
            "pesticides": [
                {"name": "醚菌酯", "concentration": "50% 水分散粒剂 3000-4000倍液", "method": "叶面喷雾"},
                {"name": "吡唑醚菌酯", "concentration": "25% 乳油 1000-2000倍液", "method": "叶面喷雾"}
            ],
            "farming_tips": [
                "拔除重病株，控制蔓延",
                "使用硫磺熏蒸进行辅助防治",
                "收获后进行土壤消毒"
            ],
            "safety_interval": "施药后10-14天方可采收"
}
    },
    "早疫病": {
        "light": {
            "pesticides": [
                {"name": "代森锰锌", "concentration": "80% 可湿性粉剂 600-800倍液", "method": "叶面喷雾"},
                {"name": "百菌清", "concentration": "75% 可湿性粉剂 500-700倍液", "method": "叶面喷雾"}
            ],
            "farming_tips": [
                "及时清除病叶和病果",
                "加强通风透光，降低田间湿度",
                "适当增施磷钾肥，提高植株抗病力"
            ],
            "safety_interval": "施药后7-10天方可采收"
        },
        "medium": {
            "pesticides": [
                {"name": "嘧菌酯", "concentration": "25% 悬浮剂 1000-1500倍液", "method": "叶面喷雾"},
                {"name": "霜脲·锰锌", "concentration": "72% 可湿性粉剂 600-800倍液", "method": "叶面喷雾"}
            ],
            "farming_tips": [
                "摘除底部老叶，改善田间通风条件",
                "控制氮肥用量，防止植株徒长",
                "采用高垄栽培，避免积水"
            ],
            "safety_interval": "施药后10-14天方可采收"
        },
        "severe": {
            "pesticides": [
                {"name": "烯酰吗啉", "concentration": "50% 可湿性粉剂 2000-2500倍液", "method": "叶面喷雾"},
                {"name": "氟吡菌胺·霜霉威", "concentration": "687.5g/L 悬浮剂 600-800倍液", "method": "叶面喷雾"}
            ],
            "farming_tips": [
                "拔除严重病株，带出田外销毁",
                "全田紧急喷药，控制病情扩散",
                "收获后彻底清除田间病残体"
            ],
            "safety_interval": "施药后14-21天方可采收"
        }
    },
    "晚疫病": {
        "light": {
            "pesticides": [
                {"name": "甲霜灵", "concentration": "25% 可湿性粉剂 500-800倍液", "method": "叶面喷雾"},
                {"name": "霜霉威", "concentration": "72.2% 水剂 600-800倍液", "method": "叶面喷雾"}
            ],
            "farming_tips": [
                "及时拔除中心病株",
                "控制灌水，降低田间湿度",
                "注意天气预报，雨前预防施药"
            ],
            "safety_interval": "施药后7-10天方可采收"
        },
        "medium": {
            "pesticides": [
                {"name": "精甲霜·锰锌", "concentration": "68% 水分散粒剂 600-800倍液", "method": "叶面喷雾"},
                {"name": "氟噻唑吡乙酮", "concentration": "10% 悬浮剂 2000-3000倍液", "method": "叶面喷雾"}
            ],
            "farming_tips": [
                "清除病叶病果，减少再侵染源",
                "加强棚室通风排湿",
                "适当提高棚温，抑制病菌生长"
            ],
            "safety_interval": "施药后10-14天方可采收"
        },
        "severe": {
            "pesticides": [
                {"name": "银法利", "concentration": "687.5g/L 悬浮剂 600-800倍液", "method": "叶面喷雾"},
                {"name": "抑快净", "concentration": "52.5% 水分散粒剂 2000-3000倍液", "method": "叶面喷雾"}
            ],
            "farming_tips": [
                "严重发病田块立即拔除病株",
                "全田施药，防止向健康植株蔓延",
                "与非茄科作物轮作3年以上"
            ],
            "safety_interval": "施药后14-21天方可采收"
        }
    },
    "细菌性斑点病": {
        "light": {
            "pesticides": [
                {"name": "噻唑锌", "concentration": "20% 悬浮剂 300-500倍液", "method": "叶面喷雾"},
                {"name": "春雷霉素", "concentration": "2% 水剂 300-500倍液", "method": "叶面喷雾"}
            ],
            "farming_tips": [
                "及时清除病叶病果",
                "避免田间积水",
                "控制氮肥施用，增强植株抗性"
            ],
            "safety_interval": "施药后5-7天方可采收"
        },
        "medium": {
            "pesticides": [
                {"name": "氢氧化铜", "concentration": "77% 可湿性粉剂 400-600倍液", "method": "叶面喷雾"},
                {"name": "噻菌铜", "concentration": "20% 悬浮剂 300-500倍液", "method": "叶面喷雾"}
            ],
            "farming_tips": [
                "摘除严重病叶，减少病原扩散",
                "避免露水未干时进行农事操作",
                "增加通风透光，降低叶面湿度"
            ],
            "safety_interval": "施药后7-10天方可采收"
        },
        "severe": {
            "pesticides": [
                {"name": "氯溴异氰尿酸", "concentration": "50% 可溶粉剂 1000-1500倍液", "method": "叶面喷雾+灌根"},
                {"name": "中生菌素", "concentration": "3% 可湿性粉剂 800-1000倍液", "method": "叶面喷雾"}
            ],
            "farming_tips": [
                "严重病株立即拔除销毁",
                "全田喷药防控，防止扩散",
                "实行水旱轮作或与非茄科作物轮作"
            ],
            "safety_interval": "施药后10-14天方可采收"
        }
    },
    "叶霉病": {
        "light": {
            "pesticides": [
                {"name": "多抗霉素", "concentration": "10% 可湿性粉剂 500-800倍液", "method": "叶面喷雾"},
                {"name": "嘧菌环胺", "concentration": "50% 水分散粒剂 1000-1500倍液", "method": "叶面喷雾"}
            ],
            "farming_tips": [
                "加强通风换气，降低棚内湿度",
                "适当控制浇水，避免叶面结露",
                "及时摘除下部病叶"
            ],
            "safety_interval": "施药后5-7天方可采收"
        },
        "medium": {
            "pesticides": [
                {"name": "氟硅唑", "concentration": "40% 乳油 8000-10000倍液", "method": "叶面喷雾"},
                {"name": "苯醚甲环唑", "concentration": "10% 水分散粒剂 1000-1500倍液", "method": "叶面喷雾"}
            ],
            "farming_tips": [
                "连续摘除病叶，改善通风透光",
                "增施钙肥和硅肥，增强叶片抗性",
                "避免密植，确保植株间通风"
            ],
            "safety_interval": "施药后7-10天方可采收"
        },
        "severe": {
            "pesticides": [
                {"name": "凯润", "concentration": "25% 乳油 1500-2000倍液", "method": "叶面喷雾"},
                {"name": "翠贝", "concentration": "50% 干悬浮剂 3000-4000倍液", "method": "叶面喷雾"}
            ],
            "farming_tips": [
                "拔除重病株，防止大规模蔓延",
                "全田喷药，重点处理中下部叶片",
                "收获后彻底清棚，进行熏蒸消毒"
            ],
            "safety_interval": "施药后10-14天方可采收"
        }
    },
    "斑枯病": {
        "light": {
            "pesticides": [
                {"name": "代森锌", "concentration": "65% 可湿性粉剂 500-700倍液", "method": "叶面喷雾"},
                {"name": "百菌清", "concentration": "75% 可湿性粉剂 600-800倍液", "method": "叶面喷雾"}
            ],
            "farming_tips": [
                "及时清除病叶，减少初侵染源",
                "加强田间管理，合理施肥浇水",
                "避免叶面长时间湿润"
            ],
            "safety_interval": "施药后7-10天方可采收"
        },
        "medium": {
            "pesticides": [
                {"name": "嘧菌酯", "concentration": "25% 悬浮剂 1000-1500倍液", "method": "叶面喷雾"},
                {"name": "戊唑醇", "concentration": "43% 悬浮剂 3000-4000倍液", "method": "叶面喷雾"}
            ],
            "farming_tips": [
                "摘除病叶并带出田外处理",
                "适当增加磷钾肥用量",
                "采用滴灌或膜下灌水，避免水溅传播"
            ],
            "safety_interval": "施药后10-14天方可采收"
        },
        "severe": {
            "pesticides": [
                {"name": "氟硅唑", "concentration": "40% 乳油 6000-8000倍液", "method": "叶面喷雾"},
                {"name": "咪鲜胺", "concentration": "25% 乳油 1000-1500倍液", "method": "叶面喷雾"}
            ],
            "farming_tips": [
                "拔除重病株，控制病情扩散",
                "全田施药，缩短施药间隔至5-7天",
                "收获后彻底清田，深翻晒土"
            ],
            "safety_interval": "施药后14-21天方可采收"
        }
    }
}

DEFAULT_TREATMENT = {
    "pesticides": [
        {"name": "广谱杀菌剂", "concentration": "按说明书使用", "method": "叶面喷雾"}
    ],
    "farming_tips": [
        "加强田间管理",
        "合理施肥，增强抗病力",
        "及时清除病残体"
    ],
    "safety_interval": "施药后7-14天方可采收"
}

class TreatmentGenerator:
    def __init__(self):
        self.db = TREATMENT_DATABASE

    def generate(self, disease: str, severity: str, crop_type: str) -> Dict[str, Any]:
        disease_data = self.db.get(disease, {})

        if not disease_data:
            return DEFAULT_TREATMENT

        severity_data = disease_data.get(severity, disease_data.get("light", DEFAULT_TREATMENT))

        return severity_data
