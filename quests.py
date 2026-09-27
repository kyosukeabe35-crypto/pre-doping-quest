# -*- coding: utf-8 -*-
"""
「事前ドーピング指令」用のミッション・セリフデータ(ミリタリー/ミッション調)。
自分の言葉に合わせて自由に追加・編集してOK。
"""

import random

# ------------------------------------------------------------
# コンビニ別「行動レベル」の補給ミッション
# {store}/{item}/{action} が指令文に埋め込まれる
# ------------------------------------------------------------
CONBINI_MISSIONS = [
    {"store": "セブンイレブン", "item": "サラダチキンバー", "action": "即食いせよ"},
    {"store": "ファミリーマート", "item": "サラダチキンバー", "action": "1本流し込め"},
    {"store": "ローソン", "item": "飲むヨーグルト(無糖)", "action": "一気に飲み干せ"},
    {"store": "セブンイレブン", "item": "ゆで卵2個", "action": "殻を剥いて片付けろ"},
    {"store": "ファミリーマート", "item": "素焼きミックスナッツ", "action": "一掴み片付けろ"},
    {"store": "ローソン", "item": "サラダチキン(プレーン)", "action": "半分でいいから腹に入れろ"},
    {"store": "セブンイレブン", "item": "冷奴", "action": "そのまま飲み込め"},
    {"store": "ファミリーマート", "item": "枝豆パック", "action": "1袋片付けろ"},
    {"store": "ローソン", "item": "チーズ(6Pタイプ)", "action": "2個食っておけ"},
    {"store": "セブンイレブン", "item": "野菜ジュース(コップ1杯分)", "action": "一気に飲み干せ"},
]

# ------------------------------------------------------------
# 「超直前(すでに店にいる)」モード用の即応ミッション
# ------------------------------------------------------------
LAST_MINUTE_MISSIONS = [
    "最初の乾杯はハイボールかウーロン茶を選べ、ビールは2杯目からにしておけ",
    "お通しのキャベツか枝豆を先に片付けろ、箸はそこから動かせ",
    "生ビール1杯目は半分まで飲んだら一旦グラスを置け",
    "揚げ物に箸をつける前に、冷奴か枝豆を1品頼んでおけ",
    "ライスは真っ先に頼むな、野菜系を1品挟んでからにしろ",
]

# ------------------------------------------------------------
# シーン別「指令」文言テンプレート
# ------------------------------------------------------------
DRINKING_MISSIONS = [
    "【警戒レベル1】腹部脂肪反応を検知。{store}の『{item}』を{action}。血糖値の暴走を阻止せよ。",
    "【第一種防衛態勢】乾杯の号令がかかる前に、{store}で『{item}』を確保、{action}。",
    "【警報】丸腰で突入すれば、ビール1杯目で血糖値が制御不能になるぞ。{store}の『{item}』を{action}。",
]

DINING_MISSIONS = [
    "【単独出撃任務】今から外食だな? {store}で『{item}』を確保し、{action}。",
    "【偵察指令】ラーメンの誘惑に対抗するため、{store}の『{item}』を{action}。",
    "【最終警告】大盛りに挑む前に、{store}の『{item}』を{action}。",
]

CALENDAR_MISSIONS = [
    "【時限指令】『{event}』開始まで秒読みだ。{store}で『{item}』を確保、{action}。",
    "【予告指令】まもなく『{event}』が始まる。突入前に{store}の『{item}』を{action}。",
    "【予定確認】『{event}』、回避は不可能だ。せめて{store}で『{item}』を{action}。",
]

# ------------------------------------------------------------
# 完了報告に対するリアクション
# ------------------------------------------------------------
SUCCESS_LINES = [
    "防衛成功。腹部脂肪の増殖係数を抑制した。",
    "任務完了。本日のアルコール吸収係数、50%減少だ(※イメージです)。",
    "防衛システム安定。心置きなく前線(飲み会)へ向かえ。",
]

SLACK_LINES = [
    "まあそんな日もある。せめて1杯目はハイボールにしておけ。",
    "防衛失敗……明日の朝、水1Lで回復を図れ。",
    "無防備な突入か。健闘を祈るが、被害担当は自分自身だぞ。",
]

# ------------------------------------------------------------
# 同調率システム: 成功回数のしきい値は降順で判定
# ------------------------------------------------------------
RANKS = [
    (10, "同調率 100% ― 完全防衛態勢"),
    (4, "同調率 65% ― 防衛安定"),
    (1, "同調率 30% ― 初期起動"),
    (0, "同調率 0% ― 未起動"),
]


def rank_for(success_count):
    for threshold, name in RANKS:
        if success_count >= threshold:
            return name
    return RANKS[-1][1]


def random_mission():
    return random.choice(CONBINI_MISSIONS)


def build_mission(template_list, **extra):
    template = random.choice(template_list)
    mission = random_mission()
    return template.format(store=mission["store"], item=mission["item"], action=mission["action"], **extra)


def drinking_quest():
    return build_mission(DRINKING_MISSIONS)


def dining_out_quest():
    return build_mission(DINING_MISSIONS)


def calendar_quest(event_name):
    return build_mission(CALENDAR_MISSIONS, event=event_name)


def last_minute_quest():
    return "【接近戦モード】" + random.choice(LAST_MINUTE_MISSIONS)


def success_line():
    return random.choice(SUCCESS_LINES)


def slack_line():
    return random.choice(SLACK_LINES)
