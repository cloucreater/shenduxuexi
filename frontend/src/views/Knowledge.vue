<script setup lang="ts">
import { ref, computed } from 'vue'

const searchQuery = ref('')
const selectedCategory = ref('all')
const selectedArticle = ref<any>(null)

// Rich knowledge base — 10+ entries per crop category
const allArticles = ref([
  // ===== 番茄 (Tomato) - 12 entries =====
  { id: 1, crop: '番茄', disease: '番茄早疫病', enName: 'Tomato Early Blight', category: '番茄', icon:'tomato',
    symptoms: '叶片出现同心轮纹状褐色病斑，病斑周围有黄色晕圈。下部叶片先发病，逐渐向上蔓延。茎部病斑呈椭圆形暗褐色凹陷。果实受害后出现暗褐色圆形凹陷斑，表面有黑色霉层。严重时全株叶片枯死，导致大幅减产。',
    prevention: '1. 选用抗病品种（如中杂9号、金棚1号等）\n2. 实行3年以上轮作，不与茄科作物连作\n3. 种子消毒：50℃温水浸种25分钟或用50%多菌灵500倍液浸种\n4. 合理密植，保持田间通风透光\n5. 增施腐熟有机肥，控制氮肥用量，增施磷钾肥\n6. 及时清除病叶、病果，集中深埋或烧毁',
    treatment: '发病初期喷施70%代森锰锌可湿性粉剂500倍液，或50%多菌灵可湿性粉剂500-800倍液，或75%百菌清可湿性粉剂600倍液。每7-10天喷施1次，连续2-3次。注意交替用药。',
    views: 1250 },

  { id: 2, crop: '番茄', disease: '番茄晚疫病', enName: 'Tomato Late Blight', category: '番茄', icon:'tomato',
    symptoms: '叶片出现暗绿色水渍状不规则病斑，湿度大时叶背出现白色霉层。茎部病斑呈黑褐色长条状。果实受害后出现暗绿色至褐色云纹状斑块，病健交界不明显，后期果实腐烂有恶臭。该病害传播极快，条件适宜时2-3天即可全田发病。',
    prevention: '1. 选用抗晚疫病品种\n2. 高畦栽培，加强排水，避免田间积水\n3. 合理密植，及时整枝打杈，改善通风条件\n4. 发现中心病株立即拔除销毁\n5. 关注天气预报，连续阴雨前提前预防\n6. 覆盖地膜减少土壤水分蒸发',
    treatment: '发病前或发病初期喷施72%霜脲·锰锌可湿性粉剂600-800倍液，或58%甲霜灵锰锌可湿性粉剂500倍液，或64%噁霜·锰锌可湿性粉剂500倍液。每7天喷施1次，视病情喷2-4次。',
    views: 980 },

  { id: 3, crop: '番茄', disease: '番茄白粉病', enName: 'Tomato Powdery Mildew', category: '番茄', icon:'tomato',
    symptoms: '叶片表面出现白色粉状斑点，后扩大成不规则白粉斑，严重时叶片正反面布满白粉。叶片逐渐变黄、卷曲、枯死。叶柄和茎部也可受害。病原菌为专性寄生菌，主要靠气流传播。',
    prevention: '1. 加强通风降湿，合理密植\n2. 增施磷钾肥，避免偏施氮肥\n3. 及时摘除老叶病叶\n4. 高温干旱时注意浇水降温\n5. 选用耐病品种',
    treatment: '发病初期喷施25%三唑酮可湿性粉剂1500-2000倍液，或40%氟硅唑乳油6000-8000倍液，或10%苯醚甲环唑水分散粒剂1500倍液。每10-14天喷1次，连续1-2次。',
    views: 760 },

  { id: 4, crop: '番茄', disease: '番茄灰霉病', enName: 'Tomato Gray Mold', category: '番茄', icon:'tomato',
    symptoms: '叶片从叶缘开始出现"V"字形病斑，灰褐色，湿度大时病斑表面产生灰色霉层。花器受害后变褐腐烂，表面产生灰色霉层。果实受害后出现水渍状病斑，后期腐烂并产生大量灰色霉层。',
    prevention: '1. 加强通风排湿，控制大棚内湿度在80%以下\n2. 及时摘除病花、病果、病叶\n3. 地膜覆盖减少土壤水分蒸发\n4. 合理施肥，增强植株抗病力\n5. 蘸花时在药液中加入50%腐霉利可湿性粉剂',
    treatment: '发病初期喷施50%腐霉利可湿性粉剂1000-1500倍液，或50%异菌脲可湿性粉剂1000-1500倍液，或40%嘧霉胺悬浮剂1000倍液。每7-10天喷1次，连续2-3次。',
    views: 890 },

  { id: 5, crop: '番茄', disease: '番茄叶霉病', enName: 'Tomato Leaf Mold', category: '番茄', icon:'tomato',
    symptoms: '叶片正面出现淡黄色褪绿斑，叶背产生灰褐色至紫褐色绒状霉层。病斑多从下部叶片开始发生，逐渐向上蔓延。严重时全叶枯死，影响光合作用和产量。',
    prevention: '1. 选用抗叶霉病品种\n2. 加强通风，降低棚内湿度\n3. 合理密植，及时整枝\n4. 与非茄科作物轮作2-3年',
    treatment: '发病初期喷施10%苯醚甲环唑水分散粒剂1500倍液，或40%氟硅唑乳油6000-8000倍液，或50%多菌灵可湿性粉剂500-800倍液。每7-10天喷1次。',
    views: 670 },

  { id: 6, crop: '番茄', disease: '番茄青枯病', enName: 'Tomato Bacterial Wilt', category: '番茄', icon:'tomato',
    symptoms: '植株顶部叶片先萎蔫，后下部叶片也萎蔫。初期早晚可恢复，数天后全株枯死但仍保持绿色。横切茎部可见维管束变褐色，挤压有白色菌脓溢出。属于土传细菌性病害。',
    prevention: '1. 实行4-5年轮作，与禾本科作物轮作\n2. 选用抗病砧木进行嫁接栽培\n3. 高畦栽培，避免大水漫灌\n4. 土壤消毒：石灰氮或棉隆处理\n5. 发现病株立即拔除，病穴撒石灰消毒',
    treatment: '发病初期用77%氢氧化铜可湿性粉剂500倍液，或20%噻菌铜悬浮剂600倍液灌根，每株灌200-300ml药液。也可使用中生菌素等生物制剂。预防为主，发病后治疗效果有限。',
    views: 1120 },

  { id: 7, crop: '番茄', disease: '番茄枯萎病', enName: 'Tomato Fusarium Wilt', category: '番茄', icon:'tomato',
    symptoms: '植株下部叶片先变黄，后向上蔓延。植株一侧或部分枝条先表现症状，叶片萎蔫下垂。纵剖茎部可见维管束变褐色。与青枯病不同，枯萎病叶片先变黄后才枯死。',
    prevention: '1. 选用抗枯萎病品种\n2. 轮作倒茬4年以上\n3. 种子消毒和苗床消毒\n4. 嫁接栽培是防治枯萎病最有效的方法',
    treatment: '发病初期用50%多菌灵可湿性粉剂500倍液或70%甲基硫菌灵可湿性粉剂600倍液灌根，每株灌200-300ml，隔7-10天再灌1次。',
    views: 580 },

  { id: 8, crop: '番茄', disease: '番茄斑枯病', enName: 'Tomato Septoria Leaf Spot', category: '番茄', icon:'tomato',
    symptoms: '叶片出现圆形水渍状小斑点，后扩大为边缘褐色、中央灰白色的近圆形病斑，病斑中央散生黑色小粒点。严重时叶片布满病斑，变黄枯死脱落。下部叶片先发病。',
    prevention: '1. 使用无病种子或种子消毒\n2. 与非茄科作物轮作3年以上\n3. 加强田间管理，及时清除病残体\n4. 合理灌溉，避免田间积水',
    treatment: '发病初期喷施70%代森锰锌可湿性粉剂500倍液，或50%多菌灵可湿性粉剂500倍液，或75%百菌清可湿性粉剂600倍液。每7-10天喷1次，连续2-3次。',
    views: 450 },

  { id: 9, crop: '番茄', disease: '番茄病毒病', enName: 'Tomato Viral Disease', category: '番茄', icon:'tomato',
    symptoms: '常见有花叶型（叶片出现黄绿相间的斑驳）、蕨叶型（叶片变细长呈蕨叶状）、条斑型（茎叶果实出现坏死条斑）。植株矮化，生长受阻。主要通过蚜虫传播。',
    prevention: '1. 选用抗病毒品种\n2. 防治传毒蚜虫（设置防虫网、挂黄板）\n3. 避免接触传染（操作时先管健株后管病株）\n4. 种子用10%磷酸三钠浸种20分钟消毒\n5. 合理轮作，清除田间杂草',
    treatment: '病毒病无特效治疗药剂。发病初期可喷施20%吗胍·乙酸铜可湿性粉剂500倍液或8%宁南霉素水剂500倍液，配合杀蚜剂使用。同时加强水肥管理，提高植株自身免疫力。',
    views: 1340 },

  { id: 10, crop: '番茄', disease: '番茄脐腐病', enName: 'Tomato Blossom End Rot', category: '番茄', icon:'tomato',
    symptoms: '果实脐部出现水渍状暗绿色斑块，后变为暗褐色或黑色凹陷坏死斑。病部果肉干缩变黑，有时伴有腐生菌感染。属于生理性病害，主要由缺钙和水分供应不均引起。',
    prevention: '1. 合理施肥，注意补充钙肥（叶面喷施0.3%氯化钙溶液）\n2. 均衡供水，避免土壤忽干忽湿\n3. 覆盖地膜保持土壤湿度稳定\n4. 避免偏施氮肥\n5. 酸性土壤可施用石灰改良',
    treatment: '发现症状后立即叶面喷施0.3%-0.5%氯化钙或硝酸钙溶液，每5-7天喷1次，连续2-3次。同时改善灌水管理，保持土壤湿度均衡。',
    views: 720 },

  { id: 11, crop: '番茄', disease: '番茄黄化曲叶病毒病', enName: 'Tomato TYLCV', category: '番茄', icon:'tomato',
    symptoms: '植株矮化，顶部叶片变小、黄化、上卷呈杯状。叶缘向上卷曲，叶脉间黄化，叶片变厚变脆。花器发育不良，落花落果严重。由烟粉虱传播，是世界性毁灭性病害。',
    prevention: '1. 选用抗TYLCV品种\n2. 使用50目防虫网覆盖通风口\n3. 苗床悬挂黄板监测和诱杀烟粉虱\n4. 清除田间杂草和病残体\n5. 培育无虫苗是关键',
    treatment: '治虫防病：喷施25%噻虫嗪水分散粒剂3000倍液或22.4%螺虫乙酯悬浮剂1500倍液防治烟粉虱。配合喷施20%吗胍·乙酸铜可湿性粉剂500倍液缓解症状。',
    views: 1560 },

  { id: 12, crop: '番茄', disease: '番茄细菌性斑点病', enName: 'Tomato Bacterial Speck', category: '番茄', icon:'tomato',
    symptoms: '叶片出现暗褐色水渍状小斑点，周围有黄色晕圈。幼果表面出现褐色小斑点，略隆起。茎部和叶柄也可受害。病原菌靠雨水飞溅和农事操作传播。',
    prevention: '1. 使用无病种子\n2. 与非茄科作物轮作2-3年\n3. 雨后及时排水\n4. 避免在植株上有露水时进行农事操作',
    treatment: '发病初期喷施77%氢氧化铜可湿性粉剂500-800倍液，或20%噻菌铜悬浮剂500-600倍液，或3%中生菌素可湿性粉剂800-1000倍液。每7-10天喷1次。',
    views: 410 },

  // ===== 黄瓜 (Cucumber) - 10 entries =====
  { id: 13, crop: '黄瓜', disease: '黄瓜霜霉病', enName: 'Cucumber Downy Mildew', category: '黄瓜', icon:'cucumber',
    symptoms: '叶片出现多角形黄色病斑，受叶脉限制呈不规则形状。湿度大时叶背产生灰黑色霉层。病斑从下部叶片开始，逐渐向上发展。严重时全田叶片枯黄，似火烧状，俗称"跑马干"。',
    prevention: '1. 选用抗霜霉病品种（如津优系列）\n2. 加强通风，降低棚内湿度\n3. 覆盖地膜，膜下灌溉\n4. 增施磷钾肥，提高植株抗病力\n5. 高温闷棚（晴天中午密闭大棚使温度升至45℃，维持2小时）',
    treatment: '发病初期喷施72%霜脲·锰锌可湿性粉剂600-800倍液，或58%甲霜灵锰锌可湿性粉剂500倍液，或687.5g/L氟菌·霜霉威悬浮剂600-800倍液。每5-7天喷1次。',
    views: 1450 },

  { id: 14, crop: '黄瓜', disease: '黄瓜白粉病', enName: 'Cucumber Powdery Mildew', category: '黄瓜', icon:'cucumber',
    symptoms: '叶片正反面出现白色近圆形粉斑，后扩大连片覆盖整个叶片。白粉层逐渐变灰白色，上面散生黑色小粒点（闭囊壳）。叶片变黄枯焦，影响光合作用。',
    prevention: '1. 选用抗白粉病品种\n2. 合理密植，及时整枝打杈\n3. 加强通风，降低田间湿度\n4. 增施磷钾肥\n5. 收获后彻底清除病残体',
    treatment: '发病初期喷施25%三唑酮可湿性粉剂1500倍液，或250g/L嘧菌酯悬浮剂1500倍液，或40%氟硅唑乳油6000-8000倍液。注意轮换用药。',
    views: 820 },

  { id: 15, crop: '黄瓜', disease: '黄瓜细菌性角斑病', enName: 'Cucumber Angular Leaf Spot', category: '黄瓜', icon:'cucumber',
    symptoms: '叶片出现水渍状小斑点，后扩大为多角形（受叶脉限制），呈淡褐色。湿度大时叶背病斑处有菌脓溢出，干燥后形成白色薄膜。病斑后期穿孔。果实受害出现水渍状小斑点。',
    prevention: '1. 使用无病种子，种子用50℃温水浸种20分钟\n2. 与非瓜类作物轮作2年以上\n3. 加强通风排湿\n4. 避免在叶片有露水时作业',
    treatment: '发病初期喷施77%氢氧化铜可湿性粉剂500倍液，或20%噻菌铜悬浮剂500-600倍液，或3%中生菌素可湿性粉剂800倍液。每7-10天喷1次。',
    views: 680 },

  { id: 16, crop: '黄瓜', disease: '黄瓜枯萎病', enName: 'Cucumber Fusarium Wilt', category: '黄瓜', icon:'cucumber',
    symptoms: '植株叶片从下向上逐渐萎蔫，似缺水状，中午尤为明显，早晚可恢复。数天后整株枯死。茎基部呈水渍状缢缩，纵剖茎部维管束变褐色。病部有白色或粉红色霉层。',
    prevention: '1. 嫁接栽培（黑籽南瓜作砧木）是防治枯萎病最有效的方法\n2. 与非瓜类作物轮作5年以上\n3. 土壤消毒\n4. 使用无病土育苗',
    treatment: '发病初期用50%多菌灵可湿性粉剂500倍液或70%甲基硫菌灵可湿性粉剂600倍液灌根，每株灌250ml，隔7天再灌1次。',
    views: 920 },

  { id: 17, crop: '黄瓜', disease: '黄瓜灰霉病', enName: 'Cucumber Gray Mold', category: '黄瓜', icon:'cucumber',
    symptoms: '主要危害花和幼瓜。病菌从开败的花器侵入，使花腐烂并产生灰色霉层，进而侵染幼瓜。幼瓜发病后腐烂软化，表面密生灰色霉层。叶片受害产生大型灰褐色不规则病斑。',
    prevention: '1. 加强通风排湿\n2. 及时摘除病花病瓜\n3. 地膜覆盖减少湿度\n4. 合理施肥，避免偏施氮肥',
    treatment: '发病初期喷施50%腐霉利可湿性粉剂1000倍液，或50%异菌脲可湿性粉剂1000倍液，或40%嘧霉胺悬浮剂800-1000倍液。每7天喷1次。',
    views: 750 },

  { id: 18, crop: '黄瓜', disease: '黄瓜疫病', enName: 'Cucumber Phytophthora Blight', category: '黄瓜', icon:'cucumber',
    symptoms: '茎基部出现暗绿色水渍状缢缩，上部叶片迅速萎蔫枯死。叶片产生暗绿色水渍状圆形大斑，湿度大时软腐。瓜条受害后出现暗绿色水渍状凹陷斑，后软腐且表面有白色霉层。',
    prevention: '1. 高畦栽培，加强排水\n2. 与非瓜类作物轮作3年以上\n3. 地膜覆盖\n4. 及时清除病株',
    treatment: '发病初期喷施72%霜脲·锰锌可湿性粉剂600-800倍液，或58%甲霜灵锰锌可湿性粉剂500倍液，或50%烯酰吗啉可湿性粉剂1500倍液。灌根与喷施结合。',
    views: 560 },

  { id: 19, crop: '黄瓜', disease: '黄瓜蔓枯病', enName: 'Cucumber Gummy Stem Blight', category: '黄瓜', icon:'cucumber',
    symptoms: '茎蔓受害多在近节部出现油渍状病斑，后变为灰白色，有时溢出琥珀色胶状物。病部干缩纵裂，上部茎叶枯萎。叶片出现近圆形或不规则形大型病斑，有明显的轮纹。',
    prevention: '1. 种子消毒\n2. 与非瓜类作物轮作2-3年\n3. 合理施肥，避免偏施氮肥\n4. 及时整枝打杈，改善通风',
    treatment: '发病初期用70%甲基硫菌灵可湿性粉剂600倍液或10%苯醚甲环唑水分散粒剂1500倍液涂抹茎蔓病部，同时叶面喷施。每7天1次，连续2-3次。',
    views: 480 },

  { id: 20, crop: '黄瓜', disease: '黄瓜炭疽病', enName: 'Cucumber Anthracnose', category: '黄瓜', icon:'cucumber',
    symptoms: '叶片出现近圆形水渍状病斑，后变为黄褐色，外围有黄色晕圈，病斑上产生黑色小粒点。茎蔓和叶柄出现长圆形凹陷病斑。果实受害出现圆形暗绿色水渍状凹陷斑，湿度大时有粉红色黏质物。',
    prevention: '1. 使用无病种子或种子消毒\n2. 轮作3年以上\n3. 加强通风，降低湿度\n4. 收获后清除病残体',
    treatment: '发病初期喷施50%多菌灵可湿性粉剂500倍液，或75%百菌清可湿性粉剂600倍液，或250g/L嘧菌酯悬浮剂1500倍液。每7天喷1次。',
    views: 520 },

  { id: 21, crop: '黄瓜', disease: '黄瓜根结线虫病', enName: 'Cucumber Root-Knot Nematode', category: '黄瓜', icon:'cucumber',
    symptoms: '植株地上部表现生长不良，矮小，叶片发黄，结果少而小。地下部根系形成大小不等的根结（瘤状物），初为白色，后变褐色。根系发育受阻，吸收功能下降。',
    prevention: '1. 与禾本科作物轮作3年以上\n2. 夏季高温闷棚（覆膜后使土温升至55℃以上）\n3. 施用生物菌肥（淡紫拟青霉等）\n4. 使用无病土育苗',
    treatment: '定植前用1.8%阿维菌素乳油1000倍液灌穴。生长期可用41.7%氟吡菌酰胺悬浮剂0.02-0.04ml/株灌根处理。',
    views: 630 },

  { id: 22, crop: '黄瓜', disease: '黄瓜靶斑病', enName: 'Cucumber Corynespora Leaf Spot', category: '黄瓜', icon:'cucumber',
    symptoms: '叶片出现黄褐色小斑点，后扩大为圆形或不规则形病斑，中央颜色较浅，周围有黄色晕圈，整体呈"靶状"。严重时多个病斑融合，叶片枯死。近年来上升为黄瓜主要病害之一。',
    prevention: '1. 选用抗病品种\n2. 合理密植，及时整枝\n3. 加强通风排湿\n4. 增施有机肥和磷钾肥',
    treatment: '发病初期喷施250g/L嘧菌酯悬浮剂1500倍液，或43%氟菌·肟菌酯悬浮剂2000-3000倍液，或50%咪鲜胺锰盐可湿性粉剂1000-1500倍液。',
    views: 390 },

  // ===== 辣椒 (Pepper) - 10 entries =====
  { id: 23, crop: '辣椒', disease: '辣椒疫病', enName: 'Pepper Phytophthora Blight', category: '辣椒', icon:'pepper',
    symptoms: '茎基部出现暗绿色水渍状病斑，后变为黑褐色缢缩，地上部迅速萎蔫枯死。叶片产生暗绿色水渍状圆形大斑。果实从蒂部开始出现暗绿色水渍状病斑，后软腐，表面有白色霉层。是辣椒的毁灭性病害。',
    prevention: '1. 高畦覆膜栽培\n2. 与非茄科作物轮作3年以上\n3. 加强排水，避免田间积水\n4. 发现病株立即拔除\n5. 采用滴灌代替漫灌',
    treatment: '发病前或发病初期用72%霜脲·锰锌可湿性粉剂600倍液，或58%甲霜灵锰锌可湿性粉剂500倍液，或50%烯酰吗啉可湿性粉剂1500倍液灌根+喷施。每7天1次。',
    views: 1100 },

  { id: 24, crop: '辣椒', disease: '辣椒炭疽病', enName: 'Pepper Anthracnose', category: '辣椒', icon:'pepper',
    symptoms: '果实上出现圆形或不规则形凹陷病斑，褐色至黑褐色，病斑上有轮纹状排列的黑色小粒点。湿度大时病斑表面产生粉红色黏质物。叶片也可受害，出现圆形褐色病斑。',
    prevention: '1. 选用抗病品种\n2. 种子消毒处理\n3. 合理密植，加强通风\n4. 及时采收，避免果实过熟\n5. 收获后清除病残体',
    treatment: '发病初期喷施50%多菌灵可湿性粉剂500倍液，或75%百菌清可湿性粉剂600倍液，或250g/L嘧菌酯悬浮剂1500倍液。重点喷施果实。',
    views: 860 },

  { id: 25, crop: '辣椒', disease: '辣椒病毒病', enName: 'Pepper Viral Disease', category: '辣椒', icon:'pepper',
    symptoms: '花叶型：叶片出现黄绿相间斑驳；畸形型：叶片变小卷曲，植株矮化；坏死型：茎秆和果实出现褐色坏死条斑。主要由蚜虫传播，苗期感染损失最重。',
    prevention: '1. 选用抗病毒品种\n2. 防蚜虫（挂银灰膜驱蚜、设防虫网）\n3. 培育无病壮苗\n4. 与非茄科作物轮作\n5. 田间操作时避免接触传播',
    treatment: '发病初期喷施20%吗胍·乙酸铜可湿性粉剂500倍液，或8%宁南霉素水剂500倍液，配合10%吡虫啉可湿性粉剂2000倍液防治蚜虫。',
    views: 980 },

  { id: 26, crop: '辣椒', disease: '辣椒青枯病', enName: 'Pepper Bacterial Wilt', category: '辣椒', icon:'pepper',
    symptoms: '植株顶部叶片先萎蔫，后全株萎蔫枯死，但叶片仍保持绿色。横切茎基部可见维管束变褐色，挤压有白色菌脓溢出。高温高湿条件下发病严重。',
    prevention: '1. 轮作4-5年，最好与禾本科作物轮作\n2. 高畦栽培，避免积水\n3. 酸性土壤施用石灰调节pH\n4. 发现病株立即拔除，病穴撒石灰',
    treatment: '发病初期用77%氢氧化铜可湿性粉剂500倍液或20%噻菌铜悬浮剂600倍液灌根。以预防为主，发病后治疗效果有限。',
    views: 720 },

  { id: 27, crop: '辣椒', disease: '辣椒白粉病', enName: 'Pepper Powdery Mildew', category: '辣椒', icon:'pepper',
    symptoms: '叶片背面产生白色粉状物，正面出现褪绿黄斑。后期白粉层覆盖整个叶背，叶片变黄脱落。大棚栽培发生较重。',
    prevention: '1. 加强通风降湿\n2. 合理密植\n3. 增施磷钾肥\n4. 及时清除病叶',
    treatment: '发病初期喷施25%三唑酮可湿性粉剂1500倍液，或250g/L嘧菌酯悬浮剂1500倍液，或40%氟硅唑乳油6000倍液。',
    views: 540 },

  { id: 28, crop: '辣椒', disease: '辣椒疮痂病', enName: 'Pepper Bacterial Spot', category: '辣椒', icon:'pepper',
    symptoms: '叶片出现水渍状小斑点，后扩大为圆形或不规则形，边缘隆起，中央凹陷呈疮痂状。病斑沿叶脉发生时常使叶片畸形。果实出现圆形隆起的小斑点，后期木栓化。',
    prevention: '1. 使用无病种子\n2. 与非茄科作物轮作2-3年\n3. 雨后及时排水\n4. 避免叶片带露水作业',
    treatment: '发病初期喷施77%氢氧化铜可湿性粉剂500倍液，或20%噻菌铜悬浮剂500-600倍液，或3%中生菌素可湿性粉剂800倍液。',
    views: 480 },

  { id: 29, crop: '辣椒', disease: '辣椒灰霉病', enName: 'Pepper Gray Mold', category: '辣椒', icon:'pepper',
    symptoms: '主要危害花器和果实。花器受害后变褐腐烂，产生灰色霉层。果实受害多从蒂部开始，出现水渍状腐烂，表面密生灰色霉层。保护地栽培发病严重。',
    prevention: '1. 加强通风排湿\n2. 及时摘除病花病果\n3. 地膜覆盖\n4. 合理施肥，控制氮肥',
    treatment: '发病初期喷施50%腐霉利可湿性粉剂1000倍液，或50%异菌脲可湿性粉剂1000倍液，或40%嘧霉胺悬浮剂800倍液。',
    views: 430 },

  { id: 30, crop: '辣椒', disease: '辣椒枯萎病', enName: 'Pepper Fusarium Wilt', category: '辣椒', icon:'pepper',
    symptoms: '植株从下部叶片开始变黄萎蔫，逐渐向上蔓延。茎基部皮层有时开裂，纵剖可见维管束变褐色。与青枯病不同的是，枯萎病叶片先变黄后枯死。',
    prevention: '1. 轮作4年以上\n2. 选用抗病品种或嫁接栽培\n3. 土壤消毒\n4. 合理灌溉，避免大水漫灌',
    treatment: '发病初期用50%多菌灵可湿性粉剂500倍液或70%甲基硫菌灵可湿性粉剂600倍液灌根，每株灌200-300ml。',
    views: 380 },

  { id: 31, crop: '辣椒', disease: '辣椒日灼病', enName: 'Pepper Sunscald', category: '辣椒', icon:'pepper',
    symptoms: '果实向阳面出现褪绿变白的斑块，后变为黄褐色或灰白色干枯斑，病部变薄、革质化。属于生理性病害，由强光直射和高温引起。',
    prevention: '1. 合理密植，使枝叶遮阴果实\n2. 增施有机肥，培育健壮植株\n3. 均衡供水\n4. 高温季节适当遮阳',
    treatment: '加强水肥管理，促进枝叶生长。严重时可搭建遮阳网。叶面喷施0.2%磷酸二氢钾增强植株抗逆性。',
    views: 320 },

  { id: 32, crop: '辣椒', disease: '辣椒根腐病', enName: 'Pepper Root Rot', category: '辣椒', icon:'pepper',
    symptoms: '植株地上部生长缓慢，叶片发黄，逐渐萎蔫。地下根系变褐腐烂，皮层易剥离。严重时整株枯死。多发生在结果初期，土壤湿度大时发病重。',
    prevention: '1. 高畦栽培，加强排水\n2. 合理轮作\n3. 土壤消毒\n4. 避免施用未腐熟的有机肥',
    treatment: '发病初期用50%多菌灵可湿性粉剂500倍液+70%甲基硫菌灵可湿性粉剂600倍液灌根，或68%精甲霜·锰锌水分散粒剂600倍液灌根。',
    views: 350 },

  // ===== 土豆 (Potato) - 10 entries =====
  { id: 33, crop: '土豆', disease: '马铃薯晚疫病', enName: 'Potato Late Blight', category: '土豆', icon:'potato',
    symptoms: '叶片出现暗绿色水渍状不规则病斑，湿度大时叶背产生白色霉层。茎部出现褐色条斑。块茎受害后出现褐色至紫褐色不规则病斑，切开后可见褐色坏死斑。历史上引起爱尔兰大饥荒的病害。',
    prevention: '1. 选用抗病品种\n2. 选用无病种薯\n3. 高畦栽培，加强排水\n4. 及时发现并拔除中心病株\n5. 合理施肥，避免偏施氮肥',
    treatment: '发病前或发病初期喷施72%霜脲·锰锌可湿性粉剂600倍液，或58%甲霜灵锰锌可湿性粉剂500倍液，或687.5g/L氟菌·霜霉威悬浮剂600-800倍液。每7-10天喷1次。',
    views: 1350 },

  { id: 34, crop: '土豆', disease: '马铃薯早疫病', enName: 'Potato Early Blight', category: '土豆', icon:'potato',
    symptoms: '叶片出现近圆形褐色病斑，有明显的同心轮纹，周围有黄色晕圈。下部叶片先发病，逐渐向上蔓延。块茎受害后出现暗褐色近圆形凹陷斑，皮下组织变褐腐烂。',
    prevention: '1. 轮作倒茬\n2. 增施有机肥和磷钾肥\n3. 合理灌溉\n4. 及时收获，避免机械损伤',
    treatment: '发病初期喷施70%代森锰锌可湿性粉剂500倍液，或75%百菌清可湿性粉剂600倍液，或250g/L嘧菌酯悬浮剂1500倍液。每7-10天喷1次。',
    views: 780 },

  { id: 35, crop: '土豆', disease: '马铃薯黑胫病', enName: 'Potato Blackleg', category: '土豆', icon:'potato',
    symptoms: '植株矮小，叶片发黄，茎基部变黑腐烂，有恶臭味。病株易从土中拔出。块茎从匍匐茎连接处开始腐烂，变为黑色黏软状。病原菌为细菌，主要靠种薯传播。',
    prevention: '1. 选用无病种薯，切块时严格刀具消毒\n2. 种薯处理：用杀菌剂浸泡\n3. 合理轮作\n4. 及时拔除病株',
    treatment: '发病初期用77%氢氧化铜可湿性粉剂500倍液灌根。以预防为主，主要依靠种薯消毒和田间卫生。',
    views: 620 },

  { id: 36, crop: '土豆', disease: '马铃薯病毒病', enName: 'Potato Viral Disease', category: '土豆', icon:'potato',
    symptoms: '常见有花叶型（叶片出现黄绿斑驳）、卷叶型（叶片向上卷曲）、束顶型（植株矮化、分枝减少）。主要通过蚜虫传播和种薯带毒。导致种性退化和产量下降。',
    prevention: '1. 使用脱毒种薯\n2. 防治蚜虫\n3. 及时拔除病株\n4. 在高海拔冷凉地区建立种薯繁育基地',
    treatment: '病毒病无特效治疗药剂。重点是使用脱毒种薯做好预防。发病初期可喷施抗病毒制剂配合杀蚜虫剂。',
    views: 890 },

  { id: 37, crop: '土豆', disease: '马铃薯疮痂病', enName: 'Potato Common Scab', category: '土豆', icon:'potato',
    symptoms: '块茎表面出现褐色粗糙的疮痂状病斑，呈木栓化隆起或凹陷。病斑大小形状不一，严重时连接成片。只危害块茎表皮，不深入内部，但严重影响商品价值。',
    prevention: '1. 选用抗病品种\n2. 酸性土壤发病轻，避免过量施用石灰\n3. 保持土壤湿度（结薯期保持土壤湿润）\n4. 与非寄主作物轮作4年以上',
    treatment: '播种前用50%多菌灵可湿性粉剂500倍液浸种，或沟施硫磺粉降低土壤pH值。灌溉可显著减轻发病。',
    views: 510 },

  { id: 38, crop: '土豆', disease: '马铃薯环腐病', enName: 'Potato Ring Rot', category: '土豆', icon:'potato',
    symptoms: '植株地上部表现萎蔫，叶片边缘向上卷曲。横切块茎可见维管束环呈淡黄色至褐色腐烂，挤压有菌脓溢出。后期块茎内部腐烂呈空洞状。细菌性病害，主要靠种薯传播。',
    prevention: '1. 严格检疫，使用无病种薯\n2. 切块时刀具用75%酒精或0.1%高锰酸钾消毒\n3. 整薯播种可有效预防\n4. 与非寄主作物轮作',
    treatment: '无有效治疗药剂。重点在于使用无病种薯和刀具消毒。发现病株立即拔除销毁。',
    views: 460 },

  { id: 39, crop: '土豆', disease: '马铃薯青枯病', enName: 'Potato Bacterial Wilt', category: '土豆', icon:'potato',
    symptoms: '植株叶片突然萎蔫，茎基部维管束变褐色，挤压有白色菌脓溢出。块茎芽眼处溢出菌脓，切开后维管束环变褐色。高温高湿条件下发病严重。',
    prevention: '1. 与禾本科作物轮作4年以上\n2. 选用抗病品种\n3. 高畦栽培，加强排水\n4. 发现病株立即拔除',
    treatment: '以预防为主。发病初期用77%氢氧化铜可湿性粉剂500倍液灌根。发病严重田块建议改种非寄主作物。',
    views: 530 },

  { id: 40, crop: '土豆', disease: '马铃薯干腐病', enName: 'Potato Dry Rot', category: '土豆', icon:'potato',
    symptoms: '块茎表面出现褐色凹陷斑，后病斑扩大，表皮皱缩。切开块茎可见内部组织变褐干腐，形成空洞，空洞内有白色或粉红色菌丝体。主要在储藏期发病。',
    prevention: '1. 收获时避免机械损伤\n2. 收获后晾晒2-3天，使伤口愈合\n3. 储藏前剔除伤病薯\n4. 储藏温度保持2-4℃，湿度85%-90%',
    treatment: '收获后在块茎伤口愈合期保持较高温湿度。储藏期间定期检查，及时剔除病薯。',
    views: 410 },

  { id: 41, crop: '土豆', disease: '马铃薯黑痣病', enName: 'Potato Black Scurf', category: '土豆', icon:'potato',
    symptoms: '茎基部和匍匐茎出现红褐色病斑，块茎表面附着黑色菌核（似泥土粘在表面，不易洗掉）。严重时影响出苗，造成缺苗断垄。',
    prevention: '1. 使用无病种薯\n2. 种薯处理：用25%嘧菌酯悬浮剂1000倍液浸泡\n3. 合理轮作\n4. 适当晚播，提高土温',
    treatment: '播种前用250g/L嘧菌酯悬浮剂或50%咯菌腈可湿性粉剂拌种处理。出苗后发病可用50%多菌灵灌根。',
    views: 370 },

  { id: 42, crop: '土豆', disease: '马铃薯粉痂病', enName: 'Potato Powdery Scab', category: '土豆', icon:'potato',
    symptoms: '块茎表面出现小疱状突起，后疱状突起破裂，散出深褐色粉末状物（休眠孢子囊球）。病斑呈火山口状凹陷。根系也可受害形成瘿瘤。',
    prevention: '1. 选用抗病品种\n2. 与非寄主作物轮作5年以上\n3. 避免在冷凉潮湿的土壤中种植\n4. 种薯消毒',
    treatment: '种薯用50%氟啶胺悬浮剂浸泡处理。发病严重田块建议长期轮作。',
    views: 290 },

  // ===== 小麦 (Wheat) - 10 entries =====
  { id: 43, crop: '小麦', disease: '小麦条锈病', enName: 'Wheat Stripe Rust', category: '小麦', icon:'wheat',
    symptoms: '主要发生在叶片上，鲜黄色的夏孢子堆沿叶脉排列成虚线状（条状）。孢子堆细小，排列整齐，似缝纫机扎过的线。发病严重时叶片枯黄，籽粒不饱满，减产可达30%-50%。',
    prevention: '1. 选用抗锈病品种\n2. 适期播种，避免过早播种\n3. 合理施肥，避免偏施氮肥\n4. 春季及时灌溉，增强植株抗性',
    treatment: '发病初期喷施25%三唑酮可湿性粉剂1000倍液，或250g/L嘧菌酯悬浮剂1500倍液，或430g/L戊唑醇悬浮剂3000-4000倍液。大田可用15%三唑酮可湿性粉剂50-60g/亩喷施。',
    views: 1200 },

  { id: 44, crop: '小麦', disease: '小麦叶锈病', enName: 'Wheat Leaf Rust', category: '小麦', icon:'wheat',
    symptoms: '叶片上散生圆形或近圆形的橘红色夏孢子堆，表皮破裂后散出铁锈色粉末。孢子堆主要发生在叶面，不穿透叶片。后期产生黑色冬孢子堆。',
    prevention: '1. 选用抗病品种\n2. 适期播种\n3. 合理密植\n4. 收获后深翻灭茬',
    treatment: '孕穗至抽穗期病叶率达5%时开始防治。喷施25%三唑酮可湿性粉剂1000倍液，或12.5%烯唑醇可湿性粉剂2000倍液。',
    views: 780 },

  { id: 45, crop: '小麦', disease: '小麦白粉病', enName: 'Wheat Powdery Mildew', category: '小麦', icon:'wheat',
    symptoms: '叶片表面出现白色绒絮状霉斑，后扩大连片覆盖叶片。霉层逐渐变灰褐色，上面散生黑色小粒点。严重时叶片发黄枯死，植株矮小。',
    prevention: '1. 选用抗白粉病品种\n2. 合理施肥，避免过量施氮\n3. 合理密植，改善通风\n4. 适期播种',
    treatment: '病叶率达10%时开始防治。喷施25%三唑酮可湿性粉剂1000-1500倍液，或250g/L嘧菌酯悬浮剂1500倍液，或12.5%烯唑醇可湿性粉剂2000倍液。',
    views: 650 },

  { id: 46, crop: '小麦', disease: '小麦赤霉病', enName: 'Wheat Fusarium Head Blight', category: '小麦', icon:'wheat',
    symptoms: '穗部受害后颖壳上出现水渍状褐色斑点，后蔓延至全穗。湿度大时颖壳缝隙和小穗基部出现粉红色霉层（分生孢子）。籽粒干瘪，品质下降，且含有毒素（DON），危害人畜健康。',
    prevention: '1. 选用抗赤霉病品种\n2. 深耕灭茬，减少菌源\n3. 合理施肥，避免过量施氮\n4. 开沟排水，降低田间湿度',
    treatment: '抽穗扬花期是防治关键期。喷施50%多菌灵可湿性粉剂800-1000倍液，或25%氰烯菌酯悬浮剂1500-2000倍液，或430g/L戊唑醇悬浮剂3000倍液。',
    views: 1400 },

  { id: 47, crop: '小麦', disease: '小麦纹枯病', enName: 'Wheat Sharp Eyespot', category: '小麦', icon:'wheat',
    symptoms: '主要危害茎基部和叶鞘。叶鞘出现中央灰白色、边缘褐色的云纹状病斑。茎秆病斑可深入内部，造成茎秆软腐倒伏。严重时导致白穗、枯孕穗。',
    prevention: '1. 合理轮作（与油菜、豆科作物轮作）\n2. 适期播种，控制播量\n3. 合理施肥，增施磷钾肥\n4. 春季及时排水',
    treatment: '返青至拔节期用24%噻呋酰胺悬浮剂20-30ml/亩，或250g/L嘧菌酯悬浮剂30ml/亩，对水30kg喷施。注意喷到茎基部。',
    views: 580 },

  { id: 48, crop: '小麦', disease: '小麦全蚀病', enName: 'Wheat Take-all', category: '小麦', icon:'wheat',
    symptoms: '苗期至成株期均可发病。根部变黑腐烂，茎基部1-2节变为黑褐色（"黑脚"症状）。抽穗后出现白穗。病株易拔起。田间呈点片发生，逐年扩大。',
    prevention: '1. 与非禾本科作物轮作3年以上\n2. 增施腐熟有机肥和磷肥\n3. 使用生物制剂（荧光假单胞菌等）处理种子',
    treatment: '播种前用12.5%硅噻菌胺悬浮剂拌种。返青期用250g/L嘧菌酯悬浮剂灌根。以预防为主。',
    views: 440 },

  { id: 49, crop: '小麦', disease: '小麦散黑穗病', enName: 'Wheat Loose Smut', category: '小麦', icon:'wheat',
    symptoms: '抽穗后整个穗部变为黑色粉末状（冬孢子），外面仅有一层薄膜包裹，薄膜破裂后黑粉散出，最后只剩穗轴。属于系统性侵染病害，一年只侵染一次。',
    prevention: '1. 使用无病种子\n2. 种子处理：用25%三唑酮可湿性粉剂或50%多菌灵可湿性粉剂拌种\n3. 建立无病留种田',
    treatment: '主要在播种前进行种子处理。抽穗后发现病穗应及时剪除销毁，防止传播下季作物。',
    views: 380 },

  { id: 50, crop: '小麦', disease: '小麦腥黑穗病', enName: 'Wheat Common Bunt', category: '小麦', icon:'wheat',
    symptoms: '病穗略短，颖壳张开，籽粒变为黑色菌瘿（内部充满黑粉）。菌瘿有鱼腥味（三甲胺）。收获时菌瘿破裂，黑粉散出污染健康籽粒和土壤。',
    prevention: '1. 种子处理是关键：用25%三唑酮可湿性粉剂或50%多菌灵拌种\n2. 使用无病种子\n3. 与非寄主作物轮作',
    treatment: '播前药剂拌种是最有效的防治方法。加强检疫，防止病菌随种子调运传播。',
    views: 320 },

  { id: 51, crop: '小麦', disease: '小麦根腐病', enName: 'Wheat Common Root Rot', category: '小麦', icon:'wheat',
    symptoms: '根部变褐腐烂，次生根减少。茎基部出现褐色条斑。叶片出现褐色斑点和枯尖。籽粒受害后出现黑胚（胚部变黑），影响发芽和品质。',
    prevention: '1. 与非禾本科作物轮作\n2. 深耕灭茬\n3. 种子处理（用咯菌腈或苯醚甲环唑拌种）\n4. 适期播种',
    treatment: '播种前用25g/L咯菌腈悬浮种衣剂或3%苯醚甲环唑悬浮种衣剂拌种。生长后期叶面喷施杀菌剂可减少黑胚率。',
    views: 360 },

  { id: 52, crop: '小麦', disease: '小麦雪霉叶枯病', enName: 'Wheat Snow Mold', category: '小麦', icon:'wheat',
    symptoms: '叶片出现水渍状暗绿色病斑，后扩大为大型梭形或椭圆形病斑，中央黄褐色，边缘不明显。湿度大时病斑表面产生粉红色霉层和菌丝。多在积雪覆盖后发生。',
    prevention: '1. 合理轮作\n2. 秋翻深耕\n3. 合理施肥\n4. 春季积雪融化后及时排水',
    treatment: '返青后喷施50%多菌灵可湿性粉剂800倍液，或70%甲基硫菌灵可湿性粉剂1000倍液。',
    views: 280 },

  // ===== 水稻 (Rice) - 10 entries =====
  { id: 53, crop: '水稻', disease: '水稻稻瘟病', enName: 'Rice Blast', category: '水稻', icon:'wheat',
    symptoms: '苗瘟：秧苗基部变褐枯死。叶瘟：叶片出现梭形病斑，中央灰白色，边缘褐色，外围有黄色晕圈。节瘟：茎节变黑腐烂，易折断。穗颈瘟：穗颈节变褐坏死，造成白穗。是水稻第一大病害。',
    prevention: '1. 选用抗病品种\n2. 合理施肥，避免过量偏施氮肥\n3. 合理灌溉，浅水勤灌\n4. 处理病稻草，减少菌源',
    treatment: '发病初期喷施75%三环唑可湿性粉剂2000-3000倍液，或40%稻瘟灵乳油800-1000倍液，或250g/L嘧菌酯悬浮剂1500倍液。穗颈瘟在破口期和齐穗期各喷1次。',
    views: 1680 },

  { id: 54, crop: '水稻', disease: '水稻纹枯病', enName: 'Rice Sheath Blight', category: '水稻', icon:'wheat',
    symptoms: '叶鞘出现暗绿色水渍状云纹状病斑，后扩大为不规则形大斑，边缘褐色，中央灰绿色。病斑可向上蔓延至叶片。严重时造成茎秆软腐倒伏，导致籽粒不饱满。',
    prevention: '1. 合理密植，改善通风\n2. 合理施肥，增施磷钾肥\n3. 浅水灌溉，适时晒田\n4. 打捞菌核（浪渣）',
    treatment: '分蘖末期至孕穗期病丛率达15%时防治。用24%噻呋酰胺悬浮剂20-30ml/亩，或250g/L嘧菌酯悬浮剂30ml/亩，或50%己唑醇水分散粒剂10g/亩对水喷施。',
    views: 1250 },

  { id: 55, crop: '水稻', disease: '水稻白叶枯病', enName: 'Rice Bacterial Blight', category: '水稻', icon:'wheat',
    symptoms: '叶片边缘出现黄白色波纹状病斑，病健交界处有波浪线。湿度大时病斑表面有淡黄色菌脓溢出，干燥后形成蜜黄色小粒。严重时叶片枯白卷曲。',
    prevention: '1. 选用抗病品种\n2. 种子消毒\n3. 合理施肥，避免偏施氮肥\n4. 大水漫灌会加速病菌传播',
    treatment: '发病初期用20%噻菌铜悬浮剂100-125ml/亩，或20%叶枯唑可湿性粉剂100-125g/亩，或50%氯溴异氰尿酸可湿性粉剂50-60g/亩对水喷施。',
    views: 920 },

  { id: 56, crop: '水稻', disease: '水稻稻曲病', enName: 'Rice False Smut', category: '水稻', icon:'wheat',
    symptoms: '穗部个别谷粒变为墨绿色或黑色稻曲球（菌核），比正常谷粒大数倍，外面覆盖一层墨绿色粉末。不仅影响产量，且稻曲球含有毒素，危害人畜健康。',
    prevention: '1. 选用抗病品种\n2. 种子消毒\n3. 合理施肥，避免偏施氮肥和迟施穗肥\n4. 破口前7-10天是防治关键期',
    treatment: '破口前7-10天喷施430g/L戊唑醇悬浮剂15-20ml/亩，或250g/L嘧菌酯悬浮剂30ml/亩。抽穗后再喷1次效果更好。',
    views: 760 },

  { id: 57, crop: '水稻', disease: '水稻恶苗病', enName: 'Rice Bakanae Disease', category: '水稻', icon:'wheat',
    symptoms: '秧苗徒长，比正常苗高而瘦弱，叶色淡黄。成株期病株比健株高，节间伸长，茎秆细弱，分蘖少或不分蘖。病株后期茎基部变褐腐烂，表面产生白色或粉红色霉层。',
    prevention: '1. 种子处理是关键：用25%咪鲜胺乳油3000倍液浸种48小时\n2. 选用无病种子\n3. 苗床消毒',
    treatment: '主要在播种前进行种子消毒。生长期发现病株及时拔除。',
    views: 580 },

  { id: 58, crop: '水稻', disease: '水稻胡麻斑病', enName: 'Rice Brown Spot', category: '水稻', icon:'wheat',
    symptoms: '叶片出现椭圆形或近圆形褐色小斑点，似芝麻粒大小，周围有黄色晕圈。严重时叶片布满病斑，变黄枯死。谷粒也可受害，形成褐色斑点，影响米质。',
    prevention: '1. 合理施肥，注意补充钾肥和微量元素（尤其是锌、硅）\n2. 改良土壤，防止土壤贫瘠\n3. 浅水灌溉，适时晒田',
    treatment: '发病初期喷施75%三环唑可湿性粉剂2000倍液+磷酸二氢钾，或250g/L嘧菌酯悬浮剂1500倍液。',
    views: 450 },

  { id: 59, crop: '水稻', disease: '水稻条纹叶枯病', enName: 'Rice Stripe Virus', category: '水稻', icon:'wheat',
    symptoms: '心叶出现黄白色褪绿条纹，后扩展至整个叶片。病株矮化，分蘖减少，不能正常抽穗或抽畸形穗。由灰飞虱传播的病毒病，苗期感染最重。',
    prevention: '1. 选用抗病品种\n2. 治虫防病：重点防治灰飞虱\n3. 调整播期，避开灰飞虱迁飞高峰\n4. 清除田边杂草',
    treatment: '以治虫为主：用25%吡蚜酮可湿性粉剂20-30g/亩或25%噻虫嗪水分散粒剂10-15g/亩防治灰飞虱。配合喷施20%吗胍·乙酸铜可湿性粉剂。',
    views: 680 },

  { id: 60, crop: '水稻', disease: '水稻细菌性条斑病', enName: 'Rice Bacterial Leaf Streak', category: '水稻', icon:'wheat',
    symptoms: '叶片出现暗绿色水渍状细条斑，沿叶脉扩展，后期变为黄褐色。湿度大时病斑表面有大量黄色菌脓溢出。与白叶枯病不同的是，条斑不受叶脉限制，可穿透叶片。',
    prevention: '1. 严格检疫，防止病菌随种子传播\n2. 种子消毒\n3. 合理施肥\n4. 避免串灌漫灌',
    treatment: '发病初期用20%噻菌铜悬浮剂100-125ml/亩，或50%氯溴异氰尿酸可湿性粉剂50-60g/亩对水喷施。',
    views: 520 },

  { id: 61, crop: '水稻', disease: '水稻干尖线虫病', enName: 'Rice White Tip Nematode', category: '水稻', icon:'wheat',
    symptoms: '孕穗期上部叶片尖端2-5cm变为黄白色或灰白色，干枯卷曲。病株略矮，穗部变小。由干尖线虫引起，主要靠种子传播。',
    prevention: '1. 种子处理是关键：温水浸种（52-54℃浸10分钟）\n2. 使用无病种子\n3. 苗床消毒',
    treatment: '播种前用16%咪鲜·杀螟丹可湿性粉剂400倍液浸种48小时，或温水浸种处理。',
    views: 340 },

  { id: 62, crop: '水稻', disease: '水稻菌核秆腐病', enName: 'Rice Stem Rot', category: '水稻', icon:'wheat',
    symptoms: '茎秆基部叶鞘变褐腐烂，剥开叶鞘可见茎秆表面和内部有大量黑色小菌核。茎秆腐烂后易折断倒伏，造成减产。多在生长后期发生。',
    prevention: '1. 合理施肥，避免过量施氮\n2. 浅水灌溉，适时晒田\n3. 收获后深翻，将菌核翻入深层\n4. 轮作',
    treatment: '分蘖末期用250g/L嘧菌酯悬浮剂30ml/亩或50%多菌灵可湿性粉剂100g/亩对水喷施在茎基部。',
    views: 290 },
])

// Search & filter
const filteredArticles = computed(() => {
  let result = allArticles.value
  if (selectedCategory.value !== 'all') {
    result = result.filter(a => a.category === selectedCategory.value)
  }
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(a =>
      a.disease.toLowerCase().includes(q) ||
      a.crop.toLowerCase().includes(q) ||
      a.enName.toLowerCase().includes(q) ||
      a.symptoms.toLowerCase().includes(q)
    )
  }
  return result
})

const categories = computed(() => {
  const map = new Map<string, { name: string; icon: string; count: number }>()
  for (const a of allArticles.value) {
    if (!map.has(a.category)) {
      map.set(a.category, { name: a.category, icon: a.icon, count: 0 })
    }
    map.get(a.category)!.count++
  }
  return Array.from(map.values())
})

const communityQuestions = ref([
  { username: '张农技员', content: '番茄晚疫病今年特别严重，请问除了打药还有别的方法吗？', time: '2小时前', replies: 5 },
  { username: '大棚老王', content: '黄瓜霜霉病怎么判断是发病初期？叶片上的小黄点就是吗？', time: '5小时前', replies: 3 },
  { username: '种植新手', content: '第一次种辣椒，请问病毒病和缺素症怎么区分？', time: '8小时前', replies: 7 },
  { username: '绿色农场', content: '马铃薯晚疫病气象预报说未来一周有雨，需要提前预防吗？', time: '昨天', replies: 4 },
  { username: '科技兴农', content: '水稻稻曲病对人有危害吗？收获时发现不少稻曲球。', time: '昨天', replies: 6 },
])

const articlesRef = ref<HTMLElement | null>(null)

// ── Panel state ──
const showPesticideGuide = ref(false)
const showFarmingCalendar = ref(false)
const showTreatmentPlans = ref(false)
const showQuestionModal = ref(false)
const newQuestion = ref({ username: '', content: '' })
const selectedPesticide = ref<any>(null)

// ── 农药使用指南数据 ──
const pesticideList = [
  { name: '代森锰锌', enName: 'Mancozeb', type: '保护性杀菌剂', target: '早疫病、晚疫病、叶霉病、斑枯病、炭疽病', dosage: '70% WP 500-600倍液', crops: '番茄、土豆、辣椒、黄瓜', usage: '发病前或发病初期叶面喷施，每7-10天喷1次，连续2-3次。不可与铜制剂及碱性农药混用。', interval: '7-15天', toxicity: '低毒' },
  { name: '多菌灵', enName: 'Carbendazim', type: '内吸性杀菌剂', target: '枯萎病、灰霉病、炭疽病、白粉病', dosage: '50% WP 500-800倍液', crops: '番茄、黄瓜、辣椒、小麦、水稻', usage: '发病初期喷施或灌根，每7-10天1次，连续2-3次。灌根每株200-300ml药液。', interval: '15-20天', toxicity: '低毒' },
  { name: '百菌清', enName: 'Chlorothalonil', type: '保护性杀菌剂', target: '早疫病、晚疫病、炭疽病、霜霉病', dosage: '75% WP 600-800倍液', crops: '番茄、黄瓜、辣椒、土豆', usage: '发病前预防性喷施，每7-10天1次。注意对鱼类有毒，远离水源施用。', interval: '7-14天', toxicity: '低毒' },
  { name: '甲霜灵锰锌', enName: 'Metalaxyl-M + Mancozeb', type: '内吸+保护复配', target: '晚疫病、霜霉病、疫病', dosage: '58% WP 500-600倍液', crops: '番茄、黄瓜、土豆、辣椒', usage: '发病初期喷施，每7天1次，连续2-3次。兼具治疗和保护作用。', interval: '7-14天', toxicity: '低毒' },
  { name: '三唑酮', enName: 'Triadimefon', type: '内吸性杀菌剂', target: '白粉病、锈病、黑穗病', dosage: '25% WP 1000-2000倍液', crops: '小麦、黄瓜、辣椒', usage: '发病初期喷施，每10-14天1次。对白粉病和锈病效果显著。', interval: '20天', toxicity: '低毒' },
  { name: '嘧菌酯', enName: 'Azoxystrobin', type: '甲氧基丙烯酸酯类', target: '白粉病、炭疽病、纹枯病、稻瘟病', dosage: '250g/L SC 1500倍液', crops: '小麦、水稻、黄瓜、番茄', usage: '发病初期喷施，每10-14天1次。广谱杀菌，兼具保护和治疗作用。', interval: '7-14天', toxicity: '低毒' },
  { name: '霜脲·锰锌', enName: 'Cymoxanil + Mancozeb', type: '内吸+保护复配', target: '晚疫病、霜霉病、疫病', dosage: '72% WP 600-800倍液', crops: '番茄、黄瓜、土豆', usage: '发病前或发病初期喷施，每5-7天1次。霜脲氰具有内吸治疗作用。', interval: '7天', toxicity: '低毒' },
  { name: '腐霉利', enName: 'Procymidone', type: '保护性杀菌剂', target: '灰霉病、菌核病', dosage: '50% WP 1000-1500倍液', crops: '番茄、黄瓜、辣椒', usage: '发病初期喷施，重点喷花器和果实，每7天1次。大棚使用效果好。', interval: '7天', toxicity: '低毒' },
  { name: '咯菌腈', enName: 'Fludioxonil', type: '保护性杀菌剂', target: '黑痣病、根腐病、黑胚病', dosage: '25g/L FS 拌种处理', crops: '土豆、小麦', usage: '播种前拌种或浸种处理。对种传和土传病害防效优异。', interval: '—', toxicity: '低毒' },
  { name: '三环唑', enName: 'Tricyclazole', type: '内吸性杀菌剂', target: '稻瘟病（特效药）', dosage: '75% WP 2000-3000倍液', crops: '水稻', usage: '防治穗颈瘟在破口期和齐穗期各喷1次。对稻瘟病有特效。', interval: '21天', toxicity: '低毒' },
  { name: '噻呋酰胺', enName: 'Thifluzamide', type: '内吸性杀菌剂', target: '纹枯病（特效药）', dosage: '24% SC 20-30ml/亩', crops: '水稻、小麦', usage: '分蘖末期至孕穗期喷施，重点喷茎基部。对纹枯病有特效。', interval: '14天', toxicity: '低毒' },
  { name: '戊唑醇', enName: 'Tebuconazole', type: '内吸性杀菌剂', target: '赤霉病、白粉病、锈病、稻曲病', dosage: '430g/L SC 3000-4000倍液', crops: '小麦、水稻', usage: '小麦扬花期防治赤霉病，水稻破口前防治稻曲病。', interval: '21天', toxicity: '低毒' },
  { name: '噻菌铜', enName: 'Thiodiazole Copper', type: '杀菌剂（细菌）', target: '青枯病、角斑病、疮痂病、白叶枯病', dosage: '20% SC 500-600倍液', crops: '番茄、辣椒、黄瓜、水稻', usage: '发病初期喷施或灌根，每7-10天1次。对细菌性病害效果较好。', interval: '7-14天', toxicity: '低毒' },
  { name: '氢氧化铜', enName: 'Copper Hydroxide', type: '杀菌剂（细菌+真菌）', target: '细菌性病害、部分真菌病害', dosage: '77% WP 500-800倍液', crops: '番茄、辣椒、黄瓜、土豆', usage: '发病初期喷施。铜制剂广谱杀菌，但注意敏感作物（如瓜类幼苗期慎用）。', interval: '7-10天', toxicity: '低毒' },
  { name: '阿维菌素', enName: 'Abamectin', type: '杀线虫/杀虫剂', target: '根结线虫、螨类、斑潜蝇', dosage: '1.8% EC 1000倍液', crops: '黄瓜、番茄', usage: '定植前灌穴或生长期灌根。对根结线虫效果良好。', interval: '7-14天', toxicity: '中等毒' },
  { name: '吡虫啉', enName: 'Imidacloprid', type: '内吸性杀虫剂', target: '蚜虫、飞虱、粉虱（传毒媒介）', dosage: '10% WP 1500-2000倍液', crops: '番茄、辣椒、水稻、小麦', usage: '配合抗病毒剂使用，防治传毒昆虫。每7-10天喷1次。', interval: '7-14天', toxicity: '低毒' },
  { name: '氰烯菌酯', enName: 'Phenamacril', type: '内吸性杀菌剂', target: '赤霉病（特效药）', dosage: '25% SC 1500-2000倍液', crops: '小麦', usage: '抽穗扬花期喷施，对赤霉病有特效且能降低毒素。', interval: '14天', toxicity: '低毒' },
  { name: '烯酰吗啉', enName: 'Dimethomorph', type: '内吸性杀菌剂', target: '疫病、霜霉病、晚疫病', dosage: '50% WP 1500-2000倍液', crops: '辣椒、黄瓜、土豆', usage: '发病初期灌根+喷施结合，每7天1次。抗性风险较低。', interval: '7天', toxicity: '低毒' },
  { name: '中生菌素', enName: 'Zhongshengmycin', type: '生物杀菌剂', target: '细菌性斑点病、角斑病、软腐病', dosage: '3% WP 800-1000倍液', crops: '番茄、黄瓜、辣椒', usage: '发病初期喷施，每7-10天1次。生物制剂，适合绿色食品生产。', interval: '7天', toxicity: '无毒' },
  { name: '宁南霉素', enName: 'Ningnanmycin', type: '生物抗病毒剂', target: '病毒病（多种作物）', dosage: '8% AS 500倍液', crops: '番茄、辣椒、水稻', usage: '发病初期配合杀蚜剂使用，每7天喷1次。增强植株免疫力。', interval: '7天', toxicity: '无毒' },
]

// ── 农事日历数据 ──
const farmingCalendar = [
  {
    season: '冬季', months: '12月-2月',
    tasks: [
      { title: '冬季清园', desc: '彻底清除田间病残体，减少越冬菌源。深翻土壤，冻死越冬害虫。', crops: '全部作物' },
      { title: '种子准备与消毒', desc: '选购抗病品种，进行种子消毒处理（温水浸种或药剂拌种）。', crops: '全部作物' },
      { title: '大棚维护', desc: '检修大棚薄膜和骨架，清洁棚膜提高透光率。', crops: '番茄、黄瓜、辣椒' },
      { title: '土壤改良', desc: '增施腐熟有机肥，酸性土壤可施用石灰调节pH至6.5-7.0。', crops: '全部作物' },
    ]
  },
  {
    season: '春季', months: '3月-5月',
    tasks: [
      { title: '春播育苗', desc: '3月上旬开始番茄、辣椒温室育苗。注意苗床消毒，培育无病壮苗。', crops: '番茄、辣椒' },
      { title: '春小麦播种', desc: '3月下旬至4月上旬播种春小麦，注意适期播种，过晚会加重锈病。', crops: '小麦' },
      { title: '早稻育秧', desc: '4月上旬育秧，苗床用三环唑浸种预防稻瘟病。', crops: '水稻' },
      { title: '黄瓜定植', desc: '4月中下旬大棚黄瓜定植，高畦覆膜，膜下滴灌降低棚内湿度。', crops: '黄瓜' },
      { title: '蚜虫监测', desc: '5月蚜虫迁飞高峰期，挂黄板监测，设置防虫网，预防病毒病传播。', crops: '番茄、辣椒' },
      { title: '马铃薯播种', desc: '3月下旬至4月上旬播种马铃薯，注意种薯切块刀具消毒。', crops: '土豆' },
      { title: '小麦春季管理', desc: '返青后追施拔节肥，喷施三唑酮防治白粉病和锈病。', crops: '小麦' },
    ]
  },
  {
    season: '夏季', months: '6月-8月',
    tasks: [
      { title: '番茄整枝打杈', desc: '及时整枝打杈改善通风，摘除下部老叶减少病害。高温季节注意遮阳降温。', crops: '番茄' },
      { title: '晚疫病监测', desc: '密切关注天气预报，连续阴雨前喷施霜脲·锰锌预防番茄/马铃薯晚疫病。', crops: '番茄、土豆' },
      { title: '水稻田间管理', desc: '浅水勤灌，适时晒田控蘖。分蘖末期防治纹枯病，破口前7-10天防治稻曲病。', crops: '水稻' },
      { title: '小麦收获', desc: '6月小麦收获，及时晾晒入库。赤霉病重发区单独收获病田。', crops: '小麦' },
      { title: '辣椒炭疽病防治', desc: '果实膨大期重点防治炭疽病，喷施嘧菌酯或百菌清，每7天1次。', crops: '辣椒' },
      { title: '高温闷棚', desc: '夏季休闲期，大棚覆膜密闭，使土温升至55℃以上持续2小时，杀灭土传病菌和根结线虫。', crops: '全部作物' },
      { title: '轮作规划', desc: '收获后及时清理残茬，制定下季轮作计划。茄科→禾本科→豆科轮作。', crops: '全部作物' },
    ]
  },
  {
    season: '秋季', months: '9月-11月',
    tasks: [
      { title: '水稻收获', desc: '9-10月水稻收获，感病田块稻草集中处理（深埋或焚烧），切勿堆放在田边。', crops: '水稻' },
      { title: '秋播准备', desc: '10月冬小麦播种，播种前用咯菌腈或苯醚甲环唑拌种防治根腐病和黑穗病。', crops: '小麦' },
      { title: '大棚秋延后', desc: '9月秋番茄/黄瓜定植，注意加强通风防治灰霉病。', crops: '番茄、黄瓜' },
      { title: '深翻灭茬', desc: '收获后立即深翻，将病残体和菌核翻入深层土壤，加速分解减少菌源。', crops: '全部作物' },
      { title: '生物防治', desc: '秋季施用生物菌肥（木霉菌、枯草芽孢杆菌），抑制土壤中病原菌。', crops: '全部作物' },
    ]
  }
]

// ── 防治方案汇总 ──
const treatmentPlans = computed(() => {
  const grouped: Record<string, any[]> = {}
  for (const a of allArticles.value) {
    if (a.treatment && a.treatment.trim()) {
      if (!grouped[a.crop]) grouped[a.crop] = []
      grouped[a.crop].push(a)
    }
  }
  return Object.entries(grouped).map(([crop, articles]) => ({
    crop,
    icon: articles[0]?.icon || 'leaf',
    count: articles.length,
    articles
  }))
})

function openArticle(article: any) { selectedArticle.value = article }
function closeArticle() { selectedArticle.value = null }

// ── Panel open/close ──
function openPesticideGuide() { showPesticideGuide.value = true }
function closePesticideGuide() { showPesticideGuide.value = false; selectedPesticide.value = null }
function openFarmingCalendar() { showFarmingCalendar.value = true }
function closeFarmingCalendar() { showFarmingCalendar.value = false }
function openTreatmentPlans() { showTreatmentPlans.value = true }
function closeTreatmentPlans() { showTreatmentPlans.value = false }
function openQuestionModal() { newQuestion.value = { username: '', content: '' }; showQuestionModal.value = true }
function closeQuestionModal() { showQuestionModal.value = false }

function submitQuestion() {
  if (!newQuestion.value.username.trim() || !newQuestion.value.content.trim()) return
  communityQuestions.value.unshift({
    username: newQuestion.value.username.trim(),
    content: newQuestion.value.content.trim(),
    time: '刚刚',
    replies: 0
  })
  closeQuestionModal()
}

function quickLinkAction(query: string, category?: string) {
  if (category !== undefined) selectedCategory.value = category
  searchQuery.value = query
  setTimeout(() => {
    articlesRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }, 100)
}
</script>

<template>
  <div class="space-y-6">
    <div class="page-header animate-fade-down">
      <h2>知识库</h2>
      <p>农作物病害知识大全 · 共 {{ allArticles.length }} 篇 · 覆盖6大类作物</p>
    </div>

    <!-- Search -->
    <div class="glass animate-fade-up">
      <div style="display:flex;gap:12px;flex-wrap:wrap;">
        <div style="flex:1;min-width:250px;">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索病害、作物、防治方法..."
            class="form-input"
          />
        </div>
        <select v-model="selectedCategory" class="form-select" style="width:180px;">
          <option value="all"><svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="vertical-align:middle;margin-right:4px;"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>全部分类 ({{ allArticles.length }})</option>
          <option v-for="cat in categories" :key="cat.name" :value="cat.name">
            {{ cat.name }} ({{ cat.count }})
          </option>
        </select>
      </div>
    </div>

    <!-- Category Filter Cards -->
    <div class="stats-grid animate-fade-up stagger-2">
      <div
        v-for="cat in categories" :key="cat.name"
        :class="['glass stat-card', { 'pulse-green': selectedCategory === cat.name }]"
        style="cursor:pointer;"
        @click="selectedCategory = selectedCategory === cat.name ? 'all' : cat.name"
      >
        <div class="stat-icon" style="background:rgba(76,175,80,0.15);color:#4caf50;display:flex;align-items:center;justify-content:center;">
          <svg v-if="cat.icon === 'tomato'" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 3v3M12 18v3"/></svg>
          <svg v-else-if="cat.icon === 'cucumber'" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><ellipse cx="12" cy="12" rx="6" ry="10"/></svg>
          <svg v-else-if="cat.icon === 'pepper'" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 2c-3 0-7 3-7 9s4 11 7 11 7-5 7-11-4-9-7-9z"/></svg>
          <svg v-else-if="cat.icon === 'potato'" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><ellipse cx="12" cy="12" rx="8" ry="6"/></svg>
          <svg v-else-if="cat.icon === 'wheat'" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 2v20M8 6c0 0 4-2 4-4 0 2 4 4 4 4"/><path d="M8 10c0 0 4-2 4-4 0 2 4 4 4 4"/><path d="M8 14c0 0 4-2 4-4 0 2 4 4 4 4"/></svg>
          <svg v-else width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/></svg>
        </div>
        <div class="stat-value">{{ cat.name }}</div>
        <div class="stat-label">{{ cat.count }} 篇知识</div>
      </div>
    </div>

    <div style="display:grid;grid-template-columns:2fr 1fr;gap:20px;align-items:start;">
      <!-- Knowledge Articles Grid - 3 columns -->
      <div class="glass">
        <h3 style="font-weight:700;margin-bottom:16px;font-size:1.05rem;">
          <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="vertical-align:middle;margin-right:6px;"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M4 4v16a2.5 2.5 0 002.5 2.5H20V2H6.5A2.5 2.5 0 004 4.5V4z"/></svg>{{ searchQuery ? `搜索结果` : '知识文章' }}
          <span style="font-weight:400;font-size:0.8rem;color:var(--text-tertiary);margin-left:8px;">
            ({{ filteredArticles.length }} 篇)
          </span>
        </h3>

        <div v-if="filteredArticles.length === 0" style="text-align:center;padding:48px;">
          <div style="margin-bottom:12px;opacity:0.3;"><svg width="48" height="48" fill="none" stroke="currentColor" stroke-width="1" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg></div>
          <p style="color:var(--text-secondary);">暂无相关知识</p>
        </div>

        <div v-else ref="articlesRef" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px;">
          <div
            v-for="(article, idx) in filteredArticles.slice(0, 30)"
            :key="article.id"
            class="section-card animate-fade-up"
            :class="`stagger-${Math.min(idx%8+1,8)}`"
            style="cursor:pointer;padding:16px;"
            @click="openArticle(article)"
          >
            <div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:8px;">
              <span class="tag tag-success" style="font-size:0.7rem;">{{ article.category }}</span>
              <span style="font-size:0.7rem;color:var(--text-muted);">{{ article.views }}读</span>
            </div>
            <h4 style="font-weight:700;font-size:0.92rem;margin-bottom:4px;">{{ article.disease }}</h4>
            <p style="font-size:0.72rem;color:var(--text-muted);margin-bottom:8px;">{{ article.enName }}</p>
            <p style="font-size:0.76rem;color:var(--text-secondary);line-height:1.5;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;">
              {{ article.symptoms.substring(0, 100) }}...
            </p>
            <div style="margin-top:10px;display:flex;gap:6px;">
              <span style="padding:2px 8px;border-radius:6px;font-size:0.68rem;background:rgba(255,255,255,0.05);color:var(--text-tertiary);">
                <svg width="12" height="12" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="vertical-align:middle;margin-right:3px;"><circle cx="12" cy="12" r="8"/><path d="M8 12h8M12 8v8"/></svg>{{ article.disease }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Community Sidebar -->
      <div class="space-y-4 animate-slide-right">
        <!-- Community Q&A -->
        <div class="glass">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
            <h3 style="font-weight:700;font-size:1rem;"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="vertical-align:middle;margin-right:6px;"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>社区问答</h3>
            <button class="btn btn-primary btn-sm" @click="openQuestionModal">提问</button>
          </div>
          <div class="space-y-2" style="max-height:360px;overflow-y:auto;">
            <div
              v-for="q in communityQuestions" :key="q.content"
              style="padding:10px 12px;background:rgba(255,255,255,0.03);border-radius:10px;"
            >
              <p style="font-size:0.82rem;line-height:1.5;">{{ q.content }}</p>
              <div style="display:flex;justify-content:space-between;margin-top:6px;">
                <span style="font-size:0.72rem;color:var(--text-muted);">{{ q.username }}</span>
                <div style="display:flex;gap:12px;font-size:0.7rem;color:var(--text-muted);">
                  <span>{{ q.time }}</span>
                  <span>{{ q.replies }} 回复</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Links -->
        <div class="glass">
          <h3 style="font-weight:700;margin-bottom:12px;font-size:1rem;"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="vertical-align:middle;margin-right:6px;"><path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/></svg>常用链接</h3>
          <div class="space-y-2">
            <button class="btn btn-outline btn-sm" style="width:100%;justify-content:flex-start;"
              @click="quickLinkAction('', 'all')">
              <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="vertical-align:middle;margin-right:6px;"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M4 4v16a2.5 2.5 0 002.5 2.5H20V2H6.5A2.5 2.5 0 004 4.5V4z"/></svg>病虫害图谱
            </button>
            <button class="btn btn-outline btn-sm" style="width:100%;justify-content:flex-start;"
              @click="openPesticideGuide">
              <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="vertical-align:middle;margin-right:6px;"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>农药使用指南
            </button>
            <button class="btn btn-outline btn-sm" style="width:100%;justify-content:flex-start;"
              @click="openFarmingCalendar">
              <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="vertical-align:middle;margin-right:6px;"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>农事日历
            </button>
            <button class="btn btn-outline btn-sm" style="width:100%;justify-content:flex-start;"
              @click="openTreatmentPlans">
              <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="vertical-align:middle;margin-right:6px;"><path d="M9 3h6M10 3v4.5L6 19.1A2 2 0 007.8 22h8.4a2 2 0 001.8-2.9L14 7.5V3"/></svg>防治方案
            </button>
          </div>
        </div>

        <!-- Stats -->
        <div class="glass">
          <h3 style="font-weight:700;margin-bottom:12px;font-size:1rem;"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="vertical-align:middle;margin-right:6px;"><rect x="18" y="3" width="4" height="18"/><rect x="10" y="8" width="4" height="13"/><rect x="2" y="13" width="4" height="8"/></svg>知识库统计</h3>
          <div class="space-y-2">
            <div style="display:flex;justify-content:space-between;padding:8px 10px;background:rgba(255,255,255,0.03);border-radius:8px;">
              <span style="font-size:0.82rem;color:var(--text-secondary);">知识文章</span>
              <span style="font-weight:700;">{{ allArticles.length }} 篇</span>
            </div>
            <div style="display:flex;justify-content:space-between;padding:8px 10px;background:rgba(255,255,255,0.03);border-radius:8px;">
              <span style="font-size:0.82rem;color:var(--text-secondary);">覆盖作物</span>
              <span style="font-weight:700;">6 类</span>
            </div>
            <div style="display:flex;justify-content:space-between;padding:8px 10px;background:rgba(255,255,255,0.03);border-radius:8px;">
              <span style="font-size:0.82rem;color:var(--text-secondary);">社区问题</span>
              <span style="font-weight:700;">{{ communityQuestions.length }} 条</span>
            </div>
            <div style="display:flex;justify-content:space-between;padding:8px 10px;background:rgba(255,255,255,0.03);border-radius:8px;">
              <span style="font-size:0.82rem;color:var(--text-secondary);">数据来源</span>
              <span style="font-weight:700;">PlantVillage + 农科院</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Article Detail Modal -->
    <div v-if="selectedArticle" class="modal-overlay" @click.self="closeArticle">
      <div class="modal-content animate-scale-in">
        <div style="padding:24px 28px;border-bottom:1px solid rgba(255,255,255,0.06);">
          <div style="display:flex;justify-content:space-between;align-items:start;">
            <div>
              <span class="tag tag-success" style="margin-bottom:8px;">{{ selectedArticle.category }}</span>
              <h2 style="font-weight:700;font-size:1.3rem;margin-top:8px;">{{ selectedArticle.disease }}</h2>
              <p style="color:var(--text-tertiary);font-size:0.85rem;">{{ selectedArticle.enName }}</p>
            </div>
            <button @click="closeArticle" style="padding:6px;border-radius:8px;border:none;background:rgba(255,255,255,0.08);color:var(--text-primary);cursor:pointer;font-size:1.2rem;"><svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
          </div>
        </div>
        <div style="padding:20px 28px 28px;" class="space-y-4">
          <div style="padding:16px;background:rgba(244,67,54,0.08);border-radius:12px;border-left:3px solid #f44336;">
            <h4 style="font-weight:700;margin-bottom:10px;"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="vertical-align:middle;margin-right:6px;"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>症状表现</h4>
            <p style="color:var(--text-secondary);line-height:1.7;white-space:pre-line;">{{ selectedArticle.symptoms }}</p>
          </div>
          <div style="padding:16px;background:rgba(33,150,243,0.08);border-radius:12px;border-left:3px solid #2196f3;">
            <h4 style="font-weight:700;margin-bottom:10px;"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="vertical-align:middle;margin-right:6px;"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>预防措施</h4>
            <p style="color:var(--text-secondary);line-height:1.7;white-space:pre-line;">{{ selectedArticle.prevention }}</p>
          </div>
          <div style="padding:16px;background:rgba(76,175,80,0.08);border-radius:12px;border-left:3px solid #4caf50;">
            <h4 style="font-weight:700;margin-bottom:10px;"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="vertical-align:middle;margin-right:6px;"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>治疗方案</h4>
            <p style="color:var(--text-secondary);line-height:1.7;white-space:pre-line;">{{ selectedArticle.treatment }}</p>
          </div>
        </div>
        <div style="padding:16px 28px;border-top:1px solid rgba(255,255,255,0.06);display:flex;justify-content:space-between;align-items:center;">
          <span style="font-size:0.8rem;color:var(--text-muted);">{{ selectedArticle.views }} 次阅读 · <svg width="12" height="12" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="vertical-align:middle;margin-right:3px;"><circle cx="12" cy="12" r="8"/><path d="M8 12h8M12 8v8"/></svg>{{ selectedArticle.disease }} · <svg width="12" height="12" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="vertical-align:middle;margin-right:3px;"><path d="M12 2L2 7l10 5 10-5-10-5z"/></svg>{{ selectedArticle.crop }}</span>
          <button @click="closeArticle" class="btn btn-outline btn-sm">关闭</button>
        </div>
      </div>
    </div>

    <!-- 农药使用指南 Panel -->
    <div v-if="showPesticideGuide" class="modal-overlay" @click.self="closePesticideGuide">
      <div class="modal-content animate-scale-in" style="max-width:820px;max-height:85vh;overflow-y:auto;">
        <div style="padding:20px 28px;border-bottom:1px solid rgba(255,255,255,0.06);display:flex;justify-content:space-between;align-items:center;">
          <div>
            <h2 style="font-weight:700;font-size:1.15rem;display:flex;align-items:center;gap:8px;"><svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>农药使用指南</h2>
            <p style="font-size:0.75rem;color:var(--text-tertiary);">共 {{ pesticideList.length }} 种常用农药 · 含杀菌剂/杀虫剂/杀线虫剂</p>
          </div>
          <button @click="closePesticideGuide" style="padding:6px;border-radius:8px;border:none;background:rgba(255,255,255,0.08);color:var(--text-primary);cursor:pointer;font-size:1.2rem;"><svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
        </div>
        <div style="padding:20px 28px;">
          <!-- Legend -->
          <div style="display:flex;gap:16px;flex-wrap:wrap;margin-bottom:16px;font-size:0.75rem;color:var(--text-secondary);">
            <span>低毒</span><span>中等毒</span><span>SC=悬浮剂</span><span>WP=可湿性粉剂</span><span>EC=乳油</span><span>AS=水剂</span>
          </div>
          <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(350px,1fr));gap:12px;">
            <div v-for="p in pesticideList" :key="p.name"
              style="padding:14px 16px;background:rgba(255,255,255,0.03);border-radius:12px;cursor:pointer;border:1px solid rgba(255,255,255,0.05);transition:all 0.2s;"
              :style="selectedPesticide?.name === p.name ? 'border-color:rgba(76,175,80,0.5);background:rgba(76,175,80,0.08);' : ''"
              @click="selectedPesticide = selectedPesticide?.name === p.name ? null : p">
              <div style="display:flex;justify-content:space-between;align-items:start;">
                <div>
                  <h4 style="font-weight:700;font-size:0.92rem;">{{ p.name }}</h4>
                  <span style="font-size:0.68rem;color:var(--text-muted);">{{ p.enName }}</span>
                </div>
                <span :style="`padding:2px 8px;border-radius:6px;font-size:0.65rem;font-weight:600;${p.toxicity==='无毒'?'background:rgba(76,175,80,0.2);color:#4caf50;':p.toxicity==='低毒'?'background:rgba(76,175,80,0.15);color:#81c784;':'background:rgba(255,152,0,0.2);color:#ffb74d;'}`">{{ p.toxicity }}</span>
              </div>
              <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:8px;">
                <span style="padding:2px 8px;border-radius:6px;font-size:0.68rem;background:rgba(33,150,243,0.15);color:#64b5f6;">{{ p.type }}</span>
                <span style="padding:2px 8px;border-radius:6px;font-size:0.68rem;background:rgba(255,255,255,0.05);color:var(--text-secondary);">{{ p.crops }}</span>
              </div>
              <!-- Expanded detail -->
              <div v-if="selectedPesticide?.name === p.name" style="margin-top:12px;padding-top:12px;border-top:1px solid rgba(255,255,255,0.06);" class="space-y-2">
                <div><span style="font-size:0.7rem;color:var(--text-tertiary);">防治对象：</span><span style="font-size:0.78rem;">{{ p.target }}</span></div>
                <div><span style="font-size:0.7rem;color:var(--text-tertiary);">推荐用量：</span><span style="font-size:0.78rem;">{{ p.dosage }}</span></div>
                <div><span style="font-size:0.7rem;color:var(--text-tertiary);">使用方法：</span><span style="font-size:0.78rem;line-height:1.6;">{{ p.usage }}</span></div>
                <div><span style="font-size:0.7rem;color:var(--text-tertiary);">安全间隔期：</span><span style="font-size:0.78rem;">{{ p.interval }}</span></div>
              </div>
            </div>
          </div>
          <p style="margin-top:16px;font-size:0.7rem;color:var(--text-muted);text-align:center;"><svg width="12" height="12" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="vertical-align:middle;margin-right:4px;"><path d="M12 2L2 22h20L12 2z"/><path d="M12 14v4"/><circle cx="12" cy="16.5" r="0.5" fill="currentColor"/></svg>以上为通用推荐，具体用量请参照产品标签和当地农技部门指导</p>
        </div>
      </div>
    </div>

    <!-- 农事日历 Panel -->
    <div v-if="showFarmingCalendar" class="modal-overlay" @click.self="closeFarmingCalendar">
      <div class="modal-content animate-scale-in" style="max-width:820px;max-height:85vh;overflow-y:auto;">
        <div style="padding:20px 28px;border-bottom:1px solid rgba(255,255,255,0.06);display:flex;justify-content:space-between;align-items:center;">
          <div>
            <h2 style="font-weight:700;font-size:1.15rem;display:flex;align-items:center;gap:8px;"><svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>农事日历</h2>
            <p style="font-size:0.75rem;color:var(--text-tertiary);">四季农事管理 · 病虫害预防为主的综合农事建议</p>
          </div>
          <button @click="closeFarmingCalendar" style="padding:6px;border-radius:8px;border:none;background:rgba(255,255,255,0.08);color:var(--text-primary);cursor:pointer;font-size:1.2rem;"><svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
        </div>
        <div style="padding:20px 28px;">
          <div v-for="(season, si) in farmingCalendar" :key="season.season"
            :style="`margin-bottom:${si<farmingCalendar.length-1?'20px':'0'};`">
            <div :style="`display:flex;align-items:center;gap:10px;margin-bottom:12px;`">
              <span :style="`padding:4px 14px;border-radius:20px;font-weight:700;font-size:0.85rem;
                ${season.season==='冬季'?'background:rgba(33,150,243,0.2);color:#64b5f6;':
                  season.season==='春季'?'background:rgba(76,175,80,0.2);color:#81c784;':
                  season.season==='夏季'?'background:rgba(255,152,0,0.2);color:#ffb74d;':
                  'background:rgba(156,39,176,0.2);color:#ce93d8;'}`">
                {{ season.season }}
              </span>
              <span style="font-size:0.78rem;color:var(--text-tertiary);">{{ season.months }}</span>
            </div>
            <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px;">
              <div v-for="task in season.tasks" :key="task.title"
                style="padding:14px;background:rgba(255,255,255,0.03);border-radius:12px;border:1px solid rgba(255,255,255,0.05);">
                <h4 style="font-weight:700;font-size:0.85rem;margin-bottom:6px;">{{ task.title }}</h4>
                <p style="font-size:0.76rem;color:var(--text-secondary);line-height:1.5;">{{ task.desc }}</p>
                <span style="display:inline-block;margin-top:8px;padding:2px 8px;border-radius:6px;font-size:0.65rem;background:rgba(255,255,255,0.05);color:var(--text-muted);">{{ task.crops }}</span>
              </div>
            </div>
          </div>
          <p style="margin-top:20px;font-size:0.7rem;color:var(--text-muted);text-align:center;">以上农事活动因地区和年份气候差异，具体时间可能有所不同，请结合实际调整</p>
        </div>
      </div>
    </div>

    <!-- 防治方案 Panel -->
    <div v-if="showTreatmentPlans" class="modal-overlay" @click.self="closeTreatmentPlans">
      <div class="modal-content animate-scale-in" style="max-width:820px;max-height:85vh;overflow-y:auto;">
        <div style="padding:20px 28px;border-bottom:1px solid rgba(255,255,255,0.06);display:flex;justify-content:space-between;align-items:center;">
          <div>
            <h2 style="font-weight:700;font-size:1.15rem;display:flex;align-items:center;gap:8px;"><svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M9 3h6M10 3v4.5L6 19.1A2 2 0 007.8 22h8.4a2 2 0 001.8-2.9L14 7.5V3"/></svg>防治方案汇总</h2>
            <p style="font-size:0.75rem;color:var(--text-tertiary);">覆盖 {{ treatmentPlans.length }} 类作物 · 共 {{ allArticles.length }} 种病害的完整防治方案</p>
          </div>
          <button @click="closeTreatmentPlans" style="padding:6px;border-radius:8px;border:none;background:rgba(255,255,255,0.08);color:var(--text-primary);cursor:pointer;font-size:1.2rem;"><svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
        </div>
        <div style="padding:20px 28px;">
          <div v-for="(group, gi) in treatmentPlans" :key="group.crop"
            :style="`margin-bottom:${gi<treatmentPlans.length-1?'24px':'0'};`">
            <h3 style="font-weight:700;font-size:1rem;margin-bottom:12px;display:flex;align-items:center;gap:8px;">
              <span style="display:flex;align-items:center;">
                <svg v-if="group.icon === 'tomato'" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 3v3M12 18v3"/></svg>
                <svg v-else-if="group.icon === 'cucumber'" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><ellipse cx="12" cy="12" rx="6" ry="10"/></svg>
                <svg v-else-if="group.icon === 'pepper'" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 2c-3 0-7 3-7 9s4 11 7 11 7-5 7-11-4-9-7-9z"/></svg>
                <svg v-else-if="group.icon === 'potato'" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><ellipse cx="12" cy="12" rx="8" ry="6"/></svg>
                <svg v-else-if="group.icon === 'wheat'" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 2v20M8 6c0 0 4-2 4-4 0 2 4 4 4 4"/><path d="M8 10c0 0 4-2 4-4 0 2 4 4 4 4"/><path d="M8 14c0 0 4-2 4-4 0 2 4 4 4 4"/></svg>
                <svg v-else width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5z"/></svg>
              </span>
              {{ group.crop }}
              <span style="font-weight:400;font-size:0.72rem;color:var(--text-muted);">({{ group.count }} 种病害)</span>
            </h3>
            <div v-for="a in group.articles" :key="a.id"
              style="padding:14px 16px;background:rgba(255,255,255,0.03);border-radius:12px;margin-bottom:8px;border:1px solid rgba(255,255,255,0.04);">
              <div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:8px;">
                <h4 style="font-weight:700;font-size:0.88rem;"><svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="vertical-align:middle;margin-right:4px;"><circle cx="12" cy="12" r="8"/><path d="M8 12h8M12 8v8"/></svg>{{ a.disease }}</h4>
                <span style="font-size:0.65rem;color:var(--text-muted);">{{ a.views }} 读</span>
              </div>
              <div style="padding:10px 14px;background:rgba(76,175,80,0.06);border-radius:10px;border-left:3px solid var(--color-accent);">
                <span style="font-size:0.7rem;font-weight:700;color:var(--color-accent);"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="vertical-align:middle;margin-right:6px;"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>治疗方案：</span>
                <span style="font-size:0.78rem;color:var(--text-secondary);line-height:1.6;">{{ a.treatment }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 提问弹窗 -->
    <div v-if="showQuestionModal" class="modal-overlay" @click.self="closeQuestionModal">
      <div class="modal-content animate-scale-in" style="max-width:480px;">
        <div style="padding:20px 28px;border-bottom:1px solid rgba(255,255,255,0.06);display:flex;justify-content:space-between;align-items:center;">
          <h2 style="font-weight:700;font-size:1.1rem;"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="vertical-align:middle;margin-right:6px;"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>发布问题</h2>
          <button @click="closeQuestionModal" style="padding:6px;border-radius:8px;border:none;background:rgba(255,255,255,0.08);color:var(--text-primary);cursor:pointer;font-size:1.2rem;"><svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
        </div>
        <div style="padding:24px 28px;" class="space-y-4">
          <div>
            <label style="display:block;font-size:0.8rem;font-weight:600;margin-bottom:6px;color:var(--text-primary);">昵称</label>
            <input
              v-model="newQuestion.username"
              type="text"
              placeholder="请输入您的昵称"
              class="form-input"
              maxlength="20"
            />
          </div>
          <div>
            <label style="display:block;font-size:0.8rem;font-weight:600;margin-bottom:6px;color:var(--text-primary);">问题描述</label>
            <textarea
              v-model="newQuestion.content"
              placeholder="请详细描述您遇到的病虫害问题..."
              class="form-input"
              rows="4"
              maxlength="500"
              style="resize:vertical;"
            ></textarea>
            <span style="font-size:0.68rem;color:var(--text-muted);float:right;margin-top:4px;">{{ newQuestion.content.length }}/500</span>
          </div>
          <div style="display:flex;gap:10px;justify-content:flex-end;">
            <button class="btn btn-outline btn-sm" @click="closeQuestionModal">取消</button>
            <button class="btn btn-primary btn-sm" @click="submitQuestion"
              :disabled="!newQuestion.username.trim() || !newQuestion.content.trim()">
              发布问题
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ── Category Cards Override ── */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 10px;
  margin-bottom: 20px;
}

.stats-grid .stat-card {
  padding: 12px !important;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 6px;
}

.stats-grid .stat-card .stat-icon {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  margin-bottom: 0;
  flex-shrink: 0;
}

.stats-grid .stat-card .stat-value {
  font-size: 0.9rem !important;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.2;
  margin-bottom: 0;
}

.stats-grid .stat-card .stat-label {
  font-size: 0.7rem;
  color: var(--text-secondary);
  margin-top: 0;
}

@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }
}
</style>