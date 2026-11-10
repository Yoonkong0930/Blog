"""Claude API 호출 공통 코드."""

import json
import re

import anthropic

from .config import MODEL

client = anthropic.Anthropic()  # ANTHROPIC_API_KEY 환경변수를 사용

WEB_SEARCH_TOOL = {"type": "web_search_20260209", "name": "web_search", "max_uses": 6}


def ask(system: str, prompt: str, *, web_search: bool = True, effort: str = "medium") -> str:
    """Claude에게 묻고 답변 텍스트를 돌려줘요. 웹 검색으로 최신 정보를 찾아볼 수 있어요."""
    messages = [{"role": "user", "content": prompt}]
    kwargs = dict(
        model=MODEL,
        max_tokens=32000,
        system=system,
        output_config={"effort": effort},
        # 안전 필터에 걸리면 서버가 다른 모델로 자동 재시도
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )
    if web_search:
        kwargs["tools"] = [WEB_SEARCH_TOOL]

    # 웹 검색이 길어지면 pause_turn으로 멈출 수 있어서, 이어서 진행하도록 반복
    for _ in range(5):
        with client.beta.messages.stream(messages=messages, **kwargs) as stream:
            response = stream.get_final_message()
        if response.stop_reason == "pause_turn":
            messages = [*messages, {"role": "assistant", "content": response.content}]
            continue
        break

    if response.stop_reason == "refusal":
        raise RuntimeError(f"Claude가 요청을 거절했어요: {response.stop_details}")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("답변이 너무 길어서 잘렸어요.")

    # 웹 검색 인용이 있으면 텍스트가 여러 블록으로 나뉘므로 이어 붙임
    return "".join(b.text for b in response.content if b.type == "text").strip()


def extract_json(text: str):
    """답변에서 JSON 부분만 꺼내요 (```json 코드블록 또는 첫 { ... })."""
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    raw = m.group(1) if m else text[text.find("{") : text.rfind("}") + 1]
    return json.loads(raw)
