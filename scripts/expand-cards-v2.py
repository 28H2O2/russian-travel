#!/usr/bin/env python3
"""
功能：把 cards.json 从 v1 的 100 张扩到 v2 目标 230 张
     （4 新场景共 100 张 + 3 老场景增量共 30 张）
输入：src/data/cards.json（含 v1 的 100 张）
输出：src/data/cards.json（追加 130 张新卡后覆盖写回）
如何运行：python3 scripts/expand-cards-v2.py
依赖：标准库
在项目中的作用：v2 内容生产的一次性数据源。沿用 v1 的 Python 数据脚本范式——
            脚本即"内容原稿"，便于后续审校追溯。
            脚本是幂等的：再次运行不会重复添加同 id 的卡。

约定（与 v1 一致）：
- id 格式：<scene>.<subcategory>.<short_id>
- 音频文件名：<scene>_NNNN_{normal|slow}.mp3
- transliteration：发音式拉丁化，大写表重音
- verification_status：一律 ai_generated_unreviewed
- likely_responses：通常 1-3 条；独词应答类（数字/方向/付款/堂食打包/烹饪法）可空
- is_essential：不动（v2 不新增必备卡，仍维持 v1 的 10 张）

场景增量分布（130 张）：
- lodging    +25 (新)：入住 4 + 信息询问 5 + 房间问题 8 + 服务请求 4 + checkout 4
- shopping   +30 (新)：进店 3 + 尺码颜色 8 + 试穿 3 + 议价 8 + 付款 4 + 特定 4
- emergency  +20 (新)：求救 4 + 身体 6 + 失物 4 + 联络 3 + 安全 3
- chat       +25 (新)：天气 3 + 寒暄 5 + 关于 UZ 5 + 关于中国 3 + 兴趣 4 + 告别 5
- food       +15：烹饪 4 + 辣度 2 + 当地补 3 + 主食 2 + 饮料 2 + 礼仪 2
- transport  +10：火车 4 + 飞机 3 + 出租进阶 3
- money       +5：整数（两千/五千/两万/五万/百万）
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CARDS_PATH = ROOT / "src" / "data" / "cards.json"


def audio_paths(scene: str, n: int) -> dict[str, str]:
    name = f"{scene}_{n:04d}"
    return {
        "phrase_normal": f"/audio/{scene}/{name}_normal.mp3",
        "phrase_slow": f"/audio/{scene}/{name}_slow.mp3",
    }


def card(
    *,
    id: str,
    scene: str,
    n: int,
    tier: int,
    cyrillic: str,
    transliteration: str,
    chinese: str,
    literal: str,
    politeness: str,
    register_note: str,
    likely_responses: list[dict[str, str]] | None = None,
    slots: list[dict[str, str]] | None = None,
    local_note: str = "",
) -> dict[str, Any]:
    return {
        "id": id,
        "scene": scene,
        "is_essential": False,  # v2 不新增必备卡
        "tier": tier,
        "cyrillic": cyrillic,
        "transliteration": transliteration,
        "chinese": chinese,
        "literal": literal,
        "audio": audio_paths(scene, n),
        "politeness": politeness,
        "register_note": register_note,
        "likely_responses": likely_responses or [],
        "slots": slots or [],
        "local_note": local_note,
        "verification_status": "ai_generated_unreviewed",
    }


# ================================================================
# LODGING — 25 张（n=1-25）
# ================================================================
LODGING = [
    # ---- 入住 (4) ----
    card(
        id="lodging.checkin.reservation", scene="lodging", n=1, tier=1,
        cyrillic="У меня́ брони́рование.", transliteration="u mi-NYA bra-NI-ra-va-ni-ye",
        chinese="我有预订。", literal="在 我 预订",
        politeness="neutral", register_note="进酒店前台第一句",
        likely_responses=[
            {"cyrillic": "Ва́ша фами́лия?", "trans": "VA-sha fa-MI-li-ya", "cn": "您贵姓？"},
            {"cyrillic": "Пока́жите паспорт.", "trans": "pa-KA-zhi-tye PAS-part", "cn": "请出示护照"},
        ],
        local_note="UZ 酒店入住必须出示护照原件——拍照不算。前台会复印 / 拍照。",
    ),
    card(
        id="lodging.checkin.my_name", scene="lodging", n=2, tier=1,
        cyrillic="Моя́ фами́лия Ли.", transliteration="ma-YA fa-MI-li-ya LI",
        chinese="我姓 Li。", literal="我的 姓 Li",
        politeness="neutral", register_note="报姓——在 UZ 报中国姓念准、对方会让你写一遍",
        likely_responses=[
            {"cyrillic": "Минутку, ищу́ вас.", "trans": "mi-NUT-ku i-SHU vas", "cn": "稍等，查一下"},
        ],
        slots=[
            {"label": "请用你的姓替换", "swap": "Моя́ фами́лия Чжан.", "trans": "ma-YA fa-MI-li-ya CHZHAN"},
        ],
    ),
    card(
        id="lodging.checkin.no_reservation", scene="lodging", n=3, tier=2,
        cyrillic="У меня́ нет брони́.", transliteration="u mi-NYA NYET bra-NI",
        chinese="我没有预订。", literal="在 我 没有 预订",
        politeness="neutral", register_note="临时找住的——走进酒店先问有没有空房",
        likely_responses=[
            {"cyrillic": "Есть свобо́дные но́мера.", "trans": "YEST' sva-BOD-ny-ye na-mi-RA", "cn": "有空房"},
            {"cyrillic": "К сожале́нию, всё за́нято.", "trans": "k sa-zha-LYE-ni-yu fsyo ZA-nya-ta", "cn": "抱歉，满了"},
        ],
    ),
    card(
        id="lodging.checkin.tonight_only", scene="lodging", n=4, tier=2,
        cyrillic="Одну́ ночь.", transliteration="ad-NU NOCH'",
        chinese="（住）一晚。", literal="一个 (阴) 夜",
        politeness="neutral", register_note="临时入住时报住几晚",
        likely_responses=[
            {"cyrillic": "То́лько одну́?", "trans": "TOL'-ka ad-NU", "cn": "只一晚？"},
        ],
        slots=[
            {"label": "两晚", "swap": "Две но́чи.", "trans": "DVYE NO-chi"},
            {"label": "三晚", "swap": "Три но́чи.", "trans": "TRI NO-chi"},
            {"label": "一周", "swap": "На неде́лю.", "trans": "na ni-DYE-lyu"},
        ],
    ),
    # ---- 信息询问 (5) ----
    card(
        id="lodging.info.breakfast_included", scene="lodging", n=5, tier=1,
        cyrillic="За́втрак включён?", transliteration="ZAF-trak fklyu-CHON",
        chinese="含早餐吗？", literal="早餐 包含 (短形)",
        politeness="neutral", register_note="决定第二天起多早的关键问题",
        likely_responses=[
            {"cyrillic": "Да, включён.", "trans": "DA fklyu-CHON", "cn": "是的，含"},
            {"cyrillic": "Нет, отдельно 50 ты́сяч.", "trans": "NYET at-DYEL'-na pyat'-di-SYAT TY-syich", "cn": "不含，单点 5 万"},
        ],
        local_note="UZ 大部分中档酒店早餐含——通常是 lepyoshka + 鸡蛋 + 沙拉 + 茶。",
    ),
    card(
        id="lodging.info.breakfast_when", scene="lodging", n=6, tier=2,
        cyrillic="Во ско́лько за́втрак?", transliteration="va SKOL'-ka ZAF-trak",
        chinese="早餐几点？", literal="到 多少 早餐（几点）",
        politeness="neutral", register_note="问早餐供应时间",
        likely_responses=[
            {"cyrillic": "С семи́ до десяти́.", "trans": "s si-MI da di-syi-TI", "cn": "7 点到 10 点"},
        ],
    ),
    card(
        id="lodging.info.wifi_password", scene="lodging", n=7, tier=1,
        cyrillic="Како́й паро́ль от Wi-Fi?", transliteration="ka-KOY pa-ROL' at WAY-FAY",
        chinese="Wi-Fi 密码是什么？", literal="什么样的 密码 来自 Wi-Fi",
        politeness="neutral", register_note="进房前必问",
        likely_responses=[
            {"cyrillic": "Вот здесь напи́сано.", "trans": "VOT ZDYES' na-PI-sa-na", "cn": "写在这里"},
            {"cyrillic": "На карте у двери́.", "trans": "na KAR-tye u dvi-RI", "cn": "门口的卡上"},
        ],
        local_note="UZ 酒店 Wi-Fi 速度一般，外网（YouTube/Google）通常能上，但晚上 8-11 点可能拥堵。",
    ),
    card(
        id="lodging.info.checkout_time", scene="lodging", n=8, tier=2,
        cyrillic="Во ско́лько выселе́ние?", transliteration="va SKOL'-ka vy-si-LYE-ni-ye",
        chinese="几点退房？", literal="到 多少 退房",
        politeness="neutral", register_note="到点不退要加钱",
        likely_responses=[
            {"cyrillic": "До двена́дцати.", "trans": "da dvi-NA-tsa-ti", "cn": "12 点前"},
        ],
    ),
    card(
        id="lodging.info.elevator", scene="lodging", n=9, tier=3,
        cyrillic="Где лифт?", transliteration="GDYE LIFT",
        chinese="电梯在哪？", literal="哪里 电梯",
        politeness="neutral", register_note="找电梯",
        likely_responses=[
            {"cyrillic": "Сле́ва от ресе́пшна.", "trans": "SLYE-va at ri-SEP-shna", "cn": "前台左边"},
        ],
    ),
    # ---- 房间问题 (8) ----
    card(
        id="lodging.problem.ac_broken", scene="lodging", n=10, tier=2,
        cyrillic="Кондиционе́р не рабо́тает.", transliteration="kan-di-tsi-a-NYER ni ra-BO-ta-yit",
        chinese="空调坏了。", literal="空调 不 工作",
        politeness="neutral", register_note="UZ 夏天 35-40 度，空调坏是大事",
        likely_responses=[
            {"cyrillic": "Сейчас при́шлю масте́ра.", "trans": "si-CHAS PRI-shlyu MAS-ti-ra", "cn": "马上派师傅"},
        ],
        local_note="塔什干 7-8 月酷热（白天 40+ 度），下榻前最好亲自测试空调。",
    ),
    card(
        id="lodging.problem.no_hot_water", scene="lodging", n=11, tier=2,
        cyrillic="Нет горя́чей воды́.", transliteration="NYET ga-RYA-chey va-DY",
        chinese="没有热水。", literal="无 热的 水",
        politeness="neutral", register_note="UZ 夏天部分老建筑会定期检修，热水断 1-3 天常见",
        likely_responses=[
            {"cyrillic": "Подожди́те 10 мину́т.", "trans": "pa-dazh-DI-tye DYE-syit' mi-NUT", "cn": "请等 10 分钟"},
            {"cyrillic": "Сейчас прове́рим.", "trans": "si-CHAS pra-VYE-rim", "cn": "马上检查"},
        ],
    ),
    card(
        id="lodging.problem.no_towels", scene="lodging", n=12, tier=2,
        cyrillic="Нет полоте́нец.", transliteration="NYET pa-la-TYE-nits",
        chinese="没有毛巾。", literal="无 毛巾（复数二格）",
        politeness="neutral", register_note="缺布草用品的标准说法",
        likely_responses=[
            {"cyrillic": "Принесём.", "trans": "pri-ni-SYOM", "cn": "我们送来"},
        ],
    ),
    card(
        id="lodging.problem.too_cold", scene="lodging", n=13, tier=3,
        cyrillic="В номере хо́лодно.", transliteration="v NO-mi-rye KHO-lad-na",
        chinese="房间里冷。", literal="在 房间 冷",
        politeness="neutral", register_note="冬天 / 空调开太足时",
        likely_responses=[
            {"cyrillic": "Включу́ обогре́в.", "trans": "fklyu-CHU a-ba-GRYEF", "cn": "我开暖气"},
        ],
    ),
    card(
        id="lodging.problem.too_hot", scene="lodging", n=14, tier=3,
        cyrillic="В номере жа́рко.", transliteration="v NO-mi-rye ZHAR-ka",
        chinese="房间里热。", literal="在 房间 热",
        politeness="neutral", register_note="夏天高频抱怨",
        likely_responses=[
            {"cyrillic": "Включи́те кондиционе́р.", "trans": "fklyu-CHI-tye kan-di-tsi-a-NYER", "cn": "您开下空调"},
        ],
    ),
    card(
        id="lodging.problem.noisy", scene="lodging", n=15, tier=3,
        cyrillic="Сосе́ди о́чень шумя́т.", transliteration="sa-SYE-di O-chen' shu-MYAT",
        chinese="邻居很吵。", literal="邻居 非常 吵闹",
        politeness="neutral", register_note="深夜投诉",
        likely_responses=[
            {"cyrillic": "Сейчас разберёмся.", "trans": "si-CHAS raz-bi-RYOM-sya", "cn": "我们去处理"},
        ],
    ),
    card(
        id="lodging.problem.toilet_broken", scene="lodging", n=16, tier=3,
        cyrillic="Туале́т засори́лся.", transliteration="tu-a-LYET za-sa-RIL-sya",
        chinese="马桶堵了。", literal="马桶 被堵住了",
        politeness="neutral", register_note="尴尬但必要的句子",
        likely_responses=[
            {"cyrillic": "При́шлю санте́хника.", "trans": "PRI-shlyu san-TYEKH-ni-ka", "cn": "派水管工过去"},
        ],
    ),
    card(
        id="lodging.problem.lights_off", scene="lodging", n=17, tier=3,
        cyrillic="Свет не включа́ется.", transliteration="SVYET ni fklyu-CHA-yit-sya",
        chinese="灯打不开。", literal="光 不 被打开",
        politeness="neutral", register_note="灯泡坏 / 总闸跳",
        likely_responses=[
            {"cyrillic": "Подождите, проверим автомат.", "trans": "pa-dazh-DI-tye pra-VYE-rim af-ta-MAT", "cn": "请等，检查空开"},
        ],
    ),
    # ---- 服务请求 (4) ----
    card(
        id="lodging.service.extra_towel", scene="lodging", n=18, tier=3,
        cyrillic="Принеси́те ещё одно́ полоте́нце, пожа́луйста.",
        transliteration="pri-ni-SI-tye yi-SHCHO ad-NO pa-la-TYEN-tse pa-ZHA-lus-ta",
        chinese="请再送一条毛巾。", literal="送来 还 一条 毛巾 请",
        politeness="Вы", register_note="给前台/打扫工的标准请求",
        likely_responses=[
            {"cyrillic": "Хорошо́, сейчас.", "trans": "kha-ra-SHO si-CHAS", "cn": "好的，马上"},
        ],
        slots=[
            {"label": "一瓶水", "swap": "ещё одну́ во́ду", "trans": "yi-SHCHO ad-NU VO-du"},
            {"label": "一块香皂", "swap": "ещё одно́ мы́ло", "trans": "yi-SHCHO ad-NO MY-la"},
        ],
    ),
    card(
        id="lodging.service.change_room", scene="lodging", n=19, tier=3,
        cyrillic="Мо́жно поменя́ть номер?", transliteration="MOZH-na pa-mi-NYAT' NO-mir",
        chinese="能换房间吗？", literal="可以 换 房间",
        politeness="neutral", register_note="对当前房间不满意时——通常需要说明理由",
        likely_responses=[
            {"cyrillic": "А что не так?", "trans": "a SHTO ni TAK", "cn": "哪里不对？"},
            {"cyrillic": "Сейча́с посмотрю́.", "trans": "si-CHAS pa-smat-RYU", "cn": "我看看"},
        ],
    ),
    card(
        id="lodging.service.call_taxi", scene="lodging", n=20, tier=2,
        cyrillic="Вы́зовите такси́, пожа́луйста.", transliteration="VY-za-vi-tye tak-SI pa-ZHA-lus-ta",
        chinese="请帮我叫出租。", literal="叫来 出租车 请",
        politeness="Вы", register_note="不会用 Yandex Go 时让前台叫",
        likely_responses=[
            {"cyrillic": "Куда́ е́дете?", "trans": "ku-DA YE-di-tye", "cn": "去哪？"},
            {"cyrillic": "Бу́дет че́рез 5 мину́т.", "trans": "BU-dit CHE-riz PYAT' mi-NUT", "cn": "5 分钟到"},
        ],
    ),
    card(
        id="lodging.service.wake_up_call", scene="lodging", n=21, tier=3,
        cyrillic="Разбуди́те меня́ в семь.", transliteration="raz-bu-DI-tye mi-NYA v SYEM'",
        chinese="请 7 点叫醒我。", literal="叫醒 我 在 七",
        politeness="Вы", register_note="对前台预约 morning call",
        likely_responses=[
            {"cyrillic": "Хорошо́, в семь.", "trans": "kha-ra-SHO v SYEM'", "cn": "好的，7 点"},
        ],
        slots=[
            {"label": "6 点", "swap": "в шесть", "trans": "v SHEST'"},
            {"label": "8 点", "swap": "в во́семь", "trans": "v VO-syim'"},
        ],
    ),
    # ---- checkout (4) ----
    card(
        id="lodging.checkout.leaving", scene="lodging", n=22, tier=2,
        cyrillic="Я выезжа́ю.", transliteration="ya vy-ye-ZHA-yu",
        chinese="我退房。", literal="我 离开 (现在时)",
        politeness="neutral", register_note="女性同样用此句（动词没变性）",
        likely_responses=[
            {"cyrillic": "Сейча́с распи́шемся.", "trans": "si-CHAS ras-PI-shem-sya", "cn": "我们办手续"},
            {"cyrillic": "Ключ верни́те.", "trans": "KLYUCH vir-NI-tye", "cn": "请交钥匙"},
        ],
    ),
    card(
        id="lodging.checkout.need_invoice", scene="lodging", n=23, tier=3,
        cyrillic="Мне ну́жен счёт.", transliteration="MNE NU-zhin SHCHOT",
        chinese="我要发票。", literal="给我 需要 发票",
        politeness="neutral", register_note="单位报销用——UZ 多数酒店开",
        likely_responses=[
            {"cyrillic": "На каку́ю фи́рму?", "trans": "na ka-KU-yu FIR-mu", "cn": "开给哪个公司？"},
        ],
    ),
    card(
        id="lodging.checkout.store_luggage", scene="lodging", n=24, tier=2,
        cyrillic="Мо́жно оста́вить бага́ж?", transliteration="MOZH-na as-TA-vit' ba-GAZH",
        chinese="可以寄存行李吗？", literal="可以 留下 行李",
        politeness="neutral", register_note="退房后还有几小时游玩时用",
        likely_responses=[
            {"cyrillic": "Да, в ка́мере хране́ния.", "trans": "DA v KA-mi-rye khra-NYE-ni-ya", "cn": "可以，在寄存处"},
            {"cyrillic": "Беспла́тно до ве́чера.", "trans": "bis-PLAT-na da VYE-chi-ra", "cn": "到晚上免费"},
        ],
    ),
    card(
        id="lodging.checkout.thanks_bye", scene="lodging", n=25, tier=2,
        cyrillic="Спаси́бо за всё. До свида́ния.",
        transliteration="spa-SI-ba za FSYO da svi-DA-ni-ya",
        chinese="谢谢您所做的一切。再见。", literal="谢谢 为 一切 再见",
        politeness="Вы", register_note="退房告别——比单说 Спасибо 显得周到",
        likely_responses=[
            {"cyrillic": "Прие́зжайте ещё!", "trans": "pri-ye-ZHAY-tye yi-SHCHO", "cn": "欢迎再来！"},
        ],
    ),
]


# ================================================================
# SHOPPING — 30 张（n=1-30）
# ================================================================
SHOPPING = [
    # ---- 进店 (3) ----
    card(
        id="shopping.enter.just_looking", scene="shopping", n=1, tier=2,
        cyrillic="Я про́сто смотрю́.", transliteration="ya PRO-sta smat-RYU",
        chinese="我只是看看。", literal="我 只是 看",
        politeness="neutral", register_note="对热情店员的礼貌拒绝",
        likely_responses=[
            {"cyrillic": "Пожа́луйста, не стесня́йтесь.", "trans": "pa-ZHA-lus-ta ni stis-NYAY-tyes'", "cn": "请便，别拘束"},
        ],
        local_note="UZ 巴扎店主特别热情，主动凑近介绍。一句这话他们就退后了，不会不爽。",
    ),
    card(
        id="shopping.enter.help_me", scene="shopping", n=2, tier=2,
        cyrillic="Помоги́те, пожа́луйста.", transliteration="pa-ma-GI-tye pa-ZHA-lus-ta",
        chinese="请帮帮我。", literal="帮 请",
        politeness="Вы", register_note="找东西 / 看不懂时主动求助",
        likely_responses=[
            {"cyrillic": "Что ищете?", "trans": "SHTO I-shi-tye", "cn": "找什么？"},
        ],
    ),
    card(
        id="shopping.enter.looking_for", scene="shopping", n=3, tier=2,
        cyrillic="Я ищу́ сувени́ры.", transliteration="ya i-SHU su-vi-NI-ry",
        chinese="我在找纪念品。", literal="我 找 纪念品 (复)",
        politeness="neutral", register_note="说清要找什么类目",
        likely_responses=[
            {"cyrillic": "Каки́е и́менно?", "trans": "ka-KI-ye I-min-na", "cn": "什么样的？"},
            {"cyrillic": "Пойдём, пока́жу.", "trans": "pay-DYOM pa-ka-ZHU", "cn": "来，我给您看"},
        ],
        slots=[
            {"label": "丝绸围巾", "swap": "шёлковый платок", "trans": "SHOL-ka-vy pla-TOK"},
            {"label": "陶器", "swap": "кера́мику", "trans": "ki-RA-mi-ku"},
            {"label": "小刀", "swap": "пчак", "trans": "PCHAK"},
        ],
        local_note="UZ 特产：шёлк（丝绸）、сюзане́（刺绣壁挂）、пчак（手工刀）、кера́мика（陶）。",
    ),
    # ---- 询问尺码颜色材质 (8) ----
    card(
        id="shopping.ask.bigger_size", scene="shopping", n=4, tier=2,
        cyrillic="Есть бо́льше разме́р?", transliteration="YEST' BOL'-she raz-MYER",
        chinese="有大一号吗？", literal="有 更大 尺寸",
        politeness="neutral", register_note="衣服 / 鞋通用",
        likely_responses=[
            {"cyrillic": "Сейча́с посмотрю́.", "trans": "si-CHAS pa-smat-RYU", "cn": "我看看"},
            {"cyrillic": "Нет, после́дний.", "trans": "NYET pas-LYED-niy", "cn": "没了，最后一件"},
        ],
    ),
    card(
        id="shopping.ask.smaller_size", scene="shopping", n=5, tier=2,
        cyrillic="Есть поме́ньше?", transliteration="YEST' pa-MYEN'-she",
        chinese="有小一号的吗？", literal="有 更小一些",
        politeness="neutral", register_note="同上",
        likely_responses=[
            {"cyrillic": "Да, есть.", "trans": "DA YEST'", "cn": "有"},
        ],
    ),
    card(
        id="shopping.ask.other_color", scene="shopping", n=6, tier=2,
        cyrillic="Друго́й цвет есть?", transliteration="dru-GOY TSVYET YEST'",
        chinese="有别的颜色吗？", literal="另一个 颜色 有",
        politeness="neutral", register_note="标准问句",
        likely_responses=[
            {"cyrillic": "Си́ний, кра́сный, чёрный.", "trans": "SI-niy KRAS-ny CHOR-ny", "cn": "蓝色 / 红色 / 黑色"},
        ],
    ),
    card(
        id="shopping.ask.other_model", scene="shopping", n=7, tier=3,
        cyrillic="Есть друга́я моде́ль?", transliteration="YEST' dru-GA-ya ma-DEL'",
        chinese="有别的款吗？", literal="有 另一 款式",
        politeness="neutral", register_note="店里同类产品有多种时",
        likely_responses=[
            {"cyrillic": "Подожди́те, принесу́.", "trans": "pa-dazh-DI-tye pri-ni-SU", "cn": "请等，我去拿"},
        ],
    ),
    card(
        id="shopping.ask.material", scene="shopping", n=8, tier=2,
        cyrillic="Из чего́ э́то?", transliteration="iz chi-VO E-ta",
        chinese="这是什么材质？", literal="出自 什么 这",
        politeness="neutral", register_note="买丝绸 / 皮 / 陶 必问",
        likely_responses=[
            {"cyrillic": "Сто проце́нтов шёлк.", "trans": "STO pra-TSEN-taf SHOLK", "cn": "100% 丝绸"},
            {"cyrillic": "Натура́льная кожа.", "trans": "na-tu-RAL'-na-ya KO-zha", "cn": "真皮"},
        ],
        local_note="UZ 巴扎丝绸真假并存——真丝燃烧后是头发味、不结球。当场可以撕一小角点火确认。",
    ),
    card(
        id="shopping.ask.handmade", scene="shopping", n=9, tier=3,
        cyrillic="Это вручну́ю?", transliteration="E-ta vruch-NU-yu",
        chinese="是手工的吗？", literal="这 手工地",
        politeness="neutral", register_note="买纪念品最关心的——手工的可议价 + 可讨故事",
        likely_responses=[
            {"cyrillic": "Да, моя́ ба́бушка.", "trans": "DA ma-YA BA-bush-ka", "cn": "是的，我奶奶（做的）"},
            {"cyrillic": "Маши́нная вы́шивка.", "trans": "ma-SHI-na-ya VY-shif-ka", "cn": "机绣"},
        ],
    ),
    card(
        id="shopping.ask.made_where", scene="shopping", n=10, tier=2,
        cyrillic="Где сде́лано?", transliteration="GDYE SDYE-la-na",
        chinese="哪里产的？", literal="哪里 做的",
        politeness="neutral", register_note="UZ 国货 vs 中国进口区别大",
        likely_responses=[
            {"cyrillic": "Узбекиста́н, Маргила́н.", "trans": "uz-bi-ki-STAN mar-gi-LAN", "cn": "乌兹别克 / Margilan"},
            {"cyrillic": "Кита́й.", "trans": "ki-TAY", "cn": "中国"},
        ],
        local_note="Margilan 是 UZ 丝绸传统之乡。Bukhara 出陶器和地毯。",
    ),
    card(
        id="shopping.ask.real_silk", scene="shopping", n=11, tier=3,
        cyrillic="Это нату́ральный шёлк?", transliteration="E-ta na-TU-ral'-ny SHOLK",
        chinese="这是真丝吗？", literal="这 天然的 丝",
        politeness="neutral", register_note="更直白地问真假",
        likely_responses=[
            {"cyrillic": "Да, гаранти́рую.", "trans": "DA ga-ran-TI-ru-yu", "cn": "是的，保真"},
        ],
    ),
    # ---- 试穿 (3) ----
    card(
        id="shopping.try.can_i_try", scene="shopping", n=12, tier=2,
        cyrillic="Мо́жно приме́рить?", transliteration="MOZH-na pri-MYE-rit'",
        chinese="可以试穿吗？", literal="可以 试穿",
        politeness="neutral", register_note="衣 / 鞋 / 帽通用",
        likely_responses=[
            {"cyrillic": "Коне́чно, проходи́те.", "trans": "ka-NYESH-na pra-kha-DI-tye", "cn": "当然，请进"},
        ],
    ),
    card(
        id="shopping.try.where_room", scene="shopping", n=13, tier=2,
        cyrillic="Где приме́рочная?", transliteration="GDYE pri-MYE-rach-na-ya",
        chinese="试衣间在哪？", literal="哪里 试衣间",
        politeness="neutral", register_note="找试衣间",
        likely_responses=[
            {"cyrillic": "Вон там.", "trans": "VON TAM", "cn": "那边"},
        ],
    ),
    card(
        id="shopping.try.does_it_fit", scene="shopping", n=14, tier=3,
        cyrillic="Как сиди́т?", transliteration="KAK si-DIT",
        chinese="（这件）合身吗？", literal="如何 坐着（穿着）",
        politeness="neutral", register_note="问店员看法 / 同伴看法",
        likely_responses=[
            {"cyrillic": "Хорошо́ сиди́т.", "trans": "kha-ra-SHO si-DIT", "cn": "很合身"},
            {"cyrillic": "Великова́то.", "trans": "vi-li-ka-VA-ta", "cn": "稍大"},
        ],
    ),
    # ---- 议价 (8) ----
    card(
        id="shopping.bargain.too_expensive", scene="shopping", n=15, tier=1,
        cyrillic="Это сли́шком до́рого.", transliteration="E-ta SLISH-kam DO-ra-ga",
        chinese="这太贵了。", literal="这 太 贵",
        politeness="neutral", register_note="议价开场之一——比 Дорого 更强调主观判断",
        likely_responses=[
            {"cyrillic": "Хорошо́, ско́лько дади́те?", "trans": "kha-ra-SHO SKOL'-ka da-DI-tye", "cn": "好，您给多少？"},
            {"cyrillic": "Цена́ фикси́рованная.", "trans": "tsi-NA fik-SI-ra-van-na-ya", "cn": "价格固定"},
        ],
    ),
    card(
        id="shopping.bargain.last_price", scene="shopping", n=16, tier=2,
        cyrillic="Кака́я после́дняя цена́?",
        transliteration="ka-KA-ya pas-LYED-nya-ya tsi-NA",
        chinese="底价是多少？", literal="什么样的 最后的 价格",
        politeness="neutral", register_note="对方让一次后追问",
        likely_responses=[
            {"cyrillic": "Сто ты́сяч.", "trans": "STO TY-syich", "cn": "10 万"},
            {"cyrillic": "Бо́льше уступа́ть не могу́.",
             "trans": "BOL'-she us-tu-PAT' ni ma-GU", "cn": "不能再让了"},
        ],
    ),
    card(
        id="shopping.bargain.counter_offer", scene="shopping", n=17, tier=2,
        cyrillic="Дава́йте за восемьдеся́т.",
        transliteration="da-VAY-tye za va-sim'-di-SYAT",
        chinese="八十怎么样？（还价）", literal="给吧 为 八十",
        politeness="Вы", register_note="给个数字让店家考虑",
        likely_responses=[
            {"cyrillic": "Нет, мне́е восьмиде́сяти пяти́ не могу́.",
             "trans": "NYET mni-YE va-smi-DYE-sya-ti pya-TI ni ma-GU", "cn": "85 以下我不能"},
            {"cyrillic": "Согла́сен.", "trans": "sa-GLA-sin", "cn": "成交"},
        ],
        slots=[
            {"label": "100 (千)", "swap": "за сто", "trans": "za STO"},
            {"label": "150", "swap": "за полтораста́", "trans": "za pal-ta-ra-STA"},
        ],
        local_note="UZ 巴扎议价习惯：店家先报价 → 你砍 30-50% → 对方让 10-20% → 平均 ≈ 砍掉 20-30%。",
    ),
    card(
        id="shopping.bargain.thinking", scene="shopping", n=18, tier=2,
        cyrillic="Я поду́маю.", transliteration="ya pa-DU-ma-yu",
        chinese="我再想想。", literal="我 思考",
        politeness="neutral", register_note="走开前的礼貌借口——店家通常会拉回让价",
        likely_responses=[
            {"cyrillic": "Подожди́те, для вас осо́бая цена́.",
             "trans": "pa-dazh-DI-tye dlya VAS a-SO-ba-ya tsi-NA", "cn": "请等，给您特别价"},
        ],
    ),
    card(
        id="shopping.bargain.walk_away", scene="shopping", n=19, tier=2,
        cyrillic="Нет, спаси́бо. Дорогова́то.",
        transliteration="NYET spa-SI-ba da-ra-ga-VA-ta",
        chinese="不了谢谢，太贵了。", literal="不 谢谢 偏贵",
        politeness="neutral", register_note="不接受时的礼貌离场",
        likely_responses=[
            {"cyrillic": "Ладно, дава́йте за се́мьдесят.",
             "trans": "LAD-na da-VAY-tye za SYEM'-di-syat", "cn": "好吧，70 卖你"},
        ],
        local_note="说完真的走两步——店家往往会喊住你说一个新价。这是 UZ 巴扎的真实规则。",
    ),
    card(
        id="shopping.bargain.discount_amount", scene="shopping", n=20, tier=3,
        cyrillic="Уступи́те де́сять проце́нтов?",
        transliteration="us-tu-PI-tye DYE-syit' pra-TSEN-taf",
        chinese="让 10% 行吗？", literal="让 十 百分之",
        politeness="Вы", register_note="量化议价",
        likely_responses=[
            {"cyrillic": "Пять проце́нтов могу́.",
             "trans": "PYAT' pra-TSEN-taf ma-GU", "cn": "5% 行"},
        ],
    ),
    card(
        id="shopping.bargain.round_number", scene="shopping", n=21, tier=3,
        cyrillic="Кругло́й су́ммой.", transliteration="kru-GLOY SU-may",
        chinese="给个整数。", literal="圆的 总和",
        politeness="neutral", register_note="嫌零头多——'抹零'技巧",
        likely_responses=[
            {"cyrillic": "Хорошо́, дава́йте.", "trans": "kha-ra-SHO da-VAY-tye", "cn": "好的"},
        ],
    ),
    card(
        id="shopping.bargain.bundle_deal", scene="shopping", n=22, tier=3,
        cyrillic="Если возьму́ два, скидка?",
        transliteration="YE-sli vaz'-MU DVA SKID-ka",
        chinese="买两个的话有折扣吗？", literal="如果 拿 二 折扣",
        politeness="neutral", register_note="组合买法压价",
        likely_responses=[
            {"cyrillic": "Тогда́ по две́сти.", "trans": "tag-DA pa DVYES-ti", "cn": "那么各 200"},
        ],
    ),
    # ---- 付款 (4) ----
    card(
        id="shopping.pay.ill_take_it", scene="shopping", n=23, tier=1,
        cyrillic="Беру́.", transliteration="bi-RU",
        chinese="（我）要了。", literal="我拿 (现在时)",
        politeness="neutral", register_note="拍板成交——比 Я возьму 更口语",
        likely_responses=[
            {"cyrillic": "Отли́чно.", "trans": "at-LICH-na", "cn": "好极了"},
        ],
    ),
    card(
        id="shopping.pay.wrap_it", scene="shopping", n=24, tier=3,
        cyrillic="Заверни́те, пожа́луйста.",
        transliteration="za-vir-NI-tye pa-ZHA-lus-ta",
        chinese="请帮我包好。", literal="包起来 请",
        politeness="Вы", register_note="脆品 / 礼物",
        likely_responses=[
            {"cyrillic": "В пода́рочную упако́вку?",
             "trans": "v pa-DA-rach-nu-yu u-pa-KOF-ku", "cn": "礼品包装吗？"},
        ],
    ),
    card(
        id="shopping.pay.bag_please", scene="shopping", n=25, tier=3,
        cyrillic="Да́йте паке́т, пожа́луйста.",
        transliteration="DAY-tye pa-KYET pa-ZHA-lus-ta",
        chinese="给我个袋子。", literal="给 袋子 请",
        politeness="Вы", register_note="UZ 小店有时不主动给袋",
        likely_responses=[
            {"cyrillic": "Пять ты́сяч.", "trans": "PYAT' TY-syich", "cn": "5 千（要钱）"},
        ],
        local_note="塔什干超市袋子通常 1-5 千 sum 一个，巴扎一般送。",
    ),
    card(
        id="shopping.pay.receipt", scene="shopping", n=26, tier=3,
        cyrillic="Чек, пожа́луйста.", transliteration="CHEK pa-ZHA-lus-ta",
        chinese="请给我收据。", literal="收据 请",
        politeness="neutral", register_note="退换或报销凭证",
        likely_responses=[
            {"cyrillic": "Вот, пожа́луйста.", "trans": "VOT pa-ZHA-lus-ta", "cn": "给您"},
        ],
    ),
    # ---- 特定 (4) ----
    card(
        id="shopping.special.for_gift", scene="shopping", n=27, tier=3,
        cyrillic="Это для пода́рка.", transliteration="E-ta dlya pa-DAR-ka",
        chinese="这是要送人的。", literal="这 为 礼物",
        politeness="neutral", register_note="说清用途——可能换来更好的包装 / 不同推荐",
        likely_responses=[
            {"cyrillic": "Тогда́ возьми́те вот это.",
             "trans": "tag-DA vaz'-MI-tye VOT E-ta", "cn": "那您拿这个"},
        ],
    ),
    card(
        id="shopping.special.want_traditional", scene="shopping", n=28, tier=3,
        cyrillic="Хочу́ что́-то традицио́нное.",
        transliteration="kha-CHU SHTO-ta tra-di-tsi-ON-na-ye",
        chinese="想要点传统的。", literal="想要 什么 传统的",
        politeness="neutral", register_note="找 UZ 特色礼品时点出来",
        likely_responses=[
            {"cyrillic": "Сюзане́ возьми́те.", "trans": "syu-za-NE vaz'-MI-tye", "cn": "拿件 suzani 吧"},
            {"cyrillic": "Тюбете́йка о́чень популя́рна.",
             "trans": "tyu-bi-TEY-ka O-chen' pa-pu-LYAR-na", "cn": "doppa 帽很受欢迎"},
        ],
        local_note="тюбете́йка (тypically called 'doppa' in Uzbek) — 男士方形帽，UZ 国民配饰。送朋友极地道。",
    ),
    card(
        id="shopping.special.spices", scene="shopping", n=29, tier=3,
        cyrillic="Каки́е здесь специ́и?",
        transliteration="ka-KI-ye ZDYES' spi-TSI-i",
        chinese="这里都有什么调料？", literal="什么样的 这里 调料",
        politeness="neutral", register_note="香料区买伴手礼",
        likely_responses=[
            {"cyrillic": "Зи́ра, барбари́с, шафра́н.",
             "trans": "ZI-ra bar-ba-RIS sha-FRAN", "cn": "孜然 / 小檗 / 藏红花"},
        ],
        local_note="UZ 香料：зи́ра（孜然，plov 必备）、барбари́с（小檗果，plov 配料）、шафра́н（藏红花）。",
    ),
    card(
        id="shopping.special.bukhara_origin", scene="shopping", n=30, tier=3,
        cyrillic="Это из Бухары́?", transliteration="E-ta iz bu-kha-RY",
        chinese="这是布哈拉的吗？", literal="这 出自 布哈拉",
        politeness="neutral", register_note="特定产地溯源——陶 / 地毯常问",
        likely_responses=[
            {"cyrillic": "Да, ору́чной рабо́ты.",
             "trans": "DA a-RUCH-noy ra-BO-ty", "cn": "是的，手工的"},
        ],
    ),
]


# ================================================================
# EMERGENCY — 20 张（n=1-20）
# ================================================================
EMERGENCY = [
    # ---- 求救 (4) ----
    card(
        id="emergency.help.help_me", scene="emergency", n=1, tier=1,
        cyrillic="Помоги́те!", transliteration="pa-ma-GI-tye",
        chinese="救命！", literal="帮 (祈使复)",
        politeness="Вы", register_note="一切紧急情况的开场——任何路人都会反应",
        likely_responses=[
            {"cyrillic": "Что случи́лось?", "trans": "SHTO slu-CHI-las'", "cn": "怎么了？"},
        ],
    ),
    card(
        id="emergency.help.call_police", scene="emergency", n=2, tier=1,
        cyrillic="Вы́зовите поли́цию!", transliteration="VY-za-vi-tye pa-LI-tsi-yu",
        chinese="报警！", literal="叫 警察",
        politeness="Вы", register_note="求路人 / 店家报警",
        likely_responses=[
            {"cyrillic": "Уже звоню́.", "trans": "u-ZHE zva-NYU", "cn": "已经打了"},
        ],
        local_note="UZ 警察电话 102。旅游警察会说一些英语。塔什干市中心警察岗哨多。",
    ),
    card(
        id="emergency.help.call_ambulance", scene="emergency", n=3, tier=1,
        cyrillic="Вы́зовите ско́рую!", transliteration="VY-za-vi-tye SKO-ru-yu",
        chinese="叫救护车！", literal="叫 急救（车）",
        politeness="Вы", register_note="紧急医疗",
        likely_responses=[
            {"cyrillic": "Где боли́т?", "trans": "GDYE ba-LIT", "cn": "哪里疼？"},
            {"cyrillic": "Сейча́с.", "trans": "si-CHAS", "cn": "马上（叫）"},
        ],
        local_note="UZ 救护车电话 103。中国驻塔什干使馆领事保护电话 +998-71-238-8857。",
    ),
    card(
        id="emergency.help.fire", scene="emergency", n=4, tier=1,
        cyrillic="Пожа́р!", transliteration="pa-ZHAR",
        chinese="着火了！", literal="火灾",
        politeness="neutral", register_note="一个词就够——所有人都会动",
        likely_responses=[],
        local_note="UZ 消防电话 101。",
    ),
    # ---- 身体不适 (6) ----
    card(
        id="emergency.health.unwell", scene="emergency", n=5, tier=2,
        cyrillic="Мне пло́хо.", transliteration="MNYE PLO-kha",
        chinese="我不舒服。", literal="给我 不好",
        politeness="neutral", register_note="泛指身体不适——会引来追问哪里疼",
        likely_responses=[
            {"cyrillic": "Что боли́т?", "trans": "SHTO ba-LIT", "cn": "哪里疼？"},
            {"cyrillic": "Се́сть мо́жете?", "trans": "SYEST' MO-zhi-tye", "cn": "您能坐下吗？"},
        ],
    ),
    card(
        id="emergency.health.headache", scene="emergency", n=6, tier=2,
        cyrillic="У меня́ боли́т голова́.",
        transliteration="u mi-NYA ba-LIT ga-la-VA",
        chinese="我头疼。", literal="在 我 疼 头",
        politeness="neutral", register_note="高原 / 水土不服 / 中暑都可用",
        likely_responses=[
            {"cyrillic": "Прими́те таблетку.", "trans": "pri-MI-tye tab-LYET-ku", "cn": "吃片药"},
        ],
    ),
    card(
        id="emergency.health.stomachache", scene="emergency", n=7, tier=2,
        cyrillic="У меня́ боли́т живо́т.",
        transliteration="u mi-NYA ba-LIT zhi-VOT",
        chinese="我肚子疼。", literal="在 我 疼 肚子",
        politeness="neutral", register_note="UZ 食物油重，旅行者初期常发",
        likely_responses=[
            {"cyrillic": "Что е́ли?", "trans": "SHTO YE-li", "cn": "吃了什么？"},
            {"cyrillic": "Купи́те смекту.", "trans": "ku-PI-tye SMYEK-tu", "cn": "买思密达"},
        ],
        local_note="UZ 药店有 смекта（Smecta，止泻）+ но-шпа（解痉）。带瓶蒙脱石散自备最稳。",
    ),
    card(
        id="emergency.health.allergy", scene="emergency", n=8, tier=2,
        cyrillic="У меня́ аллерги́я.", transliteration="u mi-NYA a-lir-GI-ya",
        chinese="我过敏。", literal="在 我 过敏",
        politeness="neutral", register_note="餐厅 / 药店都可能用",
        likely_responses=[
            {"cyrillic": "На что и́менно?", "trans": "na SHTO I-min-na", "cn": "对什么过敏？"},
        ],
        slots=[
            {"label": "对花生", "swap": "на ара́хис", "trans": "na a-RA-khis"},
            {"label": "对海鲜", "swap": "на морепроду́кты", "trans": "na ma-ri-pra-DUK-ty"},
        ],
    ),
    card(
        id="emergency.health.need_medicine", scene="emergency", n=9, tier=2,
        cyrillic="Мне ну́жно лека́рство.",
        transliteration="MNYE NUZH-na li-KARS-tva",
        chinese="我需要药。", literal="给我 需要 药品",
        politeness="neutral", register_note="药店 / 求路人指路",
        likely_responses=[
            {"cyrillic": "От чего́?", "trans": "at chi-VO", "cn": "什么药？"},
        ],
    ),
    card(
        id="emergency.health.where_pharmacy", scene="emergency", n=10, tier=1,
        cyrillic="Где апте́ка?", transliteration="GDYE ap-TYE-ka",
        chinese="药店在哪？", literal="哪里 药店",
        politeness="neutral", register_note="UZ 药店招牌 АПТЕКА、绿十字",
        likely_responses=[
            {"cyrillic": "На углу́.", "trans": "na ug-LU", "cn": "在路口"},
            {"cyrillic": "Кругло́суточная вон там.",
             "trans": "kru-gla-SU-tach-na-ya VON TAM", "cn": "24 小时店在那边"},
        ],
    ),
    # ---- 失物 (4) ----
    card(
        id="emergency.lost.passport", scene="emergency", n=11, tier=1,
        cyrillic="Я потеря́л паспорт.", transliteration="ya pa-ti-RYAL PAS-part",
        chinese="我护照丢了。", literal="我 丢失了 护照",
        politeness="neutral", register_note="女性说 потеря́ла (pa-ti-RYA-la)。最严重的失物之一",
        likely_responses=[
            {"cyrillic": "Иди́те в полицию.", "trans": "i-DI-tye v pa-LI-tsi-yu", "cn": "去警察局"},
            {"cyrillic": "Звони́те в посо́льство.",
             "trans": "zva-NI-tye v pa-SOL'-stva", "cn": "打使馆电话"},
        ],
        local_note="护照丢必须先报警拿到报案证明，再去中国驻塔什干使馆补办。",
    ),
    card(
        id="emergency.lost.wallet", scene="emergency", n=12, tier=2,
        cyrillic="Я потеря́л кошелёк.",
        transliteration="ya pa-ti-RYAL ka-shi-LYOK",
        chinese="我钱包丢了。", literal="我 丢失了 钱包",
        politeness="neutral", register_note="女性 потеря́ла",
        likely_responses=[
            {"cyrillic": "Где после́дний раз ви́дели?",
             "trans": "GDYE pas-LYED-niy RAS VI-di-li", "cn": "最后在哪见过？"},
        ],
    ),
    card(
        id="emergency.lost.phone", scene="emergency", n=13, tier=2,
        cyrillic="Я потеря́л телефо́н.",
        transliteration="ya pa-ti-RYAL ti-li-FON",
        chinese="我手机丢了。", literal="我 丢失了 电话",
        politeness="neutral", register_note="女性 потеря́ла",
        likely_responses=[
            {"cyrillic": "Я позвоню́ вам.", "trans": "ya pa-zva-NYU vam", "cn": "我帮您打打"},
        ],
    ),
    card(
        id="emergency.lost.consulate", scene="emergency", n=14, tier=2,
        cyrillic="Где кита́йское консу́льство?",
        transliteration="GDYE ki-TAY-ska-ye kan-SUL'-stva",
        chinese="中国领事馆在哪？", literal="哪里 中国的 领事馆",
        politeness="neutral", register_note="护照 / 重大事件",
        likely_responses=[
            {"cyrillic": "На Гёте, 49.", "trans": "na GYO-te SOROK DYE-vit'", "cn": "在 Goethe 街 49 号"},
        ],
        local_note="中国驻塔什干大使馆地址：улица Гёте 49（49 Goethe St.）。领保 +998-71-238-8857。",
    ),
    # ---- 联络 (3) ----
    card(
        id="emergency.contact.hospital", scene="emergency", n=15, tier=2,
        cyrillic="Где больни́ца?", transliteration="GDYE bal'-NI-tsa",
        chinese="医院在哪？", literal="哪里 医院",
        politeness="neutral", register_note="急症求路",
        likely_responses=[
            {"cyrillic": "Бли́же все́го — ЦКБ.",
             "trans": "BLI-zhe fsi-VO TSE-KA-BE", "cn": "最近的是中央临床医院"},
        ],
        local_note="塔什干涉外推荐：Tashkent International Medical Clinic（TIMC）有英语医生。",
    ),
    card(
        id="emergency.contact.police_station", scene="emergency", n=16, tier=2,
        cyrillic="Где полице́йский уча́сток?",
        transliteration="GDYE pa-li-TSEY-skiy u-CHAS-tak",
        chinese="警察局在哪？", literal="哪里 警察的 分驻所",
        politeness="neutral", register_note="报案",
        likely_responses=[
            {"cyrillic": "Иди́те пря́мо два кварта́ла.",
             "trans": "i-DI-tye PRYA-ma DVA kvar-TA-la", "cn": "直走两个街区"},
        ],
    ),
    card(
        id="emergency.contact.help_translate", scene="emergency", n=17, tier=3,
        cyrillic="Помоги́те с перево́дом.",
        transliteration="pa-ma-GI-tye s pi-ri-VO-dam",
        chinese="帮我翻译一下。", literal="帮 跟 翻译",
        politeness="Вы", register_note="语言鸿沟下求路人 / 工作人员转中介翻译",
        likely_responses=[
            {"cyrillic": "Англи́йский знаете?",
             "trans": "an-GLIY-skiy ZNA-yi-tye", "cn": "您懂英语吗？"},
        ],
    ),
    # ---- 安全 (3) ----
    card(
        id="emergency.safety.dont_touch", scene="emergency", n=18, tier=2,
        cyrillic="Не тро́гайте меня́!",
        transliteration="ni TRO-gay-tye mi-NYA",
        chinese="别碰我！", literal="不 碰 我",
        politeness="Вы", register_note="陌生人骚扰时严厉拒绝",
        likely_responses=[],
    ),
    card(
        id="emergency.safety.leave_me_alone", scene="emergency", n=19, tier=2,
        cyrillic="Оста́вьте меня́ в поко́е!",
        transliteration="as-TAF'-tye mi-NYA f pa-KO-ye",
        chinese="别烦我！", literal="留下 我 在 安宁",
        politeness="Вы", register_note="纠缠不去的人",
        likely_responses=[],
    ),
    card(
        id="emergency.safety.will_call_police", scene="emergency", n=20, tier=3,
        cyrillic="Я вы́зову поли́цию!",
        transliteration="ya VY-za-vu pa-LI-tsi-yu",
        chinese="我要报警了！", literal="我 会叫 警察",
        politeness="neutral", register_note="威慑——通常会让对方退后",
        likely_responses=[
            {"cyrillic": "Не надо, я ухожу.",
             "trans": "ni NA-da ya u-kha-ZHU", "cn": "别，我走"},
        ],
    ),
]


# ================================================================
# CHAT — 25 张（n=1-25）
# ================================================================
CHAT = [
    # ---- 天气 (3) ----
    card(
        id="chat.weather.nice_today", scene="chat", n=1, tier=2,
        cyrillic="Сего́дня хоро́шая пого́да.",
        transliteration="si-VOD-nya kha-RO-sha-ya pa-GO-da",
        chinese="今天天气真好。", literal="今天 好的 天气",
        politeness="neutral", register_note="所有 small talk 的万能开场",
        likely_responses=[
            {"cyrillic": "Да, ре́дкость.", "trans": "DA RYED-kast'", "cn": "是啊，难得"},
        ],
    ),
    card(
        id="chat.weather.too_hot", scene="chat", n=2, tier=2,
        cyrillic="Очень жа́рко сего́дня.",
        transliteration="O-chen' ZHAR-ka si-VOD-nya",
        chinese="今天好热。", literal="非常 热 今天",
        politeness="neutral", register_note="UZ 7-8 月日常",
        likely_responses=[
            {"cyrillic": "Да, ле́то.", "trans": "DA LYE-ta", "cn": "对啊，夏天"},
        ],
    ),
    card(
        id="chat.weather.will_rain", scene="chat", n=3, tier=3,
        cyrillic="Бу́дет дождь?", transliteration="BU-dit DOZHD'",
        chinese="会下雨吗？", literal="将会 雨",
        politeness="neutral", register_note="出门前问",
        likely_responses=[
            {"cyrillic": "Говоря́т, к ве́черу.",
             "trans": "ga-va-RYAT k VYE-chi-ru", "cn": "据说傍晚"},
            {"cyrillic": "Нет, всё чи́сто.", "trans": "NYET FSYO CHIS-ta", "cn": "不下，晴的"},
        ],
    ),
    # ---- 寒暄 (5) ----
    card(
        id="chat.greet.how_are_you", scene="chat", n=4, tier=2,
        cyrillic="Как ва́ши дела́?", transliteration="KAK VA-shi di-LA",
        chinese="您过得怎么样？", literal="如何 您的 事情",
        politeness="Вы", register_note="见过一次的熟人 / 朋友",
        likely_responses=[
            {"cyrillic": "Хорошо́, спаси́бо.", "trans": "kha-ra-SHO spa-SI-ba", "cn": "好，谢谢"},
            {"cyrillic": "Нормально.", "trans": "nar-MAL'-na", "cn": "还行"},
        ],
    ),
    card(
        id="chat.greet.fine_thanks", scene="chat", n=5, tier=2,
        cyrillic="У меня́ всё хорошо́.",
        transliteration="u mi-NYA FSYO kha-ra-SHO",
        chinese="我一切都好。", literal="在 我 一切 好",
        politeness="neutral", register_note="对 Как дела 的标准回答",
        likely_responses=[],
    ),
    card(
        id="chat.greet.nice_to_meet", scene="chat", n=6, tier=2,
        cyrillic="Очень прия́тно.", transliteration="O-chen' pri-YAT-na",
        chinese="幸会。", literal="非常 愉快",
        politeness="neutral", register_note="互报姓名后说",
        likely_responses=[
            {"cyrillic": "Взаимно.", "trans": "vza-IM-na", "cn": "彼此彼此"},
        ],
    ),
    card(
        id="chat.greet.your_name", scene="chat", n=7, tier=2,
        cyrillic="Как вас зову́т?", transliteration="KAK VAS za-VOOT",
        chinese="您叫什么名字？", literal="如何 您 称呼",
        politeness="Вы", register_note="对陌生人/新认识的人",
        likely_responses=[
            {"cyrillic": "Меня́ зову́т Али́.", "trans": "mi-NYA za-VOOT a-LI", "cn": "我叫 Ali"},
        ],
    ),
    card(
        id="chat.greet.where_from", scene="chat", n=8, tier=2,
        cyrillic="Отку́да вы?", transliteration="at-KU-da VY",
        chinese="您是哪里人？", literal="从哪里 您",
        politeness="Вы", register_note="互相打听",
        likely_responses=[
            {"cyrillic": "Я из Ташке́нта.", "trans": "ya iz tash-KYEN-ta", "cn": "我是塔什干人"},
            {"cyrillic": "Я из Самарка́нда.", "trans": "ya iz sa-mar-KAN-da", "cn": "我是撒马尔罕人"},
        ],
    ),
    # ---- 关于 UZ (5) ----
    card(
        id="chat.uz.first_time", scene="chat", n=9, tier=2,
        cyrillic="Я пе́рвый раз в Узбекиста́не.",
        transliteration="ya PYER-vy RAZ v uz-bi-ki-STA-nye",
        chinese="我是第一次来乌兹别克斯坦。", literal="我 第一 次 在 乌兹别克斯坦",
        politeness="neutral", register_note="女性同样用 первый（不变性）",
        likely_responses=[
            {"cyrillic": "Как вам у нас?", "trans": "KAK vam u NAS", "cn": "您觉得我们这怎么样？"},
            {"cyrillic": "Добро́ пожа́ловать!", "trans": "da-BRO pa-ZHA-la-vat'", "cn": "欢迎！"},
        ],
    ),
    card(
        id="chat.uz.local_native", scene="chat", n=10, tier=3,
        cyrillic="Вы здесь родили́сь?",
        transliteration="VY ZDYES' ra-di-LIS'",
        chinese="您是本地人吗？", literal="您 这里 出生",
        politeness="Вы", register_note="问对方是否本地",
        likely_responses=[
            {"cyrillic": "Да, коренно́й ташке́нтец.",
             "trans": "DA ka-rin-NOY tash-KYEN-tits", "cn": "对，地道塔什干人"},
        ],
    ),
    card(
        id="chat.uz.beautiful", scene="chat", n=11, tier=2,
        cyrillic="У вас о́чень краси́во.",
        transliteration="u VAS O-chen' kra-SI-va",
        chinese="你们这儿真漂亮。", literal="在 您 非常 美",
        politeness="Вы", register_note="夸城市 / 风景——本地人爱听",
        likely_responses=[
            {"cyrillic": "Спаси́бо, прия́тно слы́шать.",
             "trans": "spa-SI-ba pri-YAT-na SLY-shat'", "cn": "谢谢，听到很高兴"},
        ],
    ),
    card(
        id="chat.uz.kind_people", scene="chat", n=12, tier=2,
        cyrillic="Лю́ди здесь о́чень до́брые.",
        transliteration="LYU-di ZDYES' O-chen' DOB-ry-ye",
        chinese="这里的人真好。", literal="人 这里 非常 善良 (复)",
        politeness="neutral", register_note="赞美对方文化的安全句",
        likely_responses=[
            {"cyrillic": "Мы стара́емся.", "trans": "MY sta-RA-yim-sya", "cn": "我们尽力"},
        ],
    ),
    card(
        id="chat.uz.recommend_visit", scene="chat", n=13, tier=2,
        cyrillic="Что посове́туете посмотре́ть?",
        transliteration="SHTO pa-sa-VYE-tu-ye-tye pa-smat-RYET'",
        chinese="您推荐去哪儿看看？", literal="什么 您建议 看",
        politeness="Вы", register_note="本地人指南——最值得问",
        likely_responses=[
            {"cyrillic": "Обяза́тельно Самарка́нд и Бухара́.",
             "trans": "a-bi-ZA-til'-na sa-mar-KAND i bu-kha-RA",
             "cn": "一定去撒马尔罕和布哈拉"},
            {"cyrillic": "В Ташке́нте Чорсу́.",
             "trans": "v tash-KYEN-tye char-SU", "cn": "塔什干就 Chorsu 巴扎"},
        ],
    ),
    # ---- 关于中国 (3) ----
    card(
        id="chat.cn.been_to_china", scene="chat", n=14, tier=2,
        cyrillic="Вы бы́ли в Кита́е?",
        transliteration="VY BY-li v ki-TA-ye",
        chinese="您去过中国吗？", literal="您 曾在 在 中国",
        politeness="Вы", register_note="自然话题——UZ 商人 / 留学生很多去过",
        likely_responses=[
            {"cyrillic": "Да, в Урумчи.", "trans": "DA v u-RUM-chi", "cn": "去过，乌鲁木齐"},
            {"cyrillic": "Нет, хочу́ съе́здить.",
             "trans": "NYET kha-CHU SYEZ-dit'", "cn": "没有，想去"},
        ],
        local_note="UZ-CN 直飞航班多。塔什干 ↔ 乌鲁木齐 / 西安 / 北京。许多 UZ 人在中国留过学。",
    ),
    card(
        id="chat.cn.china_big", scene="chat", n=15, tier=3,
        cyrillic="Кита́й о́чень большо́й.",
        transliteration="ki-TAY O-chen' bal'-SHOY",
        chinese="中国很大。", literal="中国 非常 大",
        politeness="neutral", register_note="被问中国哪里来后引出地理介绍",
        likely_responses=[
            {"cyrillic": "Из како́го го́рода?",
             "trans": "iz ka-KO-va GO-ra-da", "cn": "哪个城市？"},
        ],
    ),
    card(
        id="chat.cn.welcome_to_china", scene="chat", n=16, tier=2,
        cyrillic="Прие́зжайте к нам в Кита́й.",
        transliteration="pri-ye-ZHAY-tye k nam v ki-TAY",
        chinese="欢迎来中国。", literal="来 (祈使) 到 我们 在 中国",
        politeness="Вы", register_note="临别时邀请",
        likely_responses=[
            {"cyrillic": "С удово́льствием!",
             "trans": "s u-da-VOL'-stvi-yim", "cn": "乐意！"},
        ],
    ),
    # ---- 兴趣 (4) ----
    card(
        id="chat.interest.like_tea", scene="chat", n=17, tier=3,
        cyrillic="Вы лю́бите чай?",
        transliteration="VY LYU-bi-tye CHAY",
        chinese="您喜欢茶吗？", literal="您 爱 茶",
        politeness="Вы", register_note="UZ 茶文化深——回应丰富",
        likely_responses=[
            {"cyrillic": "Без ча́я не могу́.",
             "trans": "bes CHA-ya ni ma-GU", "cn": "没茶活不下去"},
            {"cyrillic": "Зелёный лю́блю.", "trans": "zi-LYO-ny LYU-blyu", "cn": "我爱绿茶"},
        ],
    ),
    card(
        id="chat.interest.fav_plov", scene="chat", n=18, tier=3,
        cyrillic="Како́й ваш люби́мый плов?",
        transliteration="ka-KOY VASH lyu-BI-my PLOF",
        chinese="您最喜欢哪种 plov？", literal="什么 您的 最爱 plov",
        politeness="Вы", register_note="必胜话题——所有 UZ 人都能聊 10 分钟",
        likely_responses=[
            {"cyrillic": "Ферга́нский, конечно.",
             "trans": "fir-GAN-skiy ka-NYESH-na", "cn": "Fergana 的，当然"},
            {"cyrillic": "Самарка́ндский лу́чше.",
             "trans": "sa-mar-KAN-skiy LUTCH-she", "cn": "撒马尔罕的更好"},
        ],
        local_note="UZ plov 流派之争：Fergana（费尔干纳，浓郁油重）vs Tashkent（清淡蓬松）vs Samarkand（层次分明）。",
    ),
    card(
        id="chat.interest.play_football", scene="chat", n=19, tier=3,
        cyrillic="Игра́ете в футбо́л?",
        transliteration="i-GRA-yi-tye v fut-BOL",
        chinese="您踢足球吗？", literal="您玩 在 足球",
        politeness="Вы", register_note="UZ 男士最普及的运动",
        likely_responses=[
            {"cyrillic": "В детстве, сейчас то́лько смотрю.",
             "trans": "v DYET-stvye si-CHAS TOL'-ka smat-RYU",
             "cn": "小时候踢，现在只看"},
        ],
    ),
    card(
        id="chat.interest.china_popular", scene="chat", n=20, tier=3,
        cyrillic="У нас в Кита́е популя́рен TikTok.",
        transliteration="u nas v ki-TA-ye pa-pu-LYA-rin TIK-tok",
        chinese="我们中国流行 TikTok。", literal="在 我们 在 中国 流行 TikTok",
        politeness="neutral", register_note="自然介绍家乡——可以替换主题",
        likely_responses=[
            {"cyrillic": "У нас то́же.", "trans": "u NAS TO-zhe", "cn": "我们也是"},
        ],
        slots=[
            {"label": "微信", "swap": "WeChat", "trans": "WEE-chat"},
            {"label": "高铁", "swap": "скоростны́е поезда́", "trans": "ska-ras-NY-ye pa-yiz-DA"},
        ],
    ),
    # ---- 告别延伸 (5) ----
    card(
        id="chat.bye.was_nice", scene="chat", n=21, tier=2,
        cyrillic="Бы́ло о́чень прия́тно.",
        transliteration="BY-la O-chen' pri-YAT-na",
        chinese="（聊天）很愉快。", literal="是 非常 愉快",
        politeness="neutral", register_note="告别前的礼貌结尾",
        likely_responses=[
            {"cyrillic": "Мне то́же.", "trans": "MNYE TO-zhe", "cn": "我也是"},
        ],
    ),
    card(
        id="chat.bye.good_luck", scene="chat", n=22, tier=2,
        cyrillic="Уда́чи!", transliteration="u-DA-chi",
        chinese="祝好运！", literal="（祝）幸运",
        politeness="neutral", register_note="临别万能祝福",
        likely_responses=[
            {"cyrillic": "И вам.", "trans": "i VAM", "cn": "您也是"},
        ],
    ),
    card(
        id="chat.bye.take_care", scene="chat", n=23, tier=2,
        cyrillic="Берегите себя́.",
        transliteration="bi-ri-GI-tye si-BYA",
        chinese="保重。", literal="保护 自己",
        politeness="Вы", register_note="长辈 / 较深感情的告别",
        likely_responses=[
            {"cyrillic": "И вы то́же.", "trans": "i VY TO-zhe", "cn": "您也是"},
        ],
    ),
    card(
        id="chat.bye.see_you_later", scene="chat", n=24, tier=2,
        cyrillic="До встре́чи.", transliteration="da FSTRYE-chi",
        chinese="再见，期待再见。", literal="到 见面",
        politeness="neutral", register_note="比 До свидания 更口语，预期还会见",
        likely_responses=[
            {"cyrillic": "До встре́чи!", "trans": "da FSTRYE-chi", "cn": "再见！"},
        ],
    ),
    card(
        id="chat.bye.exchange_contact", scene="chat", n=25, tier=3,
        cyrillic="Дава́йте обменя́емся контакта́ми.",
        transliteration="da-VAY-tye ab-mi-NYA-yim-sya kan-tak-TA-mi",
        chinese="加个联系方式吧。", literal="给吧 交换 联系方式",
        politeness="Вы", register_note="想保持联系时",
        likely_responses=[
            {"cyrillic": "В Telegram?", "trans": "v TYE-li-gram", "cn": "Telegram？"},
            {"cyrillic": "Запиши́те мой но́мер.",
             "trans": "za-pi-SHI-tye MOY NO-mir", "cn": "记下我的电话"},
        ],
        local_note="UZ 主流即时通讯：Telegram（最普及）+ Imo（较老一辈用）。微信在 UZ 不通用。",
    ),
]


# ================================================================
# FOOD 增量 — 15 张（n=26-40）
# ================================================================
FOOD_EXT = [
    # ---- 烹饪方式 (4) ----
    card(
        id="food.cook.fried", scene="food", n=26, tier=3,
        cyrillic="Жа́реное.", transliteration="ZHA-ri-na-ye",
        chinese="炒/煎的。", literal="炒过的 (中性)",
        politeness="neutral", register_note="单词描述菜的做法",
        likely_responses=[],
    ),
    card(
        id="food.cook.boiled", scene="food", n=27, tier=3,
        cyrillic="Варёное.", transliteration="va-RYO-na-ye",
        chinese="煮的。", literal="煮过的",
        politeness="neutral", register_note="同上",
        likely_responses=[],
    ),
    card(
        id="food.cook.baked", scene="food", n=28, tier=3,
        cyrillic="Печёное.", transliteration="pi-CHO-na-ye",
        chinese="烤的（烤箱）。", literal="烤过的",
        politeness="neutral", register_note="区别于明火烤串 (шашлык)",
        likely_responses=[],
    ),
    card(
        id="food.cook.steamed", scene="food", n=29, tier=3,
        cyrillic="На пару́.", transliteration="na pa-RU",
        chinese="蒸的。", literal="在 蒸气",
        politeness="neutral", register_note="manti（蒸饺）的做法",
        likely_responses=[],
    ),
    # ---- 辣度 (2) ----
    card(
        id="food.taste.not_spicy", scene="food", n=30, tier=2,
        cyrillic="Не о́строе, пожа́луйста.",
        transliteration="ni O-stra-ye pa-ZHA-lus-ta",
        chinese="不要辣的，谢谢。", literal="不 辣 请",
        politeness="neutral", register_note="UZ 菜整体不辣但有些汤会加红辣椒",
        likely_responses=[
            {"cyrillic": "Хорошо́, без перца.",
             "trans": "kha-ra-SHO bes PYER-tsa", "cn": "好，不放辣椒"},
        ],
    ),
    card(
        id="food.taste.spicy_yes", scene="food", n=31, tier=3,
        cyrillic="Поо́стрее, пожа́луйста.",
        transliteration="pa-O-stre-ye pa-ZHA-lus-ta",
        chinese="辣一点，谢谢。", literal="更辣一些 请",
        politeness="neutral", register_note="爱吃辣的中国胃求加辣",
        likely_responses=[
            {"cyrillic": "Доба́влю острой паприки.",
             "trans": "da-BAV-lyu O-stray PAP-ri-ki", "cn": "我加红辣椒"},
        ],
    ),
    # ---- 当地菜补 (3) ----
    card(
        id="food.local.lagman", scene="food", n=32, tier=2,
        cyrillic="Лагма́н, пожа́луйста.",
        transliteration="lag-MAN pa-ZHA-lus-ta",
        chinese="请来碗 lagman。", literal="lagman 请",
        politeness="neutral", register_note="UZ 中亚拉面——肉 + 蔬菜浓汤面",
        likely_responses=[
            {"cyrillic": "Уйгу́рский и́ли узбе́кский?",
             "trans": "uy-GUR-skiy I-li uz-BYEK-skiy", "cn": "维吾尔风还是乌兹别克风？"},
        ],
        local_note="Lagman 起源于中国西北，UZ 化后汤更浓、加更多胡椒。",
    ),
    card(
        id="food.local.shurpa", scene="food", n=33, tier=2,
        cyrillic="Шу́рпа.", transliteration="SHUR-pa",
        chinese="羊肉汤。", literal="shurpa",
        politeness="neutral", register_note="UZ 经典清汤——羊肉 + 整根胡萝卜 + 整块土豆",
        likely_responses=[
            {"cyrillic": "Гото́в че́рез 20 мину́т.",
             "trans": "ga-TOF CHE-riz DVA-tsat' mi-NUT", "cn": "20 分钟后好"},
        ],
        local_note="Shurpa 是 UZ 婚宴必备开胃菜。配 lepyoshka 蘸汤吃。",
    ),
    card(
        id="food.local.manti", scene="food", n=34, tier=2,
        cyrillic="Манты́.", transliteration="man-TY",
        chinese="（中亚）大蒸饺。", literal="manti",
        politeness="neutral", register_note="UZ 蒸饺，比中国饺子大三倍，馅多",
        likely_responses=[
            {"cyrillic": "С мя́сом или с тыквой?",
             "trans": "s MYA-sam I-li s TYK-vay", "cn": "肉馅还是南瓜馅？"},
        ],
        local_note="UZ manti 馅常见：肉（уте）/ 南瓜（тыква，秋冬）/ 土豆（картошка）。",
    ),
    # ---- 主食 (2) ----
    card(
        id="food.staple.rice", scene="food", n=35, tier=3,
        cyrillic="Рис, пожа́луйста.",
        transliteration="RIS pa-ZHA-lus-ta",
        chinese="（来份）米饭。", literal="米 请",
        politeness="neutral", register_note="单点白米饭——plov 已含米",
        likely_responses=[
            {"cyrillic": "Сколько порций?",
             "trans": "SKOL'-ka POR-tsiy", "cn": "几份？"},
        ],
    ),
    card(
        id="food.staple.noodles", scene="food", n=36, tier=3,
        cyrillic="Лапша́.", transliteration="lap-SHA",
        chinese="面条。", literal="面条",
        politeness="neutral", register_note="lagman 或单点面",
        likely_responses=[],
    ),
    # ---- 饮料补 (2) ----
    card(
        id="food.drink.ayran", scene="food", n=37, tier=3,
        cyrillic="Айра́н, пожа́луйста.",
        transliteration="ay-RAN pa-ZHA-lus-ta",
        chinese="请来杯 ayran。", literal="ayran 请",
        politeness="neutral", register_note="咸味酸奶饮料——解油腻必备",
        likely_responses=[
            {"cyrillic": "Холо́дный?", "trans": "kha-LOD-ny", "cn": "冰的？"},
        ],
        local_note="Ayran 是中亚 / 高加索经典饮料，搭 plov / shashlyk 解腻；夏天必喝。",
    ),
    card(
        id="food.drink.pomegranate", scene="food", n=38, tier=3,
        cyrillic="Гра́натовый сок.",
        transliteration="GRA-na-ta-vy SOK",
        chinese="石榴汁。", literal="石榴的 汁",
        politeness="neutral", register_note="UZ 石榴当地产、便宜、地道",
        likely_responses=[
            {"cyrillic": "Свежевы́жатый.",
             "trans": "svi-zhi-VY-zha-ty", "cn": "现榨的"},
        ],
    ),
    # ---- 礼仪 (2) ----
    card(
        id="food.etiquette.im_full", scene="food", n=39, tier=2,
        cyrillic="Я нае́лся, спаси́бо.",
        transliteration="ya na-YEL-sya spa-SI-ba",
        chinese="我吃饱了，谢谢。", literal="我 吃饱了 (男) 谢谢",
        politeness="neutral", register_note="女性说 нае́лась (na-YE-las')",
        likely_responses=[
            {"cyrillic": "Ещё чай попьёте?",
             "trans": "yi-SHCHO CHAY pap-YO-tye", "cn": "再喝点茶？"},
        ],
        local_note="UZ 主人客观期待你吃多——说不下去要重复几次。这句直接打住最有效。",
    ),
    card(
        id="food.etiquette.cheers", scene="food", n=40, tier=3,
        cyrillic="За ва́ше здоро́вье!",
        transliteration="za VA-she zda-RO-vye",
        chinese="为您的健康（干杯）！", literal="为 您的 健康",
        politeness="Вы", register_note="UZ 餐桌——长辈先举杯，依次跟进",
        likely_responses=[
            {"cyrillic": "И за ва́ше!", "trans": "I za VA-she", "cn": "也为您的！"},
        ],
        local_note="UZ 敬酒文化重——婚宴每轮会指定一人念长祝词后大家干杯。带瓶中国白酒回送是好礼。",
    ),
]


# ================================================================
# TRANSPORT 增量 — 10 张（n=26-35）
# ================================================================
TRANSPORT_EXT = [
    # ---- 火车 (4) ----
    card(
        id="transport.train.buy_ticket", scene="transport", n=26, tier=2,
        cyrillic="Оди́н биле́т до Самарка́нда.",
        transliteration="a-DIN bi-LYET da sa-mar-KAN-da",
        chinese="一张到撒马尔罕的票。", literal="一 票 到 撒马尔罕",
        politeness="neutral", register_note="火车窗口标准句",
        likely_responses=[
            {"cyrillic": "В каку́ю сто́рону?",
             "trans": "v ka-KU-yu STO-ra-nu", "cn": "去程还是回程？"},
            {"cyrillic": "На како́е число́?",
             "trans": "na ka-KO-ye chis-LO", "cn": "几号的？"},
        ],
        slots=[
            {"label": "到布哈拉", "swap": "до Бухары́", "trans": "da bu-kha-RY"},
            {"label": "到希瓦", "swap": "до Хи́вы", "trans": "da KHI-vy"},
        ],
        local_note="UZ 高铁 Afrosiyob：塔什干 ↔ 撒马尔罕 2 小时 / ↔ 布哈拉 4 小时。提前 1 周买。",
    ),
    card(
        id="transport.train.departure_time", scene="transport", n=27, tier=2,
        cyrillic="Когда́ отправле́ние?",
        transliteration="kag-DA at-prav-LYE-ni-ye",
        chinese="几点开车？", literal="何时 发车",
        politeness="neutral", register_note="买完票确认",
        likely_responses=[
            {"cyrillic": "В семь со́рок утра́.",
             "trans": "v SYEM' SO-rak ut-RA", "cn": "早 7:40"},
        ],
    ),
    card(
        id="transport.train.platform", scene="transport", n=28, tier=2,
        cyrillic="Како́й путь?", transliteration="ka-KOY PUT'",
        chinese="几号站台？", literal="什么 路（道）",
        politeness="neutral", register_note="进站后定位",
        likely_responses=[
            {"cyrillic": "Тре́тий, спра́ва.",
             "trans": "TRYE-tiy SPRA-va", "cn": "3 号，右边"},
        ],
    ),
    card(
        id="transport.train.carriage", scene="transport", n=29, tier=2,
        cyrillic="Како́й ваго́н?", transliteration="ka-KOY va-GON",
        chinese="几号车厢？", literal="什么 车厢",
        politeness="neutral", register_note="上车前确认（票上有但口语再问）",
        likely_responses=[
            {"cyrillic": "Пя́тый.", "trans": "PYA-ty", "cn": "5 号"},
        ],
    ),
    # ---- 飞机 (3) ----
    card(
        id="transport.flight.checkin", scene="transport", n=30, tier=2,
        cyrillic="Где регистра́ция?",
        transliteration="GDYE ri-gi-STRA-tsi-ya",
        chinese="在哪 check-in？", literal="哪里 登记",
        politeness="neutral", register_note="进机场后找柜台",
        likely_responses=[
            {"cyrillic": "Стойка 12.", "trans": "STOY-ka dvi-NA-tsat'", "cn": "12 号柜台"},
        ],
    ),
    card(
        id="transport.flight.gate", scene="transport", n=31, tier=2,
        cyrillic="Како́й вы́ход на поса́дку?",
        transliteration="ka-KOY VY-khat na pa-SAT-ku",
        chinese="几号登机口？", literal="什么 出口 到 登机",
        politeness="neutral", register_note="过完安检",
        likely_responses=[
            {"cyrillic": "Вы́ход семь.", "trans": "VY-khat SYEM'", "cn": "7 号"},
        ],
    ),
    card(
        id="transport.flight.luggage", scene="transport", n=32, tier=3,
        cyrillic="Куда́ сдать бага́ж?",
        transliteration="ku-DA SDAT' ba-GAZH",
        chinese="行李在哪托运？", literal="到哪里 交付 行李",
        politeness="neutral", register_note="check-in 时分流",
        likely_responses=[
            {"cyrillic": "Сле́ва от стойки.",
             "trans": "SLYE-va at STOY-ki", "cn": "柜台左边"},
        ],
    ),
    # ---- 出租进阶 (3) ----
    card(
        id="transport.taxi.avoid_traffic", scene="transport", n=33, tier=3,
        cyrillic="Мо́жно объе́хать про́бку?",
        transliteration="MOZH-na ab-YE-khat' PROB-ku",
        chinese="能绕过堵车吗？", literal="可以 绕 堵车",
        politeness="neutral", register_note="赶时间时",
        likely_responses=[
            {"cyrillic": "Постара́юсь.", "trans": "pas-ta-RA-yus'", "cn": "我尽量"},
        ],
    ),
    card(
        id="transport.taxi.wait_minutes", scene="transport", n=34, tier=2,
        cyrillic="Подождёте пять мину́т?",
        transliteration="pa-dazh-DYO-tye PYAT' mi-NUT",
        chinese="能等我 5 分钟吗？", literal="您 等 五 分钟",
        politeness="Вы", register_note="临时下车买东西 / 上厕所",
        likely_responses=[
            {"cyrillic": "Хорошо́, я подожду́.",
             "trans": "kha-ra-SHO ya pa-dazh-DU", "cn": "好，我等"},
            {"cyrillic": "Счётчик пойдёт.",
             "trans": "SHCHO-chik pay-DYOT", "cn": "（表）会继续跳"},
        ],
    ),
    card(
        id="transport.taxi.stop_here_exact", scene="transport", n=35, tier=2,
        cyrillic="Здесь, пожа́луйста.",
        transliteration="ZDYES' pa-ZHA-lus-ta",
        chinese="（停）这里。", literal="这里 请",
        politeness="neutral", register_note="比'Останови́тесь здесь'更口语简短",
        likely_responses=[
            {"cyrillic": "Сюда́?", "trans": "syu-DA", "cn": "这里？"},
        ],
    ),
]


# ================================================================
# MONEY 增量 — 5 张（n=26-30）
# ================================================================
MONEY_EXT = [
    card(
        id="money.number.two_thousand", scene="money", n=26, tier=2,
        cyrillic="Две ты́сячи.", transliteration="DVYE TY-sya-chi",
        chinese="两千。", literal="二 (阴) 千 (复二)",
        politeness="neutral", register_note="UZ 价格常见单位——一份茶 / 公交票档位",
        likely_responses=[],
    ),
    card(
        id="money.number.five_thousand", scene="money", n=27, tier=2,
        cyrillic="Пять ты́сяч.", transliteration="PYAT' TY-syich",
        chinese="五千。", literal="五 千 (复二)",
        politeness="neutral", register_note="一袋小食 / 矿泉水",
        likely_responses=[],
    ),
    card(
        id="money.number.twenty_thousand", scene="money", n=28, tier=2,
        cyrillic="Два́дцать ты́сяч.",
        transliteration="DVA-tsat' TY-syich",
        chinese="两万。", literal="二十 千 (复二)",
        politeness="neutral", register_note="一份 plov 价位",
        likely_responses=[],
    ),
    card(
        id="money.number.fifty_thousand", scene="money", n=29, tier=2,
        cyrillic="Пятьдеся́т ты́сяч.",
        transliteration="pyat'-di-SYAT TY-syich",
        chinese="五万。", literal="五十 千 (复二)",
        politeness="neutral", register_note="餐厅人均价位",
        likely_responses=[],
    ),
    card(
        id="money.number.million", scene="money", n=30, tier=3,
        cyrillic="Миллио́н.", transliteration="mi-li-ON",
        chinese="（一）百万。", literal="百万",
        politeness="neutral", register_note="酒店一晚 / 大件礼物 / 总价",
        likely_responses=[],
        local_note="1 百万 sum ≈ 80 USD ≈ 580 RMB（按 2025 汇率）。",
    ),
]


NEW_CARDS = LODGING + SHOPPING + EMERGENCY + CHAT + FOOD_EXT + TRANSPORT_EXT + MONEY_EXT


def main() -> int:
    existing = json.loads(CARDS_PATH.read_text(encoding="utf-8"))
    existing_ids = {c["id"] for c in existing}

    to_add = [c for c in NEW_CARDS if c["id"] not in existing_ids]
    duplicates = [c["id"] for c in NEW_CARDS if c["id"] in existing_ids]

    if duplicates:
        print(f"⚠️ 跳过 {len(duplicates)} 张已存在的卡（按 id 比对）:")
        for d in duplicates[:5]:
            print(f"   {d}")

    combined = existing + to_add

    from collections import Counter
    scene_count = Counter(c["scene"] for c in combined)
    print("\n场景分布：")
    for s in ["essentials", "money", "transport", "food", "lodging", "shopping", "emergency", "chat"]:
        print(f"   {s:10s} {scene_count.get(s, 0):>3} 张")

    essential_count = sum(1 for c in combined if c.get("is_essential"))
    print(f"\nis_essential = true: {essential_count} 张（v2 不动 v1 的 10 张精选）")

    CARDS_PATH.write_text(
        json.dumps(combined, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"\n✓ 写入 {CARDS_PATH}（{len(existing)} → {len(combined)} 张，新增 {len(to_add)}）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
