#!/usr/bin/env python3
"""
功能：把 cards.json 从 W1 的 20 张扩到 v1 目标 100 张（4 场景 × 25）
输入：src/data/cards.json（含原有 20 张）
输出：src/data/cards.json（追加 80 张新卡后覆盖写回）
如何运行：python3 scripts/expand-cards-v1.py
依赖：标准库
在项目中的作用：v1 内容生产的一次性数据源。脚本本身就是这 80 张卡的"原稿"，
            commit 进仓库便于后续审校与追溯（哪条卡是怎么写出来的）。
            脚本是幂等的：再次运行不会重复添加同 id 的卡。

约定：
- id 格式：<scene>.<subcategory>.<short_id>
- 音频文件名：<scene>_NNNN_{normal|slow}.mp3，NNNN 从 0006 起逐张递增
- transliteration：发音式拉丁化，大写表重音
- verification_status：一律 ai_generated_unreviewed，不偷标 verified
- likely_responses：每张至少 1 条，反映真实场景下对方最可能说的话
- is_essential：跨 100 张精选 10 张钉顶（CLAUDE.md 约定）。
  本脚本内新增的 5 张精选：yes / no / slower_please / card_accepted / this_one。
  脚本运行后还需把原 20 张里 5 张降级：cheaper / how_much_to_center /
  stop_here / no_meat / water / check_please（保留 hello_formal / thank_you /
  sorry / dont_understand / how_much 不变）。最终 essential = 10。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CARDS_PATH = ROOT / "src" / "data" / "cards.json"


def audio_paths(scene: str, n: int) -> dict[str, str]:
    """生成约定的音频路径，N 从 1 起算（保证 0001-0025 与 0006-0025 一致）"""
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
    is_essential: bool,
    tier: int,
    cyrillic: str,
    transliteration: str,
    chinese: str,
    literal: str,
    politeness: str,
    register_note: str,
    likely_responses: list[dict[str, str]],
    slots: list[dict[str, str]] | None = None,
    local_note: str = "",
) -> dict[str, Any]:
    return {
        "id": id,
        "scene": scene,
        "is_essential": is_essential,
        "tier": tier,
        "cyrillic": cyrillic,
        "transliteration": transliteration,
        "chinese": chinese,
        "literal": literal,
        "audio": audio_paths(scene, n),
        "politeness": politeness,
        "register_note": register_note,
        "likely_responses": likely_responses,
        "slots": slots or [],
        "local_note": local_note,
        "verification_status": "ai_generated_unreviewed",
    }


# ================================================================
# ESSENTIALS — 20 张新卡（0006-0025）
# ================================================================
ESSENTIALS = [
    card(
        id="essentials.greeting.hello_informal", scene="essentials", n=6,
        is_essential=False, tier=2,
        cyrillic="Приве́т.", transliteration="pri-VYET",
        chinese="嗨。", literal="问候（亲近）",
        politeness="ты",
        register_note="对熟人 / 同龄人 / 年轻人；对陌生人或长辈用 Здра́вствуйте",
        likely_responses=[
            {"cyrillic": "Приве́т!", "trans": "pri-VYET", "cn": "嗨！"},
            {"cyrillic": "Здоро́во.", "trans": "zda-RO-va", "cn": "你好（更随意）"},
        ],
        local_note="塔什干年轻一代俄语母语者 + 乌兹别克族里都通用。不要对店员/出租车司机用——会显得不够尊重。",
    ),
    card(
        id="essentials.greeting.goodbye_formal", scene="essentials", n=7,
        is_essential=False, tier=1,
        cyrillic="До свида́ния.", transliteration="da svi-DA-ni-ya",
        chinese="再见。", literal="到 见面（再见）",
        politeness="Вы",
        register_note="标准告别，所有场景都不会错",
        likely_responses=[
            {"cyrillic": "До свида́ния.", "trans": "da svi-DA-ni-ya", "cn": "再见"},
            {"cyrillic": "Всего́ до́брого.", "trans": "fsi-VO DO-bra-va", "cn": "祝您一切顺利"},
        ],
    ),
    card(
        id="essentials.greeting.goodbye_informal", scene="essentials", n=8,
        is_essential=False, tier=2,
        cyrillic="Пока́.", transliteration="pa-KA",
        chinese="拜拜。", literal="再见（随意）",
        politeness="ты",
        register_note="对朋友 / 熟人；不要对店员或长辈用",
        likely_responses=[
            {"cyrillic": "Пока́!", "trans": "pa-KA", "cn": "拜！"},
            {"cyrillic": "Дава́й.", "trans": "da-VAY", "cn": "好的，回头见"},
        ],
    ),
    card(
        id="essentials.greeting.good_morning", scene="essentials", n=9,
        is_essential=False, tier=2,
        cyrillic="До́брое у́тро.", transliteration="DOB-ra-ye OO-tra",
        chinese="早上好。", literal="善良的 早晨",
        politeness="neutral",
        register_note="约到中午 11 点前用",
        likely_responses=[
            {"cyrillic": "До́брое у́тро.", "trans": "DOB-ra-ye OO-tra", "cn": "早上好"},
        ],
    ),
    card(
        id="essentials.greeting.good_day", scene="essentials", n=10,
        is_essential=False, tier=2,
        cyrillic="До́брый день.", transliteration="DOB-ry DYEN'",
        chinese="您好（白天通用）。", literal="善良的 白天",
        politeness="neutral",
        register_note="白天 11:00-18:00 最自然，写邮件开头也常用",
        likely_responses=[
            {"cyrillic": "До́брый день.", "trans": "DOB-ry DYEN'", "cn": "您好"},
        ],
    ),
    card(
        id="essentials.greeting.good_evening", scene="essentials", n=11,
        is_essential=False, tier=2,
        cyrillic="До́брый ве́чер.", transliteration="DOB-ry VYE-chir",
        chinese="晚上好。", literal="善良的 傍晚",
        politeness="neutral",
        register_note="约 18:00 之后用",
        likely_responses=[
            {"cyrillic": "До́брый ве́чер.", "trans": "DOB-ry VYE-chir", "cn": "晚上好"},
        ],
    ),
    card(
        id="essentials.basic.yes", scene="essentials", n=12,
        is_essential=True, tier=1,
        cyrillic="Да.", transliteration="DA",
        chinese="是。", literal="是",
        politeness="neutral",
        register_note="所有场合通用",
        likely_responses=[],
        local_note="听到 'Да-да' 不是答应两次，是表示'是是是、明白了'，类似中文里的'对对对'。",
    ),
    card(
        id="essentials.basic.no", scene="essentials", n=13,
        is_essential=True, tier=1,
        cyrillic="Нет.", transliteration="NYET",
        chinese="不。", literal="不",
        politeness="neutral",
        register_note="所有场合通用。比英语 'no' 略硬，但不算粗鲁",
        likely_responses=[],
    ),
    card(
        id="essentials.basic.please", scene="essentials", n=14,
        is_essential=False, tier=1,
        cyrillic="Пожа́луйста.", transliteration="pa-ZHA-lus-ta",
        chinese="请。 / 不客气。", literal="请 / 不客气（视语境）",
        politeness="neutral",
        register_note="既是'请'又是'不客气'——别人说 Спасибо 时回这个；提请求时也加这个",
        likely_responses=[],
        local_note="这是俄语最高频词之一。请求时贴在句尾、回应感谢时单独说。",
    ),
    card(
        id="essentials.basic.ok", scene="essentials", n=15,
        is_essential=False, tier=1,
        cyrillic="Хорошо́.", transliteration="kha-ra-SHO",
        chinese="好的。", literal="好",
        politeness="neutral",
        register_note="确认 / 答应；也表示对话推进",
        likely_responses=[],
    ),
    card(
        id="essentials.basic.i_dont_know", scene="essentials", n=16,
        is_essential=False, tier=1,
        cyrillic="Я не зна́ю.", transliteration="ya ni ZNA-yu",
        chinese="我不知道。", literal="我 不 知道",
        politeness="neutral",
        register_note="比 'Я не понима́ю'（我听不懂）适用更广——后者只针对'话没听懂'",
        likely_responses=[
            {"cyrillic": "Ничего́, спроси́те у него́.", "trans": "ni-chi-VO spra-SI-tye u ni-VO", "cn": "没关系，问问他"},
        ],
    ),
    card(
        id="essentials.courtesy.thank_you_very_much", scene="essentials", n=17,
        is_essential=False, tier=1,
        cyrillic="Большо́е спаси́бо.", transliteration="bal'-SHO-ye spa-SI-ba",
        chinese="非常感谢。", literal="大的 感谢",
        politeness="neutral",
        register_note="比单说 Спасибо 更郑重；适合表达真切谢意",
        likely_responses=[
            {"cyrillic": "Пожа́луйста.", "trans": "pa-ZHA-lus-ta", "cn": "不客气"},
            {"cyrillic": "Не за что.", "trans": "NYE za shta", "cn": "没什么"},
        ],
    ),
    card(
        id="essentials.communication.do_you_speak_english", scene="essentials", n=18,
        is_essential=False, tier=1,
        cyrillic="Вы говори́те по-англи́йски?",
        transliteration="vy ga-va-RI-tye pa-an-GLIY-ski",
        chinese="您会说英语吗？", literal="您 说 用-英语",
        politeness="Вы",
        register_note="对店员 / 服务员 / 司机的标准开场之二",
        likely_responses=[
            {"cyrillic": "Немно́го.", "trans": "nim-NO-ga", "cn": "一点点"},
            {"cyrillic": "Нет, не говорю́.", "trans": "NYET ni ga-va-RYU", "cn": "不，不会"},
            {"cyrillic": "Да, конечно.", "trans": "DA ka-NYESH-na", "cn": "会，当然"},
        ],
        local_note="塔什干年轻店员 + 大酒店前台多半会一点；街边小店 / 巴扎大概率不会。",
    ),
    card(
        id="essentials.communication.slower_please", scene="essentials", n=19,
        is_essential=True, tier=1,
        cyrillic="Поме́дленнее, пожа́луйста.",
        transliteration="pa-MYED-li-nye-ye pa-ZHA-lus-ta",
        chinese="请说慢一点。", literal="慢一点 请",
        politeness="neutral",
        register_note="对方语速太快时第一个救命句",
        likely_responses=[
            {"cyrillic": "Коне́чно.", "trans": "ka-NYESH-na", "cn": "当然"},
            {"cyrillic": "Извини́те.", "trans": "iz-vi-NI-tye", "cn": "抱歉"},
        ],
    ),
    card(
        id="essentials.communication.i_dont_speak_russian", scene="essentials", n=20,
        is_essential=False, tier=1,
        cyrillic="Я не говорю́ по-ру́сски.",
        transliteration="ya ni ga-va-RYU pa-RUS-ski",
        chinese="我不会说俄语。", literal="我 不 说 用-俄语",
        politeness="neutral",
        register_note="尴尬时刻的终结技。说完对方通常会切英语或找人帮忙",
        likely_responses=[
            {"cyrillic": "А по-англи́йски?", "trans": "a pa-an-GLIY-ski", "cn": "那英语呢？"},
            {"cyrillic": "Подожди́те.", "trans": "pa-dazh-DI-tye", "cn": "请稍等（去叫人）"},
        ],
    ),
    card(
        id="essentials.communication.write_it_down", scene="essentials", n=21,
        is_essential=False, tier=2,
        cyrillic="Напиши́те, пожа́луйста.",
        transliteration="na-pi-SHI-tye pa-ZHA-lus-ta",
        chinese="请写下来。", literal="写下 请",
        politeness="Вы",
        register_note="听不清数字 / 地名时用——尤其是价钱、地址",
        likely_responses=[
            {"cyrillic": "Хорошо́.", "trans": "kha-ra-SHO", "cn": "好的"},
        ],
        local_note="问价钱听不准时神器：店员会在小票背面或纸上写数字，毫无歧义。",
    ),
    card(
        id="essentials.communication.show_on_map", scene="essentials", n=22,
        is_essential=False, tier=2,
        cyrillic="Покажи́те на ка́рте, пожа́луйста.",
        transliteration="pa-ka-ZHI-tye na KAR-tye pa-ZHA-lus-ta",
        chinese="请在地图上指给我看。", literal="指给我看 在 地图 请",
        politeness="Вы",
        register_note="拿手机出来配合使用——比反复念地名快十倍",
        likely_responses=[
            {"cyrillic": "Сейча́с.", "trans": "si-CHAS", "cn": "马上"},
            {"cyrillic": "Вот здесь.", "trans": "VOT ZDYES'", "cn": "就这里"},
        ],
    ),
    card(
        id="essentials.identity.my_name_is", scene="essentials", n=23,
        is_essential=False, tier=2,
        cyrillic="Меня́ зову́т…", transliteration="mi-NYA za-VOOT",
        chinese="我叫…（我的名字是…）", literal="我 叫做",
        politeness="neutral",
        register_note="自我介绍标准句；后接你的名字",
        likely_responses=[
            {"cyrillic": "Очень прия́тно.", "trans": "O-chen' pri-YAT-na", "cn": "幸会"},
            {"cyrillic": "А меня́ … (Иван).", "trans": "a mi-NYA (i-VAN)", "cn": "我叫… (伊万)"},
        ],
        slots=[
            {"label": "（你的中文名）", "swap": "Меня́ зову́т Ли.", "trans": "mi-NYA za-VOOT LI"},
        ],
    ),
    card(
        id="essentials.identity.im_from_china", scene="essentials", n=24,
        is_essential=False, tier=2,
        cyrillic="Я из Кита́я.", transliteration="ya iz ki-TA-ya",
        chinese="我从中国来。", literal="我 从 中国",
        politeness="neutral",
        register_note="常见 small talk；店家 / 司机听到中国人很多都会主动聊几句",
        likely_responses=[
            {"cyrillic": "О, Кита́й! Добро́ пожа́ловать.", "trans": "O ki-TAY da-bro pa-ZHA-la-vat'", "cn": "哦，中国！欢迎"},
            {"cyrillic": "Из како́го го́рода?", "trans": "iz ka-KO-va GO-ra-da", "cn": "从哪个城市？"},
        ],
        local_note="乌兹别克斯坦人对中国人非常友好，因为'一带一路'近年来项目多。被问'из какого города' 准备好答案（например, Пеки́н, Шанха́й, Гуанчжо́у）。",
    ),
    card(
        id="essentials.identity.im_tourist", scene="essentials", n=25,
        is_essential=False, tier=3,
        cyrillic="Я тури́ст.", transliteration="ya tu-RIST",
        chinese="我是游客。", literal="我 游客",
        politeness="neutral",
        register_note="女性说 'Я тури́стка'（ya tu-RIST-ka）。被警察 / 海关 / 路人盘问身份时用",
        likely_responses=[
            {"cyrillic": "На́долго?", "trans": "NA-dal-ga", "cn": "待多久？"},
            {"cyrillic": "Како́й па́спорт?", "trans": "ka-KOY PAS-part", "cn": "什么护照？（哪国的）"},
        ],
    ),
]


# ================================================================
# MONEY — 20 张新卡（0006-0025）
# ================================================================
MONEY = [
    card(
        id="money.number.one", scene="money", n=6,
        is_essential=False, tier=1,
        cyrillic="Оди́н.", transliteration="a-DIN",
        chinese="一。", literal="一",
        politeness="neutral", register_note="阴性名词前用 одна́ (ad-NA)、中性 одно́ (ad-NO)",
        likely_responses=[],
        slots=[{"label": "阴性 (одна́)", "swap": "одна́ ча́шка", "trans": "ad-NA CHASH-ka"}],
    ),
    card(
        id="money.number.two", scene="money", n=7,
        is_essential=False, tier=1,
        cyrillic="Два.", transliteration="DVA",
        chinese="二。", literal="二",
        politeness="neutral",
        register_note="阴性前用 две (DVYE)，例如 две ты́сячи (两千)",
        likely_responses=[],
        slots=[{"label": "阴性 (две)", "swap": "две ты́сячи", "trans": "DVYE TY-sya-chi"}],
    ),
    card(
        id="money.number.three", scene="money", n=8,
        is_essential=False, tier=1,
        cyrillic="Три.", transliteration="TRI",
        chinese="三。", literal="三",
        politeness="neutral", register_note="数字通用，不分性",
        likely_responses=[],
    ),
    card(
        id="money.number.five", scene="money", n=9,
        is_essential=False, tier=1,
        cyrillic="Пять.", transliteration="PYAT'",
        chinese="五。", literal="五",
        politeness="neutral", register_note="5 及以上数字后名词用复数二格（пять су́мов / пять ты́сяч）",
        likely_responses=[],
    ),
    card(
        id="money.number.ten", scene="money", n=10,
        is_essential=False, tier=1,
        cyrillic="Де́сять.", transliteration="DYE-syit'",
        chinese="十。", literal="十",
        politeness="neutral", register_note="10",
        likely_responses=[],
    ),
    card(
        id="money.number.hundred", scene="money", n=11,
        is_essential=False, tier=1,
        cyrillic="Сто.", transliteration="STO",
        chinese="一百。", literal="百",
        politeness="neutral", register_note="100",
        likely_responses=[],
    ),
    card(
        id="money.number.thousand", scene="money", n=12,
        is_essential=False, tier=1,
        cyrillic="Ты́сяча.", transliteration="TY-sya-cha",
        chinese="一千。", literal="千",
        politeness="neutral",
        register_note="UZ 物价基本单位——千以下几乎没意义",
        likely_responses=[],
        local_note="1000 sum ≈ 0.08 USD ≈ 0.6 RMB。所以咖啡 20000 = 1.6 USD ≈ 12 RMB。",
    ),
    card(
        id="money.number.ten_thousand", scene="money", n=13,
        is_essential=False, tier=1,
        cyrillic="Де́сять ты́сяч.", transliteration="DYE-syit' TY-syich",
        chinese="一万。", literal="十 千",
        politeness="neutral",
        register_note="UZ 一顿便餐价位 30-50 千；几万 = 几顿饭",
        likely_responses=[],
        local_note="十万 = сто ты́сяч (STO TY-syich)；百万 = миллио́н (mi-li-ON)。",
    ),
    card(
        id="money.number.hundred_thousand", scene="money", n=14,
        is_essential=False, tier=2,
        cyrillic="Сто ты́сяч.", transliteration="STO TY-syich",
        chinese="十万。", literal="百 千",
        politeness="neutral",
        register_note="UZ 中档酒店一晚价位常落在这个区间（100k-300k sum）",
        likely_responses=[],
    ),
    card(
        id="money.payment.card_or_cash", scene="money", n=15,
        is_essential=False, tier=1,
        cyrillic="Ка́ртой и́ли нали́чными?",
        transliteration="KAR-tay I-li na-LICH-ny-mi",
        chinese="刷卡还是现金？", literal="用卡 或者 用现金",
        politeness="neutral",
        register_note="这是 *对方* 问你的话——你听清楚回答就行",
        likely_responses=[
            {"cyrillic": "Ка́ртой.", "trans": "KAR-tay", "cn": "刷卡"},
            {"cyrillic": "Нали́чными.", "trans": "na-LICH-ny-mi", "cn": "现金"},
        ],
        local_note="UZ 商家分两种：能刷卡的（购物中心、餐厅）和只收现金的（巴扎、街边小摊、出租）。",
    ),
    card(
        id="money.payment.cash", scene="money", n=16,
        is_essential=False, tier=1,
        cyrillic="Нали́чными.", transliteration="na-LICH-ny-mi",
        chinese="现金。", literal="用现金",
        politeness="neutral", register_note="单字回答付款方式",
        likely_responses=[],
    ),
    card(
        id="money.payment.by_card", scene="money", n=17,
        is_essential=False, tier=1,
        cyrillic="Ка́ртой.", transliteration="KAR-tay",
        chinese="刷卡。", literal="用卡",
        politeness="neutral", register_note="单字回答付款方式",
        likely_responses=[],
    ),
    card(
        id="money.payment.card_accepted", scene="money", n=18,
        is_essential=True, tier=1,
        cyrillic="Ка́ртой мо́жно?", transliteration="KAR-tay MOZH-na",
        chinese="可以刷卡吗？", literal="用卡 可以？",
        politeness="neutral", register_note="进店 / 上车前确认能否刷卡。能省一次找现金的麻烦",
        likely_responses=[
            {"cyrillic": "Да, мо́жно.", "trans": "DA MOZH-na", "cn": "可以"},
            {"cyrillic": "Нет, то́лько нали́чные.", "trans": "NYET TOL'-ka na-LICH-ny-ye", "cn": "不行，只收现金"},
        ],
        local_note="塔什干主流连锁店都接 Visa / Mastercard；银联在大商场可用，但小店少；UnionPay 在 ATM 比 POS 普及。",
    ),
    card(
        id="money.payment.terminal_broken", scene="money", n=19,
        is_essential=False, tier=2,
        cyrillic="Термина́л не рабо́тает.",
        transliteration="tir-mi-NAL ni ra-BO-ta-yit",
        chinese="刷卡机坏了。", literal="终端 不 工作",
        politeness="neutral",
        register_note="这是 *对方* 可能说的话——表示刷卡不通，得付现金",
        likely_responses=[
            {"cyrillic": "Есть ли банкома́т ря́дом?", "trans": "YEST' li ban-ka-MAT RYA-dam", "cn": "附近有 ATM 吗？（这是你问回去的）"},
        ],
        local_note="UZ 网络偶尔抽风、银行系统卡顿是常事。备好现金。",
    ),
    card(
        id="money.transaction.give_change", scene="money", n=20,
        is_essential=False, tier=2,
        cyrillic="Да́йте сда́чу, пожа́луйста.",
        transliteration="DAY-tye SDA-chu pa-ZHA-lus-ta",
        chinese="请找零给我。", literal="给 找零 请",
        politeness="Вы",
        register_note="店家忘了找零或拖时间时礼貌提醒",
        likely_responses=[
            {"cyrillic": "Извини́те, сейча́с.", "trans": "iz-vi-NI-tye si-CHAS", "cn": "不好意思，马上"},
        ],
    ),
    card(
        id="money.transaction.no_change", scene="money", n=21,
        is_essential=False, tier=2,
        cyrillic="Сда́чи нет.", transliteration="SDA-chi NYET",
        chinese="没有零钱（找不开）。", literal="零钱 不 (无)",
        politeness="neutral",
        register_note="这是 *对方* 可能说的话——他没零钱找你。需要换张小额或直接付正好",
        likely_responses=[
            {"cyrillic": "Хорошо́, у меня́ есть поме́льче.",
             "trans": "kha-ra-SHO u mi-NYA YEST' pa-MYEL'-che",
             "cn": "好的，我有小额（你回答）"},
        ],
        local_note="UZ 出租 / 巴扎常缺零钱，10 万的整票拍出去对方很可能没的找。尽量备 5k / 10k / 20k 小额。",
    ),
    card(
        id="money.exchange.dollar_rate", scene="money", n=22,
        is_essential=False, tier=2,
        cyrillic="Како́й курс до́ллара?",
        transliteration="ka-KOY KURS DO-la-ra",
        chinese="美元汇率是多少？", literal="什么样的 汇率 美元",
        politeness="neutral", register_note="在 обмен валют (兑换点) 问汇率",
        likely_responses=[
            {"cyrillic": "Двена́дцать ты́сяч пятьсо́т.",
             "trans": "dvi-NA-tsat' TY-syich pyat'-SOT", "cn": "12500"},
            {"cyrillic": "Сего́дня по двена́дцать.",
             "trans": "si-VOD-nya pa dvi-NA-tsat'", "cn": "今天是 12 千"},
        ],
        local_note="1 USD ≈ 12,500-12,800 UZS（2024-2025 年波动区间）。大兑换点 vs 银行汇率差 1-2%。",
    ),
    card(
        id="money.exchange.atm_where", scene="money", n=23,
        is_essential=False, tier=2,
        cyrillic="Где банкома́т?", transliteration="gdye ban-ka-MAT",
        chinese="取款机在哪？", literal="哪里 ATM",
        politeness="neutral", register_note="问路 ATM",
        likely_responses=[
            {"cyrillic": "Вон там.", "trans": "VON TAM", "cn": "那边"},
            {"cyrillic": "В ТЦ напро́тив.", "trans": "v TE-TSE na-PRO-tif", "cn": "对面商场里"},
        ],
        local_note="Kapitalbank / Asaka Bank 的 ATM 接受国际卡 + 银联。Hamkorbank 也很多。",
    ),
    card(
        id="money.payment.receipt", scene="money", n=24,
        is_essential=False, tier=2,
        cyrillic="Чек, пожа́луйста.", transliteration="CHEK pa-ZHA-lus-ta",
        chinese="请给我收据。", literal="收据 请",
        politeness="neutral", register_note="餐厅 / 商店都通用",
        likely_responses=[
            {"cyrillic": "Сейча́с.", "trans": "si-CHAS", "cn": "马上"},
        ],
    ),
    card(
        id="money.bargain.discount", scene="money", n=25,
        is_essential=False, tier=2,
        cyrillic="Ски́дка есть?", transliteration="SKID-ka YEST'",
        chinese="有折扣吗？", literal="折扣 有？",
        politeness="neutral", register_note="巴扎 / 小店议价标准开场",
        likely_responses=[
            {"cyrillic": "Пять проце́нтов.", "trans": "PYAT' pra-TSEN-taf", "cn": "5%"},
            {"cyrillic": "Для вас — да.", "trans": "dlya VAS — DA", "cn": "对您当然有"},
            {"cyrillic": "Нет, цена́ фикси́рованная.", "trans": "NYET tsi-NA fik-SI-ra-van-na-ya", "cn": "没有，标价定的"},
        ],
        local_note="超市 / 大店一般没折扣；巴扎 / 纪念品店期望砍 10-30%。",
    ),
]


# ================================================================
# TRANSPORT — 20 张新卡（0006-0025）
# ================================================================
TRANSPORT = [
    card(
        id="transport.taxi.yandex_ordered", scene="transport", n=6,
        is_essential=False, tier=2,
        cyrillic="Я заказа́л Я́ндекс.",
        transliteration="ya za-ka-ZAL YAN-deks",
        chinese="我叫了 Yandex。", literal="我 叫了 Yandex",
        politeness="neutral",
        register_note="女性说 заказа́ла (za-ka-ZA-la)。给司机确认订单",
        likely_responses=[
            {"cyrillic": "Хорошо́, выезжа́ю.", "trans": "kha-ra-SHO vy-ye-ZHA-yu", "cn": "好的，出发了"},
            {"cyrillic": "Вы где?", "trans": "vy GDYE", "cn": "您在哪？"},
        ],
        local_note="Yandex Go 是 UZ 出行第一选择：透明定价、应用打车、流程类比国内滴滴。",
    ),
    card(
        id="transport.taxi.where_are_you", scene="transport", n=7,
        is_essential=False, tier=2,
        cyrillic="Вы где?", transliteration="vy GDYE",
        chinese="您在哪？", literal="您 哪里",
        politeness="Вы",
        register_note="电话联系司机时高频；也可对方先这样问你",
        likely_responses=[
            {"cyrillic": "Я на ме́сте.", "trans": "ya na MYES-tye", "cn": "我到位了"},
            {"cyrillic": "Подожди́те 2 мину́ты.", "trans": "pa-dazh-DI-tye DVYE mi-NU-ty", "cn": "请等 2 分钟"},
        ],
    ),
    card(
        id="transport.taxi.im_outside", scene="transport", n=8,
        is_essential=False, tier=2,
        cyrillic="Я на у́лице.", transliteration="ya na OO-li-tse",
        chinese="我在路边。", literal="我 在 街道",
        politeness="neutral", register_note="告诉司机你在外面等",
        likely_responses=[
            {"cyrillic": "Понял.", "trans": "PO-nyal", "cn": "明白"},
        ],
    ),
    card(
        id="transport.taxi.wait_a_minute", scene="transport", n=9,
        is_essential=False, tier=2,
        cyrillic="Подожди́те мину́ту, пожа́луйста.",
        transliteration="pa-dazh-DI-tye mi-NU-tu pa-ZHA-lus-ta",
        chinese="请等一下。", literal="请等 一分钟 请",
        politeness="Вы", register_note="去店里取东西、临时下车前用",
        likely_responses=[
            {"cyrillic": "Хорошо́.", "trans": "kha-ra-SHO", "cn": "好的"},
        ],
    ),
    card(
        id="transport.taxi.faster", scene="transport", n=10,
        is_essential=False, tier=3,
        cyrillic="Побыстре́е, пожа́луйста.",
        transliteration="pa-by-STRE-ye pa-ZHA-lus-ta",
        chinese="请快一点。", literal="快一点 请",
        politeness="neutral",
        register_note="赶时间时使用；不要在司机有交通限制时强求",
        likely_responses=[
            {"cyrillic": "Стара́юсь.", "trans": "sta-RA-yus'", "cn": "我尽量"},
            {"cyrillic": "Про́бки.", "trans": "PROB-ki", "cn": "堵车"},
        ],
    ),
    card(
        id="transport.direction.straight", scene="transport", n=11,
        is_essential=False, tier=2,
        cyrillic="Пря́мо.", transliteration="PRYA-ma",
        chinese="直走。", literal="直",
        politeness="neutral", register_note="指路单字答案",
        likely_responses=[],
    ),
    card(
        id="transport.direction.left", scene="transport", n=12,
        is_essential=False, tier=2,
        cyrillic="Нале́во.", transliteration="na-LYE-va",
        chinese="（往）左。", literal="向左",
        politeness="neutral", register_note="指路 / 提示司机转向",
        likely_responses=[],
    ),
    card(
        id="transport.direction.right", scene="transport", n=13,
        is_essential=False, tier=2,
        cyrillic="Напра́во.", transliteration="na-PRA-va",
        chinese="（往）右。", literal="向右",
        politeness="neutral", register_note="指路 / 提示司机转向",
        likely_responses=[],
    ),
    card(
        id="transport.direction.turn_back", scene="transport", n=14,
        is_essential=False, tier=3,
        cyrillic="Обра́тно.", transliteration="a-BRAT-na",
        chinese="掉头 / 回去。", literal="返回",
        politeness="neutral", register_note="导航出错时让司机调头",
        likely_responses=[
            {"cyrillic": "Здесь нельзя́.", "trans": "ZDYES' nel'-ZYA", "cn": "这里不能（调头）"},
        ],
    ),
    card(
        id="transport.metro.which_station", scene="transport", n=15,
        is_essential=False, tier=2,
        cyrillic="Кака́я э́то ста́нция?",
        transliteration="ka-KA-ya E-ta STAN-tsi-ya",
        chinese="这是哪一站？", literal="什么样的 这 站",
        politeness="neutral", register_note="塔什干地铁站名俄文 + 乌兹别克文并行；问邻座最快",
        likely_responses=[
            {"cyrillic": "Это «Чи́ланзар».", "trans": "E-ta chi-lan-ZAR", "cn": "这是 Chilanzar 站"},
        ],
        local_note="塔什干地铁本身是苏联时代的杰作，每站装饰各不相同；很多本地人喜欢拍照。",
    ),
    card(
        id="transport.metro.next_station", scene="transport", n=16,
        is_essential=False, tier=2,
        cyrillic="Сле́дующая остано́вка кака́я?",
        transliteration="SLYE-du-yu-shcha-ya as-ta-NOV-ka ka-KA-ya",
        chinese="下一站是哪？", literal="下一个 站 什么样的",
        politeness="neutral", register_note="地铁、公交都通用",
        likely_responses=[
            {"cyrillic": "«Ми́нг урик».", "trans": "MING u-RIK", "cn": "Ming Urik 站"},
        ],
    ),
    card(
        id="transport.metro.transfer", scene="transport", n=17,
        is_essential=False, tier=2,
        cyrillic="Где переса́дка?",
        transliteration="gdye pi-ri-SAD-ka",
        chinese="哪里换乘？", literal="哪里 换乘",
        politeness="neutral", register_note="地铁换线 / 公交换车都用",
        likely_responses=[
            {"cyrillic": "На сле́дующей.", "trans": "na SLYE-du-yu-shchey", "cn": "下一站"},
            {"cyrillic": "Здесь, иди́те за указа́телем.",
             "trans": "ZDYES' i-DI-tye za u-ka-ZA-ti-lem", "cn": "这里，跟着指示牌走"},
        ],
    ),
    card(
        id="transport.transit.this_bus_to", scene="transport", n=18,
        is_essential=False, tier=2,
        cyrillic="Этот авто́бус идёт до Чорсу́?",
        transliteration="E-tat af-TO-bus i-DYOT da char-SU",
        chinese="这趟车到 Chorsu 吗？", literal="这 公交 走 到 Chorsu",
        politeness="neutral", register_note="上车前对司机或站台路人快问",
        likely_responses=[
            {"cyrillic": "Да, идёт.", "trans": "DA i-DYOT", "cn": "对，到的"},
            {"cyrillic": "Нет, друго́й.", "trans": "NYET dru-GOY", "cn": "不，下一趟"},
        ],
        slots=[
            {"label": "（你要去的目的地）", "swap": "до а́эропо́рта", "trans": "da a-e-ra-POR-ta"},
            {"label": "到火车站", "swap": "до вокза́ла", "trans": "da vak-ZA-la"},
        ],
        local_note="塔什干公交 + marshrutka 单程 ≈ 2000 sum，比出租便宜很多但需要懂路线。Google Maps 在 UZ 公交查询有时不全。",
    ),
    card(
        id="transport.transit.marshrutka_to", scene="transport", n=19,
        is_essential=False, tier=2,
        cyrillic="Маршру́тка до ры́нка?",
        transliteration="mar-SHRUT-ka da RYN-ka",
        chinese="Marshrutka（小巴）到市场吗？", literal="小巴 到 市场",
        politeness="neutral",
        register_note="Marshrutka 是 9-15 座小巴，路线固定但站点随意",
        likely_responses=[
            {"cyrillic": "Да, сади́тесь.", "trans": "DA sa-DI-tyes'", "cn": "是的，上来"},
            {"cyrillic": "Нет, мы идём в центр.", "trans": "NYET my i-DYOM v TSENTR", "cn": "不，我们去市中心"},
        ],
        local_note="向司机交钱，价格写在车窗上，3000-5000 sum 不等。挥手即停。",
    ),
    card(
        id="transport.transit.train_station", scene="transport", n=20,
        is_essential=False, tier=2,
        cyrillic="Где вокза́л?", transliteration="gdye vak-ZAL",
        chinese="火车站在哪？", literal="哪里 火车站",
        politeness="neutral", register_note="塔什干站叫 «Ташке́нт Северный»",
        likely_responses=[
            {"cyrillic": "Се́верный или Ю́жный?",
             "trans": "SYE-vir-ny I-li YUZH-ny", "cn": "北站还是南站？"},
        ],
        local_note="去撒马尔罕 / 布哈拉的 Afrosiyob 高铁就在北站发车；提前 30 分钟到 + 过安检。",
    ),
    card(
        id="transport.distance.how_long", scene="transport", n=21,
        is_essential=False, tier=2,
        cyrillic="Ско́лько е́хать?",
        transliteration="SKOL'-ka YE-khat'",
        chinese="要多久？", literal="多少 走（车程）",
        politeness="neutral", register_note="问到目的地大概要多少分钟 / 小时",
        likely_responses=[
            {"cyrillic": "Мину́т два́дцать.", "trans": "mi-NUT DVA-tsat'", "cn": "大概 20 分钟"},
            {"cyrillic": "Час.", "trans": "CHAS", "cn": "一小时"},
        ],
    ),
    card(
        id="transport.distance.is_it_far", scene="transport", n=22,
        is_essential=False, tier=2,
        cyrillic="Это далеко́?", transliteration="E-ta da-li-KO",
        chinese="（这）远吗？", literal="这 远？",
        politeness="neutral", register_note="决定走路还是叫车前问一下",
        likely_responses=[
            {"cyrillic": "Нет, пять мину́т пешко́м.",
             "trans": "NYET PYAT' mi-NUT pyish-KOM", "cn": "不远，走 5 分钟"},
            {"cyrillic": "Да, далеко́. Возьми́те такси́.",
             "trans": "DA da-li-KO vaz'-MI-tye tak-SI", "cn": "远，叫出租吧"},
        ],
    ),
    card(
        id="transport.address.by_this_address", scene="transport", n=23,
        is_essential=False, tier=2,
        cyrillic="По э́тому а́дресу, пожа́луйста.",
        transliteration="pa E-ta-mu A-dri-su pa-ZHA-lus-ta",
        chinese="请按这个地址走。", literal="按 这个 地址 请",
        politeness="Вы",
        register_note="给司机看手机屏幕上的地址 / Google Maps 标点时配合用",
        likely_responses=[
            {"cyrillic": "Понял.", "trans": "PO-nyal", "cn": "明白"},
        ],
    ),
    card(
        id="transport.misc.lost", scene="transport", n=24,
        is_essential=False, tier=3,
        cyrillic="Я заблуди́лся.",
        transliteration="ya za-blu-DIL-sya",
        chinese="我迷路了。", literal="我 迷路了",
        politeness="neutral",
        register_note="女性说 заблуди́лась (za-blu-DI-las')。求助路人 / 警察",
        likely_responses=[
            {"cyrillic": "Куда́ вам ну́жно?", "trans": "ku-DA vam NUZH-na", "cn": "您要去哪里？"},
        ],
    ),
    card(
        id="transport.taxi.give_back_change", scene="transport", n=25,
        is_essential=False, tier=2,
        cyrillic="Сда́чу, пожа́луйста.",
        transliteration="SDA-chu pa-ZHA-lus-ta",
        chinese="请找零给我。", literal="找零 请",
        politeness="neutral", register_note="付车费时礼貌索回零钱",
        likely_responses=[
            {"cyrillic": "Сейча́с.", "trans": "si-CHAS", "cn": "马上"},
            {"cyrillic": "У меня́ нет сда́чи.",
             "trans": "u mi-NYA NYET SDA-chi", "cn": "我没有零钱"},
        ],
        local_note="街边出租司机有时'忘'找零，主动开口要回——Yandex Go 自动结算就没这问题。",
    ),
]


# ================================================================
# FOOD — 20 张新卡（0006-0025）
# ================================================================
FOOD = [
    card(
        id="food.order.what_recommend", scene="food", n=6,
        is_essential=False, tier=2,
        cyrillic="Что посове́туете?",
        transliteration="SHTO pa-sa-VYE-tu-ye-tye",
        chinese="您推荐什么？", literal="什么 您建议",
        politeness="Вы",
        register_note="陌生餐厅破冰万能句；店家通常会推招牌菜",
        likely_responses=[
            {"cyrillic": "Попро́буйте плов.", "trans": "pa-PRO-buy-tye PLOF", "cn": "尝尝抓饭"},
            {"cyrillic": "Шашлы́к у нас лу́чший.",
             "trans": "shash-LYK u nas LUTCH-shiy", "cn": "我们的烤串最好"},
        ],
    ),
    card(
        id="food.order.this_one", scene="food", n=7,
        is_essential=True, tier=1,
        cyrillic="Это, пожа́луйста.",
        transliteration="E-ta pa-ZHA-lus-ta",
        chinese="（指给店员看）这个，谢谢。", literal="这 请",
        politeness="neutral",
        register_note="菜单看不懂时的万能技：手指 + 这句 = 一道菜",
        likely_responses=[
            {"cyrillic": "Хорошо́.", "trans": "kha-ra-SHO", "cn": "好的"},
            {"cyrillic": "С чем?", "trans": "s CHEM", "cn": "配什么？"},
        ],
    ),
    card(
        id="food.order.same", scene="food", n=8,
        is_essential=False, tier=2,
        cyrillic="То же са́мое.",
        transliteration="TO zhe SA-ma-ye",
        chinese="一样的（同上一位）。", literal="同 自己",
        politeness="neutral", register_note="对邻桌点的菜眼馋时——服务员秒懂",
        likely_responses=[
            {"cyrillic": "Хорошо́.", "trans": "kha-ra-SHO", "cn": "好"},
        ],
    ),
    card(
        id="food.order.one_more", scene="food", n=9,
        is_essential=False, tier=2,
        cyrillic="Ещё оди́н, пожа́луйста.",
        transliteration="yi-SHCHO a-DIN pa-ZHA-lus-ta",
        chinese="再来一个。", literal="还 一个 请",
        politeness="neutral", register_note="加单",
        likely_responses=[
            {"cyrillic": "То́чно?", "trans": "TOCH-na", "cn": "确定？"},
            {"cyrillic": "Хорошо́.", "trans": "kha-ra-SHO", "cn": "好"},
        ],
        slots=[
            {"label": "再来一杯（茶）", "swap": "ещё одну́ ча́шку ча́я", "trans": "yi-SHCHO ad-NU CHASH-ku CHA-ya"},
        ],
    ),
    card(
        id="food.order.takeaway", scene="food", n=10,
        is_essential=False, tier=2,
        cyrillic="С собо́й.", transliteration="s sa-BOY",
        chinese="带走。", literal="跟 自己（外带）",
        politeness="neutral", register_note="对'Здесь и́ли с собо́й?'的标准回答",
        likely_responses=[],
    ),
    card(
        id="food.order.for_here", scene="food", n=11,
        is_essential=False, tier=2,
        cyrillic="Здесь.", transliteration="ZDYES'",
        chinese="（在）这里（吃）。", literal="这里",
        politeness="neutral", register_note="同上对应'堂食'",
        likely_responses=[],
    ),
    card(
        id="food.diet.vegetarian", scene="food", n=12,
        is_essential=False, tier=2,
        cyrillic="Я вегетариа́нец.",
        transliteration="ya vi-gi-ta-ri-A-nits",
        chinese="我吃素。", literal="我 素食者",
        politeness="neutral",
        register_note="女性说 вегетариа́нка (vi-gi-ta-ri-AN-ka)。但在 UZ 严格素食难落地",
        likely_responses=[
            {"cyrillic": "Без мя́са?", "trans": "bez MYA-sa", "cn": "不要肉？"},
            {"cyrillic": "У нас есть овощно́е.",
             "trans": "u nas YEST' a-vash-NO-ye", "cn": "我们有素菜"},
        ],
        local_note="UZ 饮食以肉为主：plov 含羊肉、shashlyk 是烤肉串。素食可选：lagman 蔬菜版、salad、bread + cheese。",
    ),
    card(
        id="food.diet.no_pork", scene="food", n=13,
        is_essential=False, tier=3,
        cyrillic="Я не ем свини́ну.",
        transliteration="ya ni YEM svi-NI-nu",
        chinese="我不吃猪肉。", literal="我 不 吃 猪肉",
        politeness="neutral",
        register_note="UZ 是穆斯林国家、餐厅基本无猪肉。但有俄罗斯族餐厅会有",
        likely_responses=[
            {"cyrillic": "У нас нет.", "trans": "u nas NYET", "cn": "我们没有"},
        ],
    ),
    card(
        id="food.diet.no_alcohol", scene="food", n=14,
        is_essential=False, tier=3,
        cyrillic="Без алкого́ля.",
        transliteration="bez al-ka-GO-lya",
        chinese="不要酒精。", literal="不带 酒精",
        politeness="neutral", register_note="点带料理酒的菜时声明、或拒绝劝酒",
        likely_responses=[
            {"cyrillic": "Хорошо́, понял.", "trans": "kha-ra-SHO PO-nyal", "cn": "好的，明白"},
        ],
    ),
    card(
        id="food.taste.delicious", scene="food", n=15,
        is_essential=False, tier=2,
        cyrillic="Очень вку́сно.",
        transliteration="O-chen' FKUS-na",
        chinese="真好吃。", literal="非常 好吃",
        politeness="neutral", register_note="对厨师 / 老板 / 招呼员的最佳礼貌反馈",
        likely_responses=[
            {"cyrillic": "Спаси́бо!", "trans": "spa-SI-ba", "cn": "谢谢！"},
            {"cyrillic": "На здоро́вье.", "trans": "na zda-RO-vye", "cn": "请慢用"},
        ],
        local_note="家庭餐厅尤其受用——可能换来一道送的菜或一杯茶。",
    ),
    card(
        id="food.drink.tea", scene="food", n=16,
        is_essential=False, tier=1,
        cyrillic="Чай, пожа́луйста.",
        transliteration="CHAY pa-ZHA-lus-ta",
        chinese="（请来）一杯茶。", literal="茶 请",
        politeness="neutral", register_note="UZ 茶文化深厚——餐前 / 餐后必上",
        likely_responses=[
            {"cyrillic": "Чёрный и́ли зелёный?",
             "trans": "CHYOR-ny I-li zi-LYO-ny", "cn": "红茶还是绿茶？"},
        ],
        local_note="UZ 默认绿茶 (зелёный)，跟饺子 / plov 一起喝。红茶 (чёрный) 是俄罗斯式，看店主民族选择。",
    ),
    card(
        id="food.drink.coffee", scene="food", n=17,
        is_essential=False, tier=2,
        cyrillic="Кофе, пожа́луйста.",
        transliteration="KO-fye pa-ZHA-lus-ta",
        chinese="（请来）一杯咖啡。", literal="咖啡 请",
        politeness="neutral", register_note="咖啡馆点单",
        likely_responses=[
            {"cyrillic": "Эспре́ссо и́ли америка́но?",
             "trans": "es-PRES-sa I-li a-mi-ri-KA-na", "cn": "Espresso 还是 Americano？"},
        ],
        local_note="塔什干年轻人开了不少独立咖啡馆，意式咖啡品质不输莫斯科。",
    ),
    card(
        id="food.local.plov", scene="food", n=18,
        is_essential=False, tier=1,
        cyrillic="Я бу́ду плов.",
        transliteration="ya BU-du PLOF",
        chinese="我要抓饭（plov）。", literal="我 将 plov",
        politeness="neutral",
        register_note="UZ 国菜——羊肉 / 牛肉 + 胡萝卜 + 米饭 + 葡萄干，香辛",
        likely_responses=[
            {"cyrillic": "С чем — мя́со и́ли о́вощи?",
             "trans": "s CHEM — MYA-sa I-li O-va-shchi", "cn": "什么口味——肉的还是素的？"},
            {"cyrillic": "Принесём.", "trans": "pri-ni-SYOM", "cn": "上菜"},
        ],
        local_note="正宗 plov 来自塔什干 Central Asian Plov Centre（Беш Қозон，Besh Qozon）——巨锅现炒。",
    ),
    card(
        id="food.local.shashlik", scene="food", n=19,
        is_essential=False, tier=2,
        cyrillic="Шашлы́к, пожа́луйста.",
        transliteration="shash-LYK pa-ZHA-lus-ta",
        chinese="请来烤肉串。", literal="烤串 请",
        politeness="neutral", register_note="中亚 BBQ 串——羊肉 / 鸡肉 / 牛肉",
        likely_responses=[
            {"cyrillic": "Из бара́нины или ку́рицы?",
             "trans": "iz ba-RA-ni-ny I-li KU-ri-tsy", "cn": "羊肉的还是鸡肉的？"},
        ],
        local_note="UZ shashlyk 通常配 lepyoshka（饼）+ 洋葱片 + 醋。点 4-5 串一人足够。",
    ),
    card(
        id="food.local.samsa", scene="food", n=20,
        is_essential=False, tier=2,
        cyrillic="Самсу́ с мя́сом, пожа́луйста.",
        transliteration="sam-SU s MYA-sam pa-ZHA-lus-ta",
        chinese="请来个肉馅 samsa。", literal="samsa 跟 肉 请",
        politeness="neutral", register_note="UZ 街头烤包子——馅有羊肉 / 南瓜 / 土豆",
        likely_responses=[
            {"cyrillic": "Горя́чая, осторо́жно.",
             "trans": "ga-RYA-cha-ya as-ta-ROZH-na", "cn": "烫的，小心"},
        ],
        local_note="街头小摊 5000-10000 sum 一个，巨好吃；中午饭点排队。",
    ),
    card(
        id="food.local.lepyoshka", scene="food", n=21,
        is_essential=False, tier=2,
        cyrillic="Одну́ лепёшку, пожа́луйста.",
        transliteration="ad-NU li-PYOSH-ku pa-ZHA-lus-ta",
        chinese="（请来）一个烤饼。", literal="一个 (阴) 饼 请",
        politeness="neutral",
        register_note="圆形扁面包，每餐都有；巴扎现烤 + 现卖",
        likely_responses=[
            {"cyrillic": "Сейча́с пе́кутся.", "trans": "si-CHAS PYE-kut-sya", "cn": "正在烤"},
        ],
        local_note="UZ 文化禁忌：lepyoshka 不能扣放在桌子上（视为不敬），不能踩 / 扔。买完装进袋子里。",
    ),
    card(
        id="food.complain.cold", scene="food", n=22,
        is_essential=False, tier=3,
        cyrillic="Это холо́дное.",
        transliteration="E-ta kha-LOD-na-ye",
        chinese="这个是凉的。", literal="这 凉的",
        politeness="neutral", register_note="温和投诉——通常店家会帮你换热的",
        likely_responses=[
            {"cyrillic": "Извини́те, заме́ню.",
             "trans": "iz-vi-NI-tye za-MYE-nyu", "cn": "抱歉，给您换"},
        ],
    ),
    card(
        id="food.complain.wrong_order", scene="food", n=23,
        is_essential=False, tier=3,
        cyrillic="Это не моё.",
        transliteration="E-ta ni ma-YO",
        chinese="这不是我点的。", literal="这 不 我的",
        politeness="neutral", register_note="比'这不是我点的'完整句更简短自然",
        likely_responses=[
            {"cyrillic": "Извини́те, сейча́с принесу́.",
             "trans": "iz-vi-NI-tye si-CHAS pri-ni-SU", "cn": "抱歉，马上拿（您的）来"},
        ],
    ),
    card(
        id="food.pay.split", scene="food", n=24,
        is_essential=False, tier=3,
        cyrillic="Разде́льно, пожа́луйста.",
        transliteration="raz-DYEL'-na pa-ZHA-lus-ta",
        chinese="请分开结账。", literal="分别地 请",
        politeness="neutral", register_note="UZ 餐厅大多默认一桌一单——主动说才会分单",
        likely_responses=[
            {"cyrillic": "Хорошо́, кто что брал?",
             "trans": "kha-ra-SHO KTO SHTO BRAL", "cn": "好，谁吃了什么？"},
        ],
    ),
    card(
        id="food.pay.tip", scene="food", n=25,
        is_essential=False, tier=3,
        cyrillic="Сда́чи не на́до.",
        transliteration="SDA-chi ni NA-da",
        chinese="不用找零（留小费）。", literal="找零 不 需要",
        politeness="neutral",
        register_note="留小费的优雅说法——把零钱给服务员当小费",
        likely_responses=[
            {"cyrillic": "Спаси́бо большо́е!",
             "trans": "spa-SI-ba bal'-SHO-ye", "cn": "非常感谢！"},
        ],
        local_note="UZ 不强制小费——账单上常含 'service' 10%。如果没收，整桌饭额外 5-10% 是受欢迎的。",
    ),
]

NEW_CARDS = ESSENTIALS + MONEY + TRANSPORT + FOOD


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

    # 简单结构校验 + 重音标记数量分布
    from collections import Counter
    scene_count = Counter(c["scene"] for c in combined)
    print("\n场景分布：")
    for s in ["essentials", "money", "transport", "food", "lodging", "shopping", "emergency", "chat"]:
        print(f"   {s:10s} {scene_count.get(s, 0):>3} 张")

    essential_count = sum(1 for c in combined if c.get("is_essential"))
    print(f"\nis_essential = true: {essential_count} 张")

    # 写回
    CARDS_PATH.write_text(
        json.dumps(combined, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"\n✓ 写入 {CARDS_PATH}（{len(existing)} → {len(combined)} 张，新增 {len(to_add)}）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
