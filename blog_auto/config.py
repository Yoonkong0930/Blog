"""설정값. 환경변수로 바꿀 수 있어요."""

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

KST = timezone(timedelta(hours=9))

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "posts"

# 사용할 Claude 모델
MODEL = os.environ.get("BLOG_MODEL") or "claude-sonnet-5-5"

# 네이버 예약 발행 추천 시간 (글 순서대로)
PUBLISH_TIMES = (os.environ.get("PUBLISH_TIMES") or "08:00,19:00").split(",")


def today_kst() -> datetime:
    return datetime.now(KST)
