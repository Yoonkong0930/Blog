"""오늘 쓸 블로그 주제를 고르는 단계."""

import json
from collections import Counter

from .claude import ask, extract_json
from .config import CATEGORIES

# 분야별로 어떤 글을 원하는지 Claude에게 알려주는 설명
CATEGORY_GUIDE = {
    "건강/의학": "생활 속 건강 정보, 증상·질환 기초 상식, 계절 건강 관리, 영양제·검진 정보 등 (일반 정보 수준)",
    "일상": "올리브영 세일·추천템, 코스트코 할인·인기 상품, 다이소 추천템, 생활 꿀팁, 계절 쇼핑 리스트 등",
    "여행": "국내외 여행지 추천, 계절 축제, 여행 준비물·꿀팁, 항공·숙소 예약 팁, 당일치기 코스 등",
}

SYSTEM = """너는 네이버 블로그 콘텐츠 기획자야.
사람들이 지금 많이 검색하고, 들어왔을 때 실제로 도움이 되는 정보성 글 주제를 고른다.

주제 고르는 기준:
- 정해준 분야 안에서만 고를 것
- 지금 시기(계절, 행사, 세일 기간, 이슈)와 연결된 주제를 우선할 것
- 정리·방법·비교·체크리스트·추천 목록처럼 읽을거리가 있는 글이 될 것
- 사건 사고, 사망, 범죄, 정치 논쟁, 특정 인물의 논란은 피할 것
- 건강/의학은 진단이나 치료를 대신하지 않는 일반 정보로 다룰 수 있는 주제만 고를 것
- 최근에 이미 쓴 주제와 겹치지 않을 것"""


def manual_topics(text: str) -> list[dict]:
    """사용자가 직접 정한 주제(쉼표나 줄바꿈으로 구분)를 글쓰기 단계가 쓰는 형식으로 바꿔요."""
    items = [t.strip() for t in text.replace("\n", ",").split(",") if t.strip()]
    return [
        {
            "category": "",
            "keyword": t,
            "title": t,
            "angle": "사용자가 직접 정한 주제야. 이 주제를 검색하는 사람이 가장 궁금해할 내용을 중심으로 정리해.",
            "why_now": "사용자가 직접 정한 주제",
            "manual": True,
        }
        for t in items
    ]


def choose_categories(recent_topics: list[dict], count: int) -> list[str]:
    """최근에 덜 쓴 분야부터 골라서 분야가 골고루 돌아가게 해요."""
    used = Counter(t.get("category") for t in recent_topics)
    ordered = sorted(CATEGORIES, key=lambda c: (used[c], CATEGORIES.index(c)))
    return [ordered[i % len(ordered)] for i in range(count)]


def pick_topics(trends: list[dict], recent_topics: list[dict], count: int, date_str: str) -> list[dict]:
    categories = choose_categories(recent_topics, count)
    category_text = "\n".join(
        f"{i}. {c}: {CATEGORY_GUIDE.get(c, '')}" for i, c in enumerate(categories, 1)
    )
    trend_text = json.dumps(trends, ensure_ascii=False, indent=1) if trends else "(가져오지 못함)"
    recent = "\n".join(f"- {t['title']}" for t in recent_topics) or "(없음)"

    prompt = f"""오늘은 {date_str}이야. 오늘 네이버 블로그에 올릴 글 주제 {count}개를 골라줘.
아래 분야에서 순서대로 하나씩 골라.

## 오늘 쓸 분야
{category_text}

## 참고: 오늘의 구글 트렌드 (대한민국)
분야와 맞는 키워드가 있으면 활용하고, 없으면 무시해도 돼.
{trend_text}

## 최근에 이미 쓴 글 (겹치지 않게)
{recent}

웹 검색으로 지금 이 분야에서 사람들이 관심 가질 만한 소식(세일·행사 일정, 계절 이슈, 인기 상품 등)을 확인해.
마지막에 아래 형식의 JSON만 ```json 코드블록으로 답해줘. category에는 위 분야 이름을 그대로 써.

```json
{{"topics": [
  {{
    "category": "분야 이름",
    "keyword": "핵심 검색 키워드",
    "title": "블로그 글 제목 (검색이 잘 되게, 30자 안팎)",
    "angle": "어떤 관점으로 무엇을 정리하는 글인지 한두 문장",
    "why_now": "지금 사람들이 관심 가질 이유"
  }}
]}}
```"""
    data = extract_json(ask(SYSTEM, prompt, effort="medium"))
    return data["topics"][:count]
