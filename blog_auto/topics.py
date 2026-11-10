"""사용자가 직접 정한 주제를 글쓰기 단계가 쓰는 형식으로 바꿔요."""


def manual_topics(text: str) -> list[dict]:
    """쉼표나 줄바꿈으로 구분된 주제 목록을 받아요."""
    items = [t.strip() for t in text.replace("\n", ",").split(",") if t.strip()]
    return [
        {
            "category": "",
            "keyword": t,
            "title": t,
            "angle": "사용자가 직접 정한 주제야. 이 주제를 검색하는 사람이 가장 궁금해할 내용을 중심으로 정리해.",
            "why_now": "사용자가 직접 정한 주제",
        }
        for t in items
    ]
