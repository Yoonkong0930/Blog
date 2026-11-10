"""오늘 쓸 블로그 주제를 고르는 단계."""

import json

from .claude import ask, extract_json

SYSTEM = """너는 네이버 블로그 콘텐츠 기획자야.
사람들이 지금 많이 궁금해하고, 검색해서 들어왔을 때 실제로 도움이 되는 정보성 글 주제를 고른다.

주제 고르는 기준:
- 지금 관심이 높은 이슈와 연결되되, 정보·정리·방법·비교·체크리스트처럼 읽을거리가 있는 글이 될 것
- 사건 사고, 사망, 범죄, 정치 논쟁, 특정 인물의 사생활·논란은 피할 것
- 의학·법률·투자 조언처럼 틀리면 해가 되는 주제는 일반 정보 수준으로만 다룰 수 있을 때만 고를 것
- 서로 다른 분야로 골고루 (예: 생활, IT, 경제, 문화, 건강, 여행)
- 최근에 이미 쓴 주제와 겹치지 않을 것"""


def pick_topics(trends: list[dict], recent_titles: list[str], count: int, date_str: str) -> list[dict]:
    trend_text = (
        json.dumps(trends, ensure_ascii=False, indent=1)
        if trends
        else "(트렌드 데이터를 가져오지 못했어. 웹 검색으로 오늘 한국에서 화제인 키워드를 직접 찾아줘.)"
    )
    recent = "\n".join(f"- {t}" for t in recent_titles) or "(없음)"

    prompt = f"""오늘은 {date_str}이야. 오늘 네이버 블로그에 올릴 글 주제 {count}개를 골라줘.

## 오늘의 구글 트렌드 (대한민국)
{trend_text}

## 최근에 이미 쓴 글 (겹치지 않게)
{recent}

필요하면 웹 검색으로 각 키워드가 왜 화제인지 확인해.
마지막에 아래 형식의 JSON만 ```json 코드블록으로 답해줘.

```json
{{"topics": [
  {{
    "keyword": "관련 트렌드 키워드",
    "title": "블로그 글 제목 (검색이 잘 되게, 30자 안팎)",
    "angle": "어떤 관점으로 무엇을 정리하는 글인지 한두 문장",
    "why_now": "지금 사람들이 관심 가질 이유",
    "category": "분야"
  }}
]}}
```"""
    data = extract_json(ask(SYSTEM, prompt, effort="medium"))
    return data["topics"][:count]
