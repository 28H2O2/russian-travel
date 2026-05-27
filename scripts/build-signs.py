#!/usr/bin/env python3
"""
功能：将 _staging 候选图按手工选择转 webp + 移到正式目录 + 写 signs.json
输入：
    public/signs/_staging/_manifest.json
    本脚本内嵌的 SELECTIONS 列表（人工挑选结果）
输出：
    public/signs/<category>/<id>.webp
    src/data/signs.json
如何运行：
    python3 scripts/build-signs.py
依赖：cwebp（系统）, requests（python）
在项目中的作用：路牌识字 feature 的内容生产 Pipeline 阶段 2/3。
    把从 Wikimedia 抓回来的候选图固化为 v1 的 30 张正式 sign 卡片。
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STAGING_DIR = PROJECT_ROOT / "scripts" / ".signs-staging"
SIGNS_DIR = PROJECT_ROOT / "public" / "signs"
DATA_PATH = PROJECT_ROOT / "src" / "data" / "signs.json"

WEBP_QUALITY = 78           # 视觉/体积折中
WEBP_MAX_WIDTH = 960        # 卡片宽度 + retina 余量


# ---------------------------------------------------------------------
# 手工挑选结果：(category, id, 源 staging 路径，从 manifest.local_path)
# ---------------------------------------------------------------------
SELECTIONS: list[dict] = [
    # ========= AIRPORT (5) =========
    {
        "id": "airport.tashkent_facade_night",
        "category": "airport",
        "src_rel": "scripts/.signs-staging/airport/tashkent_international_airport/img_08.jpg",
        "ru": None,
        "ru_translit": None,
        "uz_latin": "TOSHKENT XALQARO AEROPORTI",
        "uz_cyrillic": "ТОШКЕНТ ХАЛҚАРО АЭРОПОРТИ",
        "chinese": "塔什干国际机场",
        "literal": "Toshkent（塔什干）+ xalqaro（国际）+ aeroporti（机场）",
        "context": "落地塔什干第一眼就是这个蓝色大字招牌。注意它写的是乌兹别克语（不是俄语），用的是西里尔字母——因为这是老一辈仍然认得的拼法。",
        "local_note": "塔什干岛尔米尔机场 (TAS) 入夜后这个招牌会发蓝光，从远处就能认出。乌兹别克语 xalqaro = 国际，对应俄语 международный。",
    },
    {
        "id": "airport.tashkent_apron_uzbekistan_airways",
        "category": "airport",
        "src_rel": "scripts/.signs-staging/airport/tashkent_international_airport/img_07.jpg",
        "ru": None,
        "ru_translit": None,
        "uz_latin": "TASHKENT",
        "uz_cyrillic": None,
        "chinese": "塔什干（拉丁拼写）+ 乌兹别克斯坦航空（机尾）",
        "literal": "TASHKENT = 塔什干；蓝色尾翼的鸟徽 = Uzbekistan Airways",
        "context": "停机坪视角的塔什干机场。屋顶 TASHKENT 是英文拼法（机场对国际旅客的标识），停的飞机是 Uzbekistan Airways（HY 航班代码）。",
        "local_note": "TAS 主要承运国是 Uzbekistan Airways。机场代码 TAS 来自俄语/乌兹别克语 ТАшкент 的前三字母。",
    },
    {
        "id": "airport.tashkent_terminal_interior",
        "category": "airport",
        "src_rel": "scripts/.signs-staging/airport/tashkent_international_airport/img_01.jpg",
        "ru": None,
        "ru_translit": None,
        "uz_latin": None,
        "uz_cyrillic": None,
        "chinese": "塔什干机场候机区内景",
        "literal": "—",
        "context": "登机区典型场景。窗外可以看到 Uzbekistan Airways（绿色尾翼）和俄罗斯/独联体国家来的航班。",
        "local_note": "塔什干机场内的指示牌基本三语：UZ Latin / UZ Cyrillic / English，部分还有俄语。买东西、问路、过安检——比想象的好走。",
    },
    {
        "id": "airport.moscow_sheremetyevo_vintage",
        "category": "airport",
        "src_rel": "scripts/.signs-staging/airport/airport_sign_cyrillic_russian/img_01.jpg",
        "ru": "МОСКВА ШЕРЕМЕТЬЕВО",
        "ru_translit": "MAS-kva  she-re-MYE-tye-va",
        "uz_latin": None,
        "uz_cyrillic": None,
        "chinese": "莫斯科 谢列梅捷沃（机场）",
        "literal": "МОСКВА = 莫斯科，ШЕРЕМЕТЬЕВО = 机场名（地名）",
        "context": "经典苏联时期的莫斯科 SVO 机场招牌。如果你从塔什干转莫斯科，这种字体的航站楼牌是会看到的标志性 motif。",
        "local_note": "Шереметьево（SVO）和 Домодедово（DME）是莫斯科两大机场。塔什干很多航线 transit MOW——会用到。",
    },
    {
        "id": "airport.tashkent_control_tower",
        "category": "airport",
        "src_rel": "scripts/.signs-staging/airport/tashkent_international_airport/img_06.jpg",
        "ru": None,
        "ru_translit": None,
        "uz_latin": None,
        "uz_cyrillic": None,
        "chinese": "塔什干机场停机坪与塔台",
        "literal": "—",
        "context": "停机坪视角，远处是 TAS 的塔台。停的飞机大概率是 Uzbekistan Airways（蓝白涂装）。",
        "local_note": "TAS 是中亚最大机场之一。从塔什干到费尔干纳、撒马尔罕、努库斯都有内陆航班——便宜，比火车快。",
    },

    # ========= STREET (7) =========
    {
        "id": "street.navoiy_kochasi",
        "category": "street",
        "src_rel": "scripts/.signs-staging/street/tashkent_street_sign/img_01.jpg",
        "ru": None,
        "ru_translit": None,
        "uz_latin": "NAVOIY KO'CHASI",
        "uz_cyrillic": "НАВОИЙ КЎЧАСИ",
        "chinese": "纳沃伊街",
        "literal": "Navoiy（人名 · 15 世纪诗人）+ ko'chasi（街）",
        "context": "塔什干典型的蓝色搪瓷路牌。所有主街都会有这种白字蓝底的牌子，挂在十字路口的灯柱上。",
        "local_note": "Alisher Navoiy 是乌兹别克民族诗圣，每个城市都有 Navoiy 街/广场/地铁站。看到这名字 = 在主干道附近。ko'chasi 等于俄语的 улица（街）。",
    },
    {
        "id": "street.mustaqillik_bekati",
        "category": "street",
        "src_rel": "scripts/.signs-staging/street/tashkent_metro_entrance/img_01.jpg",
        "ru": None,
        "ru_translit": None,
        "uz_latin": "MUSTAQILLIK MAYDONI BEKATI",
        "uz_cyrillic": "МУСТАКИЛЛИК МАЙДОНИ БЕКАТИ",
        "chinese": "独立广场地铁站",
        "literal": "Mustaqillik（独立）+ maydoni（广场）+ bekati（站）",
        "context": "塔什干地铁站入口外墙。这是塔什干市中心最重要的站之一，邻近 Hilton、各国大使馆和 Tashkent City 综合体。",
        "local_note": "看到 БЕКАТИ / BEKATI 三个字基本就是地铁站。MAYDON / МАЙДОН = 广场，约等于俄语的 площадь。",
    },
    {
        "id": "street.metro_navigation_panel",
        "category": "street",
        "src_rel": "scripts/.signs-staging/street/tashkent_metro_station/img_07.jpg",
        "ru": None,
        "ru_translit": None,
        "uz_latin": "Chiqish",
        "uz_cyrillic": "Чиқиш · Выход · Exit",
        "chinese": "出口 / 站内导向图（三语：乌拉丁、乌西里尔/俄、英）",
        "literal": "Chiqish（UZ）= Выход（RU）= Exit（EN）",
        "context": "2024 年更新过的塔什干地铁站内导向图。每个出口对应不同地标（如 Tashkent City Mall, Hilton, Конserваtoria）。",
        "local_note": "塔什干地铁内部导向是三语同框，对外国人友好——选 EXIT 4-5 通往 Tashkent City Mall, 选 EXIT 3 通往 Paxtakor 体育场。",
    },
    {
        "id": "street.alisher_navoiy_station_platform",
        "category": "street",
        "src_rel": "scripts/.signs-staging/street/tashkent_metro_station/img_02.jpg",
        "ru": None,
        "ru_translit": None,
        "uz_latin": None,
        "uz_cyrillic": None,
        "chinese": "塔什干地铁 Alisher Navoiy 站内景",
        "literal": "—",
        "context": "全球最美地铁站之一。穹顶是仿撒马尔罕清真寺的几何装饰。蓝白涂装的列车上印着乌兹别克国旗色。",
        "local_note": "Alisher Navoiy 站位于 O'zbekiston 线，是市中心枢纽。车厢号 4022 这种 4 位数从苏联时期沿用至今。",
    },
    {
        "id": "street.bilingual_cyrillic_latin",
        "category": "street",
        "src_rel": "scripts/.signs-staging/street/cyrillic_street_sign_russian/img_05.jpg",
        "ru": "Мостар",
        "ru_translit": "MOS-tar",
        "uz_latin": "Mostar",
        "uz_cyrillic": None,
        "chinese": "城市名「Mostar/Мостар」拉丁 + 西里尔双语标识",
        "literal": "同一个地名 · 两种字母拼出来一样的发音",
        "context": "波黑 Mostar 入城牌。虽然不是 UZ，但这种「拉丁 + 西里尔同框」正是塔什干招牌的常态——同一个词用两套字母排版。",
        "local_note": "练习窍门：看到双语牌就用心比对——拉丁的 sh = 西里尔的 ш，gʻ = ғ，oʻ = ў。习惯了在塔什干认招牌速度会快 3 倍。",
    },
    {
        "id": "street.tashkent_loves_you",
        "category": "street",
        "src_rel": "scripts/.signs-staging/street/tashkent_street_sign/img_07.jpg",
        "ru": None,
        "ru_translit": None,
        "uz_latin": "TASHKENT ❤ YOU",
        "uz_cyrillic": None,
        "chinese": "塔什干爱你（城市营销标识）",
        "literal": "城市 + 心 + 你",
        "context": "塔什干网红地标之一，类似 I♥NY。一般在 Furkat 街附近，正对着 KFC 和 Hilton。",
        "local_note": "拍照打卡点。但你会注意到：连官方文旅标都用英文 + UZ 拉丁，不再用西里尔。城市旅游业全面拉丁化是 2020 年后的事。",
    },
    {
        "id": "street.metro_platform_chilanzar",
        "category": "street",
        "src_rel": "scripts/.signs-staging/street/tashkent_metro_station/img_03.jpg",
        "ru": None,
        "ru_translit": None,
        "uz_latin": None,
        "uz_cyrillic": None,
        "chinese": "塔什干地铁 Chilanzar 线某站台",
        "literal": "—",
        "context": "塔什干地铁 3 条线：Chilanzar（红）、O'zbekiston（蓝）、Yunusabad（绿）。蓝白列车是 Chilanzar 线的标志色。",
        "local_note": "票价 1400-1700 sum 一程（约 1 元人民币），地铁站内通常允许拍照但不能拍设施细节——2018 年前完全禁止拍照。",
    },

    # ========= MARKET (6) =========
    {
        "id": "market.chorsu_meat_dome",
        "category": "market",
        "src_rel": "scripts/.signs-staging/market/chorsu_bazaar_tashkent/img_01.jpg",
        "ru": None,
        "ru_translit": None,
        "uz_latin": None,
        "uz_cyrillic": None,
        "chinese": "Chorsu 巴扎肉类大堂",
        "literal": "—",
        "context": "Chorsu 巴扎的标志性蓝色穹顶下，是塔什干最大的肉类集市。摊位前的小数字牌就是摊位编号（用来在巴扎里找路）。",
        "local_note": "Chorsu = 古波斯语「四条路口」。这里是塔什干老城心脏，从地铁 Chorsu 站出来步行 2 分钟。卖肉的几乎都是男性，按公斤报价。",
    },
    {
        "id": "market.chorsu_vegetable_1969",
        "category": "market",
        "src_rel": "scripts/.signs-staging/market/chorsu_bazaar_tashkent/img_06.jpg",
        "ru": None,
        "ru_translit": None,
        "uz_latin": "1969",
        "uz_cyrillic": None,
        "chinese": "蔬菜摊 + 摊位号「1969」",
        "literal": "1969 = 摊位编号",
        "context": "Chorsu 巴扎蔬菜区。每个摊位下方都有这种白底蓝字的摊位号，由市场管委会编号。",
        "local_note": "如果跟朋友约「在 Chorsu 见」，发摊位号是最准确的找人方式（巴扎有几百米深）。萝卜 / 香菜 / 葱蒜是中亚日常主菜。",
    },
    {
        "id": "market.chorsu_onion_rastasi",
        "category": "market",
        "src_rel": "scripts/.signs-staging/market/chorsu_bazaar_tashkent/img_07.jpg",
        "ru": None,
        "ru_translit": None,
        "uz_latin": "RASTASI",
        "uz_cyrillic": None,
        "chinese": "（蔬果）排队卖摊位",
        "literal": "Rastasi = 一排/一列卖摊位（巴扎术语）",
        "context": "Chorsu 巴扎洋葱大蒜区。顶部红色横幅 RASTASI 是「（某品类）排区」的意思。1358 / 1359 是相邻两个摊位号。",
        "local_note": "rasta（拉丁）/ раста（西里尔）= 同一品类的整片销售区。问路时说「Piyoz rastasi qayerda?」（洋葱区在哪？），比说品名清楚。",
    },
    {
        "id": "market.chorsu_navat_candy",
        "category": "market",
        "src_rel": "scripts/.signs-staging/market/chorsu_bazaar_tashkent/img_05.jpg",
        "ru": None,
        "ru_translit": None,
        "uz_latin": "Navat",
        "uz_cyrillic": "Наво́т",
        "chinese": "巴扎甜品摊：纳瓦特（结晶蔗糖）",
        "literal": "Navat = 蔗糖结晶块（突厥-波斯传统甜品）",
        "context": "Chorsu 巴扎的甜食/干果区。前景是琥珀色透明的结晶糖（Navat / нават），是泡茶的伴侣，给客人 / 病人 / 老人吃的。",
        "local_note": "买 navat 要挑大块通透、咬一口脆响的。塔什干本地价 30-40k sum/kg。中亚人喝茶不放白糖、只放 navat。",
    },
    {
        "id": "market.chorsu_ceramics_suzani",
        "category": "market",
        "src_rel": "scripts/.signs-staging/market/chorsu_bazaar_tashkent/img_02.jpg",
        "ru": None,
        "ru_translit": None,
        "uz_latin": None,
        "uz_cyrillic": None,
        "chinese": "巴扎陶瓷与苏扎尼摊位",
        "literal": "—",
        "context": "Chorsu 巴扎工艺品区。陶盘上的几何/植物纹是 Rishton（费尔干纳）出产的传统瓷。背景挂的布是苏扎尼（suzani）刺绣。",
        "local_note": "纪念品三件套：Rishton 陶盘、Bukhara 银饰、Samarkand 纸。这里价比博物馆店便宜 40-60%，但要会 mol bozor（议价）。",
    },
    {
        "id": "market.talitskoye_moloko_aprel",
        "category": "market",
        "src_rel": "scripts/.signs-staging/public/pharmacy_sign_russia/img_07.jpg",
        "ru": "Талицкое молоко · АПТЕКА АПРЕЛЬ",
        "ru_translit": "TA-li-tska-ye ma-la-KO · ap-TYE-ka ap-RYEL",
        "uz_latin": None,
        "uz_cyrillic": None,
        "chinese": "Талицкое 牛奶店 + 「四月」连锁药店",
        "literal": "Талицкое = 品牌名（地名形容词）, молоко = 牛奶, АПРЕЛЬ = 四月",
        "context": "俄罗斯/独联体街角双店：右边蓝色是奶制品店（Талицкое 是俄罗斯本土乳品品牌），左边绿色是连锁药店 Аптека Апрель。",
        "local_note": "молоко（milk）/ хлеб（bread）/ мясо（meat）这种基础店招要一眼认。塔什干的小区角落也有类似复合店——奶+药+小卖部三合一。",
    },

    # ========= RESTAURANT (6) =========
    {
        "id": "restaurant.business_lunch_menu",
        "category": "restaurant",
        "src_rel": "scripts/.signs-staging/restaurant/russian_restaurant_menu_sign/img_01.jpg",
        "ru": "БИЗНЕС - ЛАНЧ с 12.00 до 17.00",
        "ru_translit": "BIZ-nes  LANCH  s  dva-NA-tsa-ti  da  syem-NA-tsa-ti",
        "uz_latin": None,
        "uz_cyrillic": None,
        "chinese": "工作餐午市菜单（12:00-17:00 供应）",
        "literal": "Бизнес-ланч = business lunch；с ... до ... = 从 ... 到 ...",
        "context": "俄罗斯 / 独联体餐厅常见的午餐菜单结构。「Холодные закуски」= 冷盘；「Супы」= 汤；「Горячие блюда」= 热菜；「Гарнир」= 主食/配菜。",
        "local_note": "塔什干很多餐厅都有 бизнес-ланч 套餐，约 25-40k sum 三道菜，比单点便宜一半。卡片里出现的几个菜：салат / суп-лапша / шашлык 都是中亚常见。",
    },
    {
        "id": "restaurant.crystal_garden_hotel",
        "category": "restaurant",
        "src_rel": "scripts/.signs-staging/restaurant/tashkent_restaurant/img_03.jpg",
        "ru": None,
        "ru_translit": None,
        "uz_latin": "Crystal Garden",
        "uz_cyrillic": None,
        "chinese": "Crystal Garden 餐厅（City Palace 酒店内）",
        "literal": "—",
        "context": "塔什干 Amir Temur 大道上的高端餐厅。塔什干新酒店区，餐厅命名几乎全部直接用英文/拉丁——目标客户是涉外。",
        "local_note": "Amir Temur Shoh Ko'chasi 是塔什干主商业街，看到拉丁招牌占多数 = 进入了高端涉外区。本地小店多在背街，认招牌更需要 UZ Cyrillic 功底。",
    },
    {
        "id": "restaurant.azerbaijani_cuisine",
        "category": "restaurant",
        "src_rel": "scripts/.signs-staging/restaurant/tashkent_restaurant/img_05.jpg",
        "ru": None,
        "ru_translit": None,
        "uz_latin": "Azerbaijani cuisine",
        "uz_cyrillic": None,
        "chinese": "阿塞拜疆菜餐厅",
        "literal": "国名 + cuisine（菜系）",
        "context": "塔什干常见的「他国菜系」餐厅。门口插的是阿塞拜疆国旗 + 乌兹别克斯坦国旗。",
        "local_note": "塔什干吃饭多元：阿塞拜疆 / 格鲁吉亚 / 鞑靼 / 韩国（Koryo-saram）/ 维吾尔菜都有专门馆子。看见外国国旗 = 这家是异国菜。",
    },
    {
        "id": "restaurant.deyfendi_kebab_house",
        "category": "restaurant",
        "src_rel": "scripts/.signs-staging/restaurant/tashkent_restaurant/img_06.jpg",
        "ru": None,
        "ru_translit": None,
        "uz_latin": "BEYEFENDI",
        "uz_cyrillic": None,
        "chinese": "Beyefendi 烤肉店（土耳其风格连锁）",
        "literal": "Beyefendi（土耳其语：先生 / sir）",
        "context": "塔什干热门土耳其连锁烤肉店。门窗内是 LED 菜单：lamb chop / lamb sho'rva / meatball with cheese 等英文菜名。",
        "local_note": "土耳其菜在塔什干极流行——同源突厥文化、味道也接近本地 shashlik。Beyefendi / Edoy / Bahor 三大连锁都不错。",
    },
    {
        "id": "restaurant.central_asian_plov_centre",
        "category": "restaurant",
        "src_rel": "scripts/.signs-staging/restaurant/tashkent_restaurant/img_07.jpg",
        "ru": None,
        "ru_translit": None,
        "uz_latin": "Central Asian Plov Centre",
        "uz_cyrillic": None,
        "chinese": "中亚抓饭中心（塔什干 plov 圣地）",
        "literal": "Plov = 抓饭（乌兹别克国菜）",
        "context": "Yunusabad 区的中亚抓饭中心，每天上午 11:00-14:00 开门，卖完即止。师傅当场从巨型大锅 (kazan) 给你盛 plov。",
        "local_note": "塔什干吃 plov 必须中午去——下午 1-2 点最热闹也最新鲜。本地价 20-30k sum 一份。点单只说「plov bir»（plov 一份），不用菜单。",
    },
    {
        "id": "restaurant.chaikhana_doppa_elder",
        "category": "restaurant",
        "src_rel": "scripts/.signs-staging/restaurant/uzbek_chaikhana/img_02.jpg",
        "ru": None,
        "ru_translit": None,
        "uz_latin": "choyxona",
        "uz_cyrillic": "чойхона",
        "chinese": "茶馆内的老者（典型乌兹别克穿戴）",
        "literal": "choy（茶）+ xona（屋）= 茶屋",
        "context": "茶馆（choyxona / chaikhana）的典型场景：老者戴 doppa（黑白方帽）穿 chapan（长袍）。这种地方是「准餐厅」——主要喝茶、配 plov 或 shashlik。",
        "local_note": "茶馆没有招牌也能认：白墙、雕花门、户外有炕床的「topchan」（围坐喝茶的木台子）就是。男性社交场所，女性可以进但不常去。",
    },

    # ========= PUBLIC (6) =========
    {
        "id": "public.brighton_beach_central_pharmacy",
        "category": "public",
        "src_rel": "scripts/.signs-staging/public/pharmacy_sign_russia/img_06.jpg",
        "ru": "Центральная Аптека",
        "ru_translit": "tsen-TRAL-na-ya  ap-TYE-ka",
        "uz_latin": None,
        "uz_cyrillic": None,
        "chinese": "中心药店",
        "literal": "Центральная（中央的）+ Аптека（药店）",
        "context": "纽约布鲁克林 Brighton Beach 俄罗斯人聚居区的连锁药店。Аптека 字体是俄/独联体药店通用的「白衬线大写」。",
        "local_note": "在塔什干认 Аптека 这个词最重要——五金店 / 药店 / 杂货店外观相似，唯有「АПТЕКА」+ 绿色十字是药店标识。乌兹别克语拉丁拼写也是 Apteka。",
    },
    {
        "id": "public.veterinary_pharmacy_neon",
        "category": "public",
        "src_rel": "scripts/.signs-staging/public/pharmacy_sign_russia/img_08.jpg",
        "ru": "Ветеринарная Аптека",
        "ru_translit": "vye-tye-ri-NAR-na-ya  ap-TYE-ka",
        "uz_latin": None,
        "uz_cyrillic": None,
        "chinese": "兽医药店（兽用药房）",
        "literal": "Ветеринарная = 兽医的 + Аптека = 药店；招牌两侧蓝猫、红狗霓虹",
        "context": "西伯利亚 Novosibirsk 的兽医药店。如果你 / 同伴带宠物去 UZ 旅行，看到这种招牌就是宠物药店。开门时间「10-21」= 10:00-21:00。",
        "local_note": "在 UZ 兽医药店没俄罗斯这么常见，但塔什干 Yunusabad、Mirzo Ulug'bek 区都有。带宠物入境 UZ 需提前 14 天兽医证 + 微芯片。",
    },
    {
        "id": "public.finnish_russian_border_pharmacy",
        "category": "public",
        "src_rel": "scripts/.signs-staging/public/pharmacy_sign_russia/img_04.jpg",
        "ru": "АПТЕКА",
        "ru_translit": "ap-TYE-ka",
        "uz_latin": None,
        "uz_cyrillic": None,
        "chinese": "药店（同时显示芬兰语 APTEEKKI）",
        "literal": "АПТЕКА（俄语）= APTEEKKI（芬兰语，注意双 E、双 K）",
        "context": "俄罗斯-芬兰 Torfyanovka 关口的药店。窗户上同时贴俄语「АПТЕКА」和芬兰语「APTEEKKI」——便利两国旅客。",
        "local_note": "认 АПТЕКА 的窍门：俄语和乌兹别克语拉丁拼写都是这个词，跨整个独联体 + 巴尔干都通用。绿色十字 + 这五个字母 = 100% 是药店。",
    },
    {
        "id": "public.village_pharmacy_deer",
        "category": "public",
        "src_rel": "scripts/.signs-staging/public/pharmacy_sign_russia/img_01.jpg",
        "ru": "АПТЕКА",
        "ru_translit": "ap-TYE-ka",
        "uz_latin": None,
        "uz_cyrillic": None,
        "chinese": "村镇药店（乌克兰乡村风格）",
        "literal": "АПТЕКА = 药店",
        "context": "乌克兰 Voronkivtsi 村的小镇药店。竖排红字 АПТЕКА 是苏联沿用至今的最简招牌设计：木门、油漆铁字、两侧鹿雕。",
        "local_note": "如果你去塔什干周边小镇（Chimgan, Khiva 老城外），药店都长这样：低调、字立排在门旁。营业时间常被手写贴纸覆盖在玻璃上。",
    },
    {
        "id": "public.modern_chain_zhivika",
        "category": "public",
        "src_rel": "scripts/.signs-staging/public/pharmacy_sign_russia/img_03.jpg",
        "ru": "Аптека  ·  Аптеки Живика",
        "ru_translit": "ap-TYE-ka  ·  ap-TYE-ki  zhi-VI-ka",
        "uz_latin": None,
        "uz_cyrillic": None,
        "chinese": "现代连锁药店（俄罗斯 Тюмень·Живика 品牌）",
        "literal": "Аптеки = 复数形式（多家分店）; Живика = 品牌名（直译「活泉」）",
        "context": "西伯利亚 Tyumen 的连锁药店店面。这是 UZ 之外的俄罗斯连锁招牌，但你在塔什干会看到几乎一模一样的设计：绿底白字 + 十字 + 二维码。",
        "local_note": "塔什干本地连锁药店是 \"Apteka.uz\"、\"Doridarmon\"、\"NEO\"。招牌风格雷同，认绿色十字最快——夜晚也亮。",
    },
    {
        "id": "public.rural_apteka_117",
        "category": "public",
        "src_rel": "scripts/.signs-staging/public/pharmacy_sign_russia/img_02.jpg",
        "ru": "АПТЕКА № 117",
        "ru_translit": "ap-TYE-ka  NO-mer  sto sem-NA-tsat",
        "uz_latin": None,
        "uz_cyrillic": None,
        "chinese": "117 号药店",
        "literal": "АПТЕКА + №（编号）+ 117",
        "context": "俄罗斯西伯利亚乡村药店。蓝色木屋 + 木栅栏 + 牌匾，是苏联国营药店分布编号系统的遗存。",
        "local_note": "在塔什干你不会看到 № 这种编号药店（已民营化）。但「№」（俄语「编号」缩写）= 乌兹别克语拉丁「№」/ 西里尔「№」，所有公文还在用。",
    },
]


def cwebp_convert(src: Path, dst: Path) -> bool:
    """调用 cwebp 转码"""
    dst.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "cwebp",
        "-q", str(WEBP_QUALITY),
        "-resize", str(WEBP_MAX_WIDTH), "0",   # 宽 960、高自动等比
        "-quiet",
        str(src),
        "-o", str(dst),
    ]
    res = subprocess.run(cmd, capture_output=True)
    if res.returncode != 0:
        print(f"  ! cwebp failed for {src.name}: {res.stderr.decode()}")
        return False
    return True


def main() -> int:
    if not STAGING_DIR.exists():
        print(f"!! staging dir not found: {STAGING_DIR}")
        return 1

    with open(STAGING_DIR / "_manifest.json", "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # 把 manifest 平铺成 by-local_path 索引
    by_path: dict[str, dict] = {}
    for cat, entries in manifest.items():
        for e in entries:
            by_path[e["local_path"]] = e

    signs_json: list[dict] = []
    converted = 0

    print(f"Processing {len(SELECTIONS)} selected images...")
    for sel in SELECTIONS:
        src_rel = sel["src_rel"]
        entry = by_path.get(src_rel)
        if not entry:
            print(f"  !! missing in manifest: {src_rel}")
            continue
        src = PROJECT_ROOT / src_rel
        if not src.exists():
            print(f"  !! file not found on disk: {src}")
            continue

        dst = SIGNS_DIR / sel["category"] / f"{sel['id'].split('.', 1)[1]}.webp"
        if not cwebp_convert(src, dst):
            continue

        # attribution from manifest
        author = entry.get("artist", "") or entry.get("credit", "") or "Wikimedia contributor"
        license_short = entry.get("license", "Unknown")
        source_url = entry.get("source_url", "")

        # alt 用中文短描述
        alt = f"{sel['chinese']}（{sel['category']}）"

        sign = {
            "id": sel["id"],
            "category": sel["category"],
            "image": {
                "src": f"/signs/{sel['category']}/{dst.name}",
                "alt": alt,
                "attribution": {
                    "author": author[:80],
                    "source_url": source_url,
                    "license": license_short,
                    "via": "Wikimedia Commons",
                },
            },
            "chinese": sel["chinese"],
            "context": sel["context"],
        }
        # 可选字段（None 不输出）
        for k in ("ru", "ru_translit", "uz_latin", "uz_cyrillic", "literal", "local_note"):
            v = sel.get(k)
            if v:
                sign[k] = v

        signs_json.append(sign)
        converted += 1
        print(f"  [{converted:2d}] {sel['id']:50s} → {dst.relative_to(PROJECT_ROOT)}")

    # 写 signs.json
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(signs_json, f, ensure_ascii=False, indent=2)

    print()
    print(f"=== Done ===")
    print(f"Converted: {converted}")
    print(f"signs.json: {DATA_PATH.relative_to(PROJECT_ROOT)}")
    by_cat: dict[str, int] = {}
    for s in signs_json:
        by_cat[s["category"]] = by_cat.get(s["category"], 0) + 1
    for cat in ("airport", "street", "market", "restaurant", "public"):
        print(f"  {cat:12s} {by_cat.get(cat, 0)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
