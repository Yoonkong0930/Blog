"""주제 하나로 블로그 글 초안을 쓰는 단계."""

import re

from .claude import ask

SYSTEM = """너는 네이버 블로그를 오래 운영한 블로거야. 독자에게 실제로 도움이 되는 정보성 글을 쓴다.

글쓰기 규칙:
- 친근한 존댓말(~요체). 사람이 직접 쓴 것처럼 자연스럽게
- 분량은 본문 기준 2,000~3,000자
- 첫 문단에서 이 글을 읽으면 무엇을 알게 되는지 바로 말할 것
- 소제목(##)으로 3~5개 구간을 나누고, 필요한 곳에 목록이나 표를 쓸 것
- 날짜, 숫자, 가격, 일정 같은 사실은 웹 검색으로 확인한 것만 쓰고, 확실하지 않으면 쓰지 말 것
- 같은 키워드를 억지로 반복하지 말 것
- 마지막에 짧은 정리 문단
- '이 글은 AI가' 같은 문구, 이모지 남발, 과장 광고 문구는 쓰지 말 것
- 본문에 이미지가 들어가면 좋을 자리에 [이미지: 어떤 사진] 형태로 표시할 것

분야별 규칙:
- 건강/의학: 진단·치료를 대신하지 않는 일반 정보로 쓰고, 효과를 단정하거나 과장하지 말 것.
  출처는 질병관리청, 대학병원, 학회 같은 공신력 있는 곳을 우선하고,
  마지막에 '증상이 계속되면 전문의와 상담하세요' 같은 안내를 넣을 것
- 일상(쇼핑·할인·추천템): 가격, 할인율, 행사 기간은 검색으로 확인된 것만 쓰고 기준 날짜를 함께 적을 것.
  매장·시기마다 다를 수 있다고 안내할 것
- 여행: 운영 시간, 요금, 축제 일정은 확인된 것만 쓰고, 방문 전 공식 안내를 확인하라고 할 것"""

FORMAT = """아래 형식 그대로 답해줘. 형식 밖의 말은 쓰지 마.

제목: (최종 글 제목)
태그: (네이버 태그 8~10개, 쉼표로 구분, # 없이)
썸네일: (썸네일에 크게 넣을 문구, 15자 이내)
요약: (검색 결과에 보일 한 줄 요약)
사진검색: (썸네일 배경 사진을 찾을 영어 검색어 2~3단어, 예: kimchi cabbage)
참고: (참고한 사이트 주소들, 쉼표로 구분)
---
(마크다운 본문)"""


def write_post(topic: dict, date_str: str) -> dict:
    prompt = f"""오늘은 {date_str}이야. 아래 주제로 네이버 블로그 글을 써줘.
먼저 웹 검색으로 최신 정보를 확인한 다음 써.

- 제목 후보: {topic['title']}
- 분야: {topic.get('category', '')}
- 키워드: {topic['keyword']}
- 방향: {topic['angle']}
- 지금 관심 가질 이유: {topic['why_now']}

{FORMAT}"""
    return parse_post(ask(SYSTEM, prompt, effort="high"))


def parse_post(text: str) -> dict:
    head, sep, body = text.partition("\n---")
    if not sep:
        raise ValueError("글 형식이 올바르지 않아요 (--- 구분선 없음)")

    def field(name: str) -> str:
        m = re.search(rf"^\s*{name}\s*:\s*(.+)$", head, re.M)
        return m.group(1).strip() if m else ""

    return {
        "title": field("제목"),
        "tags": [t.strip().lstrip("#") for t in field("태그").split(",") if t.strip()],
        "thumbnail_text": field("썸네일") or field("제목"),
        "summary": field("요약"),
        "image_query": field("사진검색"),
        "sources": [s.strip() for s in field("참고").split(",") if s.strip()],
        "body": body.lstrip("-\n").strip(),
    }
