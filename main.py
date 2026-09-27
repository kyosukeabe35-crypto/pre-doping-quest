#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
事前ドーピング指令 CLI - MVP
「お酒や食事を我慢したくないが、体型を維持・改善したい」大人向けの
先入れ(足し算)ドーピング支援アプリ。

実行:
    python3 main.py
"""

import json
import os
from datetime import datetime, timedelta

import quests
import calendar_integration

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EVENTS_FILE = os.path.join(BASE_DIR, "events.json")
PROGRESS_FILE = os.path.join(BASE_DIR, "progress.json")

# 予定時刻がこの分数以内に迫っていたら「出撃対象」とみなす
UPCOMING_WINDOW_MINUTES = 120


def load_events():
    if not os.path.exists(EVENTS_FILE):
        return []
    with open(EVENTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_event_time(time_str, now):
    hour, minute = map(int, time_str.split(":"))
    candidate = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    return candidate


def find_upcoming_events():
    now = datetime.now()
    upcoming = []
    for event in load_events():
        event_time = parse_event_time(event["time"], now)
        delta_minutes = (event_time - now).total_seconds() / 60
        if 0 <= delta_minutes <= UPCOMING_WINDOW_MINUTES:
            upcoming.append((event["name"], event_time, delta_minutes))
    upcoming.sort(key=lambda x: x[2])
    return upcoming


def load_progress():
    if not os.path.exists(PROGRESS_FILE):
        return {"success_count": 0}
    with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_progress(progress):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def print_banner():
    progress = load_progress()
    rank = quests.rank_for(progress["success_count"])
    print("=" * 50)
    print("   事前ドーピング指令 - 先入れ指令システム")
    print(f"   称号: {rank}  (ミッション成功 {progress['success_count']}回)")
    print("=" * 50)


def print_menu():
    print()
    print("[1] 予定から出撃")
    print("[2] 今から飲み会")
    print("[3] 今から外食")
    print("[4] 超直前(もう店にいる)")
    print("[0] 終了")
    print()


def issue_quest(quest_text):
    print()
    print("-" * 50)
    print(quest_text)
    print("-" * 50)
    return prompt_completion()


def prompt_completion():
    while True:
        answer = input("実行結果を報告せよ [1: やった / 2: サボる] > ").strip()
        if answer == "1":
            progress = load_progress()
            progress["success_count"] += 1
            save_progress(progress)
            new_rank = quests.rank_for(progress["success_count"])
            print()
            print(quests.success_line())
            print(f"(称号: {new_rank} / ミッション成功 {progress['success_count']}回)")
            return True
        elif answer == "2":
            print()
            print(quests.slack_line())
            return False
        else:
            print("1 か 2 で入力しろ。")


def handle_calendar():
    source = "local"
    if calendar_integration.is_configured():
        try:
            upcoming = calendar_integration.fetch_upcoming_events(UPCOMING_WINDOW_MINUTES)
            source = "google"
        except calendar_integration.GoogleCalendarUnavailable as e:
            print()
            print(f"(Googleカレンダー連携に失敗、ローカル予定にフォールバック: {e})")
            upcoming = find_upcoming_events()
    else:
        upcoming = find_upcoming_events()

    if not upcoming:
        print()
        print(f"直近{UPCOMING_WINDOW_MINUTES}分以内の出撃予定はナシ。平和だな、今のうちに休んでおけ。")
        if source == "local":
            print(f"(予定は {os.path.basename(EVENTS_FILE)} に自分で追加できる。"
                  f"Googleカレンダーと連携したい場合は credentials.json を用意しろ)")
        return

    print()
    print("出撃対象の予定を検知:")
    for i, (name, event_time, delta) in enumerate(upcoming, start=1):
        print(f"  [{i}] {name}  ({event_time.strftime('%H:%M')} / あと約{int(delta)}分)")

    choice = input("指令を出す予定の番号を選べ > ").strip()
    try:
        idx = int(choice) - 1
        name, _, _ = upcoming[idx]
    except (ValueError, IndexError):
        print("番号がおかしい。メインメニューに戻る。")
        return

    quest_text = quests.calendar_quest(name)
    issue_quest(quest_text)


def handle_drinking():
    quest_text = quests.drinking_quest()
    issue_quest(quest_text)


def handle_dining_out():
    quest_text = quests.dining_out_quest()
    issue_quest(quest_text)


def handle_last_minute():
    quest_text = "【超直前指令】" + quests.last_minute_quest()
    issue_quest(quest_text)


def main():
    print_banner()
    while True:
        print_menu()
        choice = input("コマンドを選べ > ").strip()

        if choice == "1":
            handle_calendar()
        elif choice == "2":
            handle_drinking()
        elif choice == "3":
            handle_dining_out()
        elif choice == "4":
            handle_last_minute()
        elif choice == "0":
            print("また出撃を待つ。健闘を祈る。")
            break
        else:
            print("そのコマンドは存在しない。")


if __name__ == "__main__":
    main()
