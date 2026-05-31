from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.user import User
from app.models.knowledge import KnowledgeBase, Message

Base.metadata.create_all(bind=engine)

def init_default_admin():
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                password_hash=get_password_hash("admin"),
                email="admin@example.com",
                phone="13800138000",
                role="admin"
            )
            db.add(admin_user)
            db.commit()
            print("[OK] Admin account created: admin / admin")
        else:
            print("[INFO] Admin account already exists")

        # Also create a demo user
        demo_user = db.query(User).filter(User.username == "farmer").first()
        if not demo_user:
            demo_user = User(
                username="farmer",
                password_hash=get_password_hash("farmer123"),
                email="farmer@example.com",
                phone="13900139000",
                role="user"
            )
            db.add(demo_user)
            db.commit()
            print("[OK] Demo user created: farmer / farmer123")
    except Exception as e:
        print(f"[ERROR] Failed to init admin: {e}")
        db.rollback()
    finally:
        db.close()

def seed_knowledge_base():
    """Seed the knowledge base with real agricultural disease data."""
    db = SessionLocal()
    try:
        existing = db.query(KnowledgeBase).count()
        if existing > 0:
            print(f"[INFO] Knowledge base already has {existing} entries, skipping seed")
            return

        knowledge_data = [
            {
                "disease_name": "白粉病",
                "disease_name_en": "Powdery Mildew",
                "crop_type": "番茄",
                "symptoms": "叶片表面出现白色粉状斑点，逐渐扩大覆盖整个叶片。\n叶片变黄、卷曲甚至枯萎。\n严重时导致植株生长受阻，果实品质下降。\n茎秆和花器也可能受到侵害，出现白色霉层。",
                "prevention": "1. 选择抗病品种进行种植\n2. 保持植株间距，确保田间通风良好\n3. 及时摘除并销毁病叶，减少病原积累\n4. 合理灌溉，避免田间湿度过高\n5. 增施磷钾肥，避免偏施氮肥\n6. 实行轮作制度，避免连作",
                "treatment": "1. 发病初期喷施多菌灵悬浮剂，稀释1000-1500倍，每7-10天一次\n2. 使用百菌清可湿性粉剂，稀释600-800倍，叶面喷施\n3. 硫磺制剂对白粉病有特效，但高温时慎用\n4. 生物防治：使用枯草芽孢杆菌等生物农药\n5. 严重时交替使用不同药剂，避免产生抗药性",
                "image_path": None
            },
            {
                "disease_name": "叶斑病",
                "disease_name_en": "Leaf Spot",
                "crop_type": "番茄",
                "symptoms": "叶片上出现圆形或不规则形斑点，直径2-10mm。\n斑点颜色从褐色到黑色不等，中心可能出现灰白色霉层。\n病斑周围常有黄色晕圈，严重时病斑连片。\n下部叶片先发病，逐渐向上部蔓延，严重时叶片脱落。",
                "prevention": "1. 清除田间病残体，减少初侵染源\n2. 合理密植，保持通风透光\n3. 避免叶片积水，采用滴灌或沟灌\n4. 增施有机肥，提高植株抗病性\n5. 种子消毒处理，使用温汤浸种或药剂拌种\n6. 与非茄科作物轮作2-3年",
                "treatment": "1. 使用代森锰锌可湿性粉剂，稀释500-700倍喷施\n2. 甲基硫菌灵悬浮剂，稀释800-1000倍\n3. 苯醚甲环唑水分散粒剂，稀释1500-2000倍\n4. 每7-10天喷药一次，连续2-3次\n5. 雨后及时补喷，防止病菌扩散",
                "image_path": None
            },
            {
                "disease_name": "锈病",
                "disease_name_en": "Rust",
                "crop_type": "小麦",
                "symptoms": "叶片背面出现黄色或橙色锈斑（夏孢子堆）。\n后期病斑变为深褐色（冬孢子堆）。\n严重时叶片提前枯死脱落，植株生长衰弱。\n茎秆和叶鞘也可受害，影响灌浆和产量。",
                "prevention": "1. 选用抗锈病品种，定期更新品种\n2. 合理施肥，避免偏施氮肥\n3. 加强田间排水，降低田间湿度\n4. 及时清除田间杂草和自生苗\n5. 适期播种，避开锈病高发期\n6. 实行轮作，减少土壤中病原积累",
                "treatment": "1. 三唑酮（粉锈宁）乳油，稀释1000-1500倍喷施\n2. 戊唑醇悬浮剂，稀释2000-3000倍\n3. 丙环唑乳油，稀释1500-2000倍\n4. 发病初期及时喷药，间隔10-15天\n5. 药剂交替使用，延缓抗药性产生",
                "image_path": None
            },
            {
                "disease_name": "早疫病",
                "disease_name_en": "Early Blight",
                "crop_type": "土豆",
                "symptoms": "叶片上出现同心轮纹状褐色病斑，病斑周围有黄色晕圈。\n下部叶片先发病，逐渐向上蔓延。\n茎部和叶柄出现暗褐色梭形病斑。\n块茎受害后出现凹陷的圆形或椭圆形病斑，皮下组织变褐。",
                "prevention": "1. 实行与非茄科作物3年以上轮作\n2. 选用无病种薯，播种前进行种薯处理\n3. 加强田间管理，及时培土防止块茎外露\n4. 合理灌溉，避免田间积水\n5. 收获时避免损伤块茎，贮藏前充分晾晒\n6. 清除田间病残体，减少越冬菌源",
                "treatment": "1. 代森锌可湿性粉剂，稀释500-600倍喷施\n2. 百菌清可湿性粉剂，稀释600-800倍\n3. 嘧菌酯悬浮剂，稀释1500-2000倍\n4. 发病前或发病初期开始喷药，每7-10天一次\n5. 注意喷药均匀，重点喷施下部叶片",
                "image_path": None
            },
            {
                "disease_name": "晚疫病",
                "disease_name_en": "Late Blight",
                "crop_type": "土豆",
                "symptoms": "叶片出现暗绿色水渍状病斑，迅速扩大变为褐色。\n叶背出现白色霉层（孢囊梗和孢子囊），湿度大时尤为明显。\n茎部和叶柄出现褐色条斑，严重时整株枯死。\n块茎受害出现不规则褐色凹陷病斑，内部组织变褐腐烂。",
                "prevention": "1. 选用抗晚疫病品种\n2. 使用无病种薯，严格剔除病薯\n3. 合理灌溉，避免大水漫灌\n4. 加强田间通风，降低湿度\n5. 及时清除中心病株，深埋或烧毁\n6. 关注天气预报，在阴雨天气来临前预防性喷药",
                "treatment": "1. 甲霜灵锰锌可湿性粉剂，稀释600-800倍\n2. 霜霉威盐酸盐水剂，稀释600-800倍\n3. 烯酰吗啉悬浮剂，稀释1500-2000倍\n4. 氟吡菌胺·霜霉威悬浮剂，稀释1000-1500倍\n5. 发病初期立即喷药，间隔5-7天，连续2-3次",
                "image_path": None
            },
            {
                "disease_name": "细菌性斑点病",
                "disease_name_en": "Bacterial Spot",
                "crop_type": "番茄",
                "symptoms": "叶片出现水渍状小斑点，后扩大为黑褐色不规则病斑。\n病斑周围有黄色晕圈，严重时病斑连片导致叶片枯死。\n果实受害出现略微凸起的黑褐色斑点，影响商品价值。\n茎秆和叶柄也可受害，出现黑色条纹。",
                "prevention": "1. 选用抗病品种\n2. 种子消毒：使用50℃温水浸种25分钟\n3. 与非茄科作物实行2-3年轮作\n4. 加强田间通风，降低湿度\n5. 避免在叶片潮湿时进行农事操作\n6. 及时清除病残体，减少病原",
                "treatment": "1. 氢氧化铜可湿性粉剂，稀释500-800倍\n2. 春雷霉素水剂，稀释800-1000倍\n3. 噻菌铜悬浮剂，稀释600-800倍\n4. 发病初期喷药，每7-10天一次\n5. 铜制剂与抗生素类药剂交替使用效果更佳",
                "image_path": None
            },
            {
                "disease_name": "叶霉病",
                "disease_name_en": "Leaf Mold",
                "crop_type": "番茄",
                "symptoms": "叶片正面出现淡黄色褪绿斑，背面形成灰紫色至褐色霉层。\n病斑多从下部老叶开始，逐渐向上部扩展。\n严重时叶片卷曲、干枯，影响光合作用。\n花器和果实也可受害，导致落花落果。",
                "prevention": "1. 选用抗叶霉病品种\n2. 加强通风，降低棚室湿度至80%以下\n3. 合理密植，及时整枝打杈\n4. 采用膜下滴灌，降低空气湿度\n5. 清洁田园，及时清除病叶\n6. 与非茄科作物轮作",
                "treatment": "1. 嘧菌酯悬浮剂，稀释1500-2000倍\n2. 氟硅唑乳油，稀释3000-4000倍\n3. 异菌脲可湿性粉剂，稀释600-800倍\n4. 甲基硫菌灵悬浮剂，稀释800-1000倍\n5. 每7-10天喷药一次，注意喷施叶背",
                "image_path": None
            },
            {
                "disease_name": "斑枯病",
                "disease_name_en": "Septoria Leaf Spot",
                "crop_type": "番茄",
                "symptoms": "叶片出现水渍状小圆斑，后扩大为中央灰白色、边缘褐色病斑。\n病斑直径约2-5mm，中央散生黑色小粒点。\n严重时病斑密布，叶片枯黄早落。\n茎秆和果实也可受害，但较少见。",
                "prevention": "1. 实行3年以上轮作\n2. 种子消毒处理\n3. 及时清除病残体\n4. 合理密植，保持通风\n5. 增施磷钾肥，提高植株抗性\n6. 苗床消毒，培育无病壮苗",
                "treatment": "1. 代森锰锌可湿性粉剂，稀释500-600倍\n2. 百菌清可湿性粉剂，稀释600-800倍\n3. 苯醚甲环唑水分散粒剂，稀释1500倍\n4. 发病前预防性喷药效果最佳\n5. 每7-10天一次，雨季适当缩短间隔",
                "image_path": None
            },
            {
                "disease_name": "黄瓜霜霉病",
                "disease_name_en": "Cucumber Downy Mildew",
                "crop_type": "黄瓜",
                "symptoms": "叶片出现多角形黄褐色病斑，受叶脉限制。\n湿度大时叶背出现紫灰色霉层。\n病斑后期连片，叶片迅速枯死。\n病害发展极快，3-5天可蔓延全田，俗称\"跑马干\"。",
                "prevention": "1. 选用抗霜霉病品种\n2. 加强通风，降低湿度\n3. 合理灌溉，避免叶面结露\n4. 增施磷钾肥和生物菌肥\n5. 高温闷棚：晴天中午密闭大棚2小时\n6. 与非瓜类作物轮作",
                "treatment": "1. 霜脲·锰锌可湿性粉剂，稀释600-800倍\n2. 烯酰·霜脲氰悬浮剂，稀释1000-1500倍\n3. 氟菌·霜霉威悬浮剂，稀释800-1000倍\n4. 发病初期立即喷药，间隔5-7天\n5. 注意药剂轮换使用，避免抗药性",
                "image_path": None
            },
            {
                "disease_name": "玉米大斑病",
                "disease_name_en": "Northern Corn Leaf Blight",
                "crop_type": "玉米",
                "symptoms": "叶片出现长梭形或长椭圆形大斑，长5-10cm。\n病斑中部灰褐色，边缘暗褐色。\n严重时病斑连片，叶片枯死，影响光合作用。\n一般下部叶片先发病，逐渐向上部蔓延。",
                "prevention": "1. 选用抗大斑病杂交品种\n2. 合理密植，保证通风透光\n3. 增施有机肥和磷钾肥\n4. 及时清除田间病残体\n5. 实行轮作，避免连作\n6. 适期播种，避开病害高发期",
                "treatment": "1. 丙环唑·嘧菌酯悬浮剂，稀释1500-2000倍\n2. 吡唑醚菌酯乳油，稀释2000-3000倍\n3. 戊唑醇悬浮剂，稀释2000倍\n4. 发病初期开始喷药，间隔7-10天\n5. 大喇叭口期和抽雄期是防治关键期",
                "image_path": None
            },
            {
                "disease_name": "水稻稻瘟病",
                "disease_name_en": "Rice Blast",
                "crop_type": "水稻",
                "symptoms": "苗瘟：秧苗基部变褐枯死，表面有灰绿色霉层。\n叶瘟：叶片出现梭形病斑，中央灰白色、边缘褐色。\n节瘟：茎节变黑褐色，易折断倒伏。\n穗颈瘟：穗颈节变褐坏死，造成白穗或谷粒不饱满。",
                "prevention": "1. 选用抗稻瘟病品种\n2. 合理施肥，避免过量施用氮肥\n3. 合理灌溉，浅水勤灌，适时晒田\n4. 种子消毒处理\n5. 清除田间病草和病残体\n6. 合理密植，保证通风透光",
                "treatment": "1. 三环唑可湿性粉剂，稀释500-600倍\n2. 稻瘟灵乳油，稀释800-1000倍\n3. 嘧菌酯悬浮剂，稀释1500-2000倍\n4. 预防为主：破口期和齐穗期各喷药一次\n5. 叶瘟发病初期及时防治，防止蔓延至穗部",
                "image_path": None
            },
            {
                "disease_name": "辣椒炭疽病",
                "disease_name_en": "Pepper Anthracnose",
                "crop_type": "辣椒",
                "symptoms": "果实出现圆形或椭圆形凹陷病斑，中央灰白色。\n病斑上有轮纹状排列的黑色小粒点（分生孢子盘）。\n湿度大时病斑上出现粉红色粘稠物。\n叶片也可受害，出现褐色圆形病斑。",
                "prevention": "1. 选用抗病品种\n2. 种子消毒：55℃温水浸种15分钟\n3. 与禾本科作物轮作2-3年\n4. 合理密植，保持通风\n5. 及时采收，避免果实过熟\n6. 清除田间病果病叶",
                "treatment": "1. 咪鲜胺乳油，稀释1000-1500倍\n2. 苯醚甲环唑水分散粒剂，稀释1500倍\n3. 吡唑醚菌酯乳油，稀释2000倍\n4. 发病初期开始喷药，间隔7-10天\n5. 重点喷施果实部位",
                "image_path": None
            },
        ]

        for item in knowledge_data:
            kb = KnowledgeBase(**item)
            db.add(kb)

        db.commit()
        print(f"[OK] Knowledge base seeded with {len(knowledge_data)} entries")
    except Exception as e:
        print(f"[ERROR] Failed to seed knowledge base: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_default_admin()
    seed_knowledge_base()
    print("[DONE] Database initialization complete")
