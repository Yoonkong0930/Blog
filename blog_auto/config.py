"""설정값. 환경변수로 바꿀 수 있어요."""

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

KST = timezone(timedelta(hours=9))

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "posts"

# 사용할 Claude 모델
MODEL = os.environ.get("BLOG_MODEL") or "claude-sonnet-5-5"

# 글 분야 (쉼표로 구분). 실행할 때마다 최근에 덜 쓴 분야부터 골라요
CATEGORIES = [c.strip() for c in (os.environ.get("CATEGORIES") or "건강/의학,일상,여행").split(",") if c.strip()]

# 하루에 만들 글 개수
POSTS_PER_DAY = int(os.environ.get("POSTS_PER_DAY") or 2)

# 네이버 예약 발행 추천 시간 (글 순서대로)
PUBLISH_TIMES = (os.environ.get("PUBLISH_TIMES") or "08:00,19:00").split(",")

# 최근 며칠 동안 다룬 주제는 다시 고르지 않음
DEDUPE_DAYS = int(os.environ.get("DEDUPE_DAYS") or 14)


def today_kst() -> datetime:
    return datetime.now(KST)
