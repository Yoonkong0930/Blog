"""설정값. 환경변수로 바꿀 수 있어요."""

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

KST = timezone(timedelta(hours=9))

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "posts"

# 사용할 Claude 모델
MODEL = os.environ.get("BLOG_MODEL") or "claude-sonnet-5-5"

# 하루에 만들 글 개수
POSTS_PER_DAY = int(os.environ.get("POSTS_PER_DAY") or 2)

# 네이버 예약 발행 추천 시간 (글 순서대로)
PUBLISH_TIMES = (os.environ.get("PUBLISH_TIMES") or "08:00,19:00").split(",")

# 썸네일 배경 사진의 진하기 (0.10 = 10%. 높을수록 사진이 진하게 보임)
THUMB_IMAGE_OPACITY = float(os.environ.get("THUMB_IMAGE_OPACITY") or 0.10)

# 최근 며칠 동안 다룬 주제는 다시 고르지 않음
DEDUPE_DAYS = int(os.environ.get("DEDUPE_DAYS") or 14)

# 썸네일 글꼴 (GitHub Actions에서는 fonts-noto-cjk 패키지가 설치됨)
FONT_CANDIDATES = [
    os.environ.get("BLOG_FONT", ""),
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc",
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
    "C:/Windows/Fonts/malgunbd.ttf",
]


def today_kst() -> datetime:
    return datetime.now(KST)
