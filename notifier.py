#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飲み会っぽい予定が近づいたら、デスクトップ通知で「事前ドーピング指令」を飛ばす監視スクリプト。

使い方:
    python3 notifier.py --once     # 1回だけチェックして終了(cron向け)
    python3 notifier.py --watch    # 常駐して定期チェック(Ctrl+Cで終了)

通知タイミング: 予定開始の NOTIFY_MINUTES_BEFORE 分前になったら1回だけ通知する。
同じ予定に何度も通知しないよう、notified_state.json に「通知済みID」を記録する。
"""

import argparse
import json
import os
import subprocess
import sys
import time

import quests
import calendar_integration
import main as app  # events.json フォールバック(find_upcoming_events)を再利用

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "notified_state.json")

# 予定開始の何分前に通知するか
NOTIFY_MINUTES_BEFORE = 30
# --watch モードでのチェック間隔(秒)
WATCH_INTERVAL_SECONDS = 60

# このキーワードを含む予定名は「飲み会」判定してドーピング指令のノリを強める
DRINKING_KEYWORDS = ["飲み", "居酒屋", "宴会", "忘年会", "新年会", "歓送迎会", "打ち上げ", "乾杯"]


def is_drinking_event(name):
    return any(keyword in name for keyword in DRINKING_KEYWORDS)


def load_state():
    if not os.path.exists(STATE_FILE):
        return {"notified": []}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def event_id(name, event_time):
    return f"{name}@{event_time.isoformat()}"


def send_notification(title, message):
    if sys.platform == "darwin":
        script = f'display notification "{message}" with title "{title}" sound name "Glass"'
        subprocess.run(["osascript", "-e", script], check=False)
    else:
        print(f"[通知] {title}: {message}")


def collect_upcoming():
    if calendar_integration.is_configured():
        try:
            return calendar_integration.fetch_upcoming_events(NOTIFY_MINUTES_BEFORE)
        except calendar_integration.GoogleCalendarUnavailable as e:
            print(f"(Googleカレンダー連携に失敗、ローカル予定にフォールバック: {e})")
    return app.find_upcoming_events()


def check_once():
    state = load_state()
    notified_ids = set(state.get("notified", []))
    fired = 0

    for name, event_time, delta_minutes in collect_upcoming():
        if delta_minutes > NOTIFY_MINUTES_BEFORE:
            continue

        eid = event_id(name, event_time)
        if eid in notified_ids:
            continue

        if is_drinking_event(name):
            quest_text = quests.drinking_quest()
            title = f"【緊急クエスト】{name} まであと{int(delta_minutes)}分"
        else:
            quest_text = quests.calendar_quest(name)
            title = f"【出撃警報】{name} まであと{int(delta_minutes)}分"

        send_notification(title, quest_text)
        print(f"通知送信: {title} / {quest_text}")

        notified_ids.add(eid)
        fired += 1

    state["notified"] = list(notified_ids)
    save_state(state)
    return fired


def watch():
    print(f"監視開始(予定{NOTIFY_MINUTES_BEFORE}分前に通知 / {WATCH_INTERVAL_SECONDS}秒間隔、Ctrl+Cで終了)")
    try:
        while True:
            check_once()
            time.sleep(WATCH_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\n監視終了。")


def main():
    parser = argparse.ArgumentParser(description="事前ドーピング指令 - 予定通知監視")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--once", action="store_true", help="1回だけチェックして終了")
    group.add_argument("--watch", action="store_true", help="常駐して定期チェック")
    args = parser.parse_args()

    if args.once:
        fired = check_once()
        print(f"チェック完了。通知した予定: {fired}件")
    else:
        watch()


if __name__ == "__main__":
    main()
