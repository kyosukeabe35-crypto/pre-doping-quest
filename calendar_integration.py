# -*- coding: utf-8 -*-
"""
Googleカレンダー連携。

初回セットアップ(ユーザー自身が行う):
  1. https://console.cloud.google.com/ でプロジェクトを作成(既存でもOK)
  2. 「APIとサービス」→「ライブラリ」で "Google Calendar API" を有効化
  3. 「APIとサービス」→「認証情報」→「認証情報を作成」→「OAuthクライアントID」
     - アプリケーションの種類: デスクトップアプリ
  4. 作成したクライアントIDの「JSONをダウンロード」でファイルを取得し、
     このディレクトリに `credentials.json` として保存する
  5. 初回実行時にブラウザが開き、Googleアカウントでのログイン・同意を求められる
     (これは本人が自分のブラウザで行う。以後は token.json にキャッシュされ、
     再ログインは不要)

このファイルが未設定(credentials.jsonが無い)場合、呼び出し側は
ローカルの events.json にフォールバックする。
"""

import os
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


class GoogleCalendarUnavailable(Exception):
    """credentials.json が無い、またはライブラリ未導入で連携できないとき"""


def is_configured():
    return os.path.exists(CREDENTIALS_FILE)


def _get_credentials():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise GoogleCalendarUnavailable(
                    f"{CREDENTIALS_FILE} が見つからない。セットアップ手順は "
                    "calendar_integration.py 冒頭のコメントを参照。"
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            f.write(creds.to_json())

    return creds


def fetch_upcoming_events(window_minutes):
    """
    直近 window_minutes 分以内に開始するイベントを
    [(summary, start_datetime, delta_minutes), ...] の形で返す。
    連携未設定・失敗時は GoogleCalendarUnavailable を送出する。
    """
    try:
        from googleapiclient.discovery import build
    except ImportError as e:
        raise GoogleCalendarUnavailable(
            "google-api-python-client が未インストール。"
            "`pip install google-auth google-auth-oauthlib google-api-python-client` "
            "を実行しろ。"
        ) from e

    creds = _get_credentials()
    service = build("calendar", "v3", credentials=creds)

    now = datetime.utcnow()
    time_min = now.isoformat() + "Z"
    time_max = (now + timedelta(minutes=window_minutes)).isoformat() + "Z"

    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    items = events_result.get("items", [])

    upcoming = []
    now_local = datetime.now().astimezone()
    for item in items:
        start = item["start"].get("dateTime", item["start"].get("date"))
        summary = item.get("summary", "(無題の予定)")
        try:
            start_dt = datetime.fromisoformat(start)
        except ValueError:
            continue
        if start_dt.tzinfo is None:
            start_dt = start_dt.astimezone()
        delta_minutes = (start_dt - now_local).total_seconds() / 60
        upcoming.append((summary, start_dt, delta_minutes))

    upcoming.sort(key=lambda x: x[2])
    return upcoming
