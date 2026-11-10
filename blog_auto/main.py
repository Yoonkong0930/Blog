"""매일 실행: 주제 선정 → 초안 작성 → posts/날짜/ 폴더에 저장.

실행:  python -m blog_auto.main
연습:  python -m blog_auto.main --dry-run   (API를 부르지 않고 예시 글로 결과물 모양만 확인)
"""

import argparse
import json
import os
import re
from datetime import timedelta

import markdown

from .config import DEDUPE_DAYS, POSTS_DIR, POSTS_PER_DAY, PUBLISH_TIMES, today_kst

HTML_TEMPLATE = """<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
 body {{ max-width: 720px; margin: 40px auto; padding: 0 16px; font-family: sans-serif; line-height: 1.8; color: #222; }}
 .guide {{ background: #f3f6fb; border: 1px solid #d5deeb; border-radius: 8px; padding: 12px 16px; font-size: 14px; }}
 table {{ border-collapse: collapse; }} td, th {{ border: 1px solid #ccc; padding: 6px 10px; }}
</style></head><body>
<div class="guide">
 <b>사용법</b>: 아래 '본문 시작'부터 끝까지 드래그해서 복사 → 네이버 블로그 글쓰기에 붙여넣기<br>
 <b>제목</b>: {title}<br>
 <b>태그</b>: {tags}<br>
 <b>예약 발행 추천</b>: {publish_at}
</div>
<p>— 본문 시작 —</p>
{body}
</body></html>
"""


def slugify(text: str) -> str:
    return re.sub(r"[^\w가-힣]+", "-", text).strip("-")[:40] or "post"


def recent_topics(days: int) -> list[dict]:
    topics = []
    cutoff = (today_kst() - timedelta(days=days)).strftime("%Y-%m-%d")
    for f in sorted(POSTS_DIR.glob("*/topics.json")):
        if f.parent.name >= cutoff:
            topics += json.loads(f.read_text(encoding="utf-8"))
    return topics


def new_day_dir(date_str: str):
    """같은 날 여러 번 실행하면 2026-11-10, 2026-11-10-2, ... 처럼 새 폴더를 써요."""
    day_dir, n = POSTS_DIR / date_str, 2
    while day_dir.exists():
        day_dir, n = POSTS_DIR / f"{date_str}-{n}", n + 1
    return day_dir


def save_post(day_dir, n: int, post: dict, publish_at: str) -> dict:
    folder = day_dir / f"{n}-{slugify(post['title'])}"
    folder.mkdir(parents=True, exist_ok=True)

    tags_line = " ".join(f"#{t}" for t in post["tags"])
    md = (
        f"# {post['title']}\n\n"
        f"> 예약 발행 추천: **{publish_at}** · 요약: {post['summary']}\n\n"
        f"{post['body']}\n\n"
        f"---\n\n**태그**: {tags_line}\n"
    )
    if post["sources"]:
        md += "\n**참고 자료** (발행 전 사실 확인용, 본문에는 넣지 않아도 돼요)\n" + "".join(
            f"- {s}\n" for s in post["sources"]
        )
    (folder / "post.md").write_text(md, encoding="utf-8")

    body_html = markdown.markdown(post["body"], extensions=["tables"])
    (folder / "post.html").write_text(
        HTML_TEMPLATE.format(title=post["title"], tags=tags_line, publish_at=publish_at, body=body_html),
        encoding="utf-8",
    )
    return {"folder": folder.name, "title": post["title"], "publish_at": publish_at, "tags": post["tags"]}


def write_index(day_dir, date_str: str, entries: list[dict], failures: list[str]) -> None:
    lines = [
        f"# {date_str} 블로그 초안",
        "",
        "| 순서 | 예약 발행 | 제목 | 파일 |",
        "|---|---|---|---|",
    ]
    for i, e in enumerate(entries, 1):
        lines.append(
            f"| {i} | {e['publish_at']} | {e['title']} | "
            f"[글]({e['folder']}/post.md) · [복사용 HTML]({e['folder']}/post.html) |"
        )
    if failures:
        lines += ["", "**실패한 주제**", *[f"- {f}" for f in failures]]
    lines += [
        "",
        "## 발행 순서",
        "1. `post.md`를 열어 내용을 읽고, 내 경험이나 의견을 한두 문단 더해 주세요.",
        "2. 네이버 블로그 글쓰기에서 제목을 넣고 본문을 붙여넣어요.",
        "3. 태그를 넣고, 발행 버튼 옆 **예약**에서 위 시간으로 설정해요.",
    ]
    (day_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


SAMPLE_POST = {
    "title": "연말정산 미리보기 서비스 이용 방법 총정리",
    "tags": ["연말정산", "연말정산미리보기", "홈택스", "절세", "13월의월급"],
    "summary": "홈택스 연말정산 미리보기로 예상 환급액을 확인하는 방법을 정리했어요.",
    "sources": ["https://www.hometax.go.kr"],
    "body": "연말정산, 미리 준비하면 환급액이 달라져요.\n\n## 미리보기 서비스란?\n\n"
    "예시 본문입니다.\n\n| 항목 | 내용 |\n|---|---|\n| 기간 | 예시 |\n\n## 정리\n\n예시 정리 문단이에요.",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="API 없이 예시 글로 결과물만 만들어 보기")
    parser.add_argument("--count", type=int, default=POSTS_PER_DAY)
    parser.add_argument(
        "--topics",
        default=os.environ.get("TOPICS", ""),
        help="직접 정한 주제 (쉼표로 구분). 넣으면 자동 주제 선정을 건너뛰어요",
    )
    args = parser.parse_args()

    from .topics import manual_topics

    my_topics = manual_topics(args.topics)
    if my_topics:
        args.count = len(my_topics)

    now = today_kst()
    date_str = now.strftime("%Y-%m-%d")
    day_dir = POSTS_DIR / f"_dry-run-{date_str}" if args.dry_run else new_day_dir(date_str)
    times = [(PUBLISH_TIMES[i % len(PUBLISH_TIMES)]).strip() for i in range(args.count)]

    if args.dry_run:
        posts = [dict(SAMPLE_POST, title=f"{SAMPLE_POST['title']} {i + 1}") for i in range(args.count)]
        entries = [save_post(day_dir, i + 1, p, f"{date_str} {times[i]}") for i, p in enumerate(posts)]
        write_index(day_dir, date_str, entries, [])
        print(f"예시 결과물을 만들었어요: {day_dir}")
        return

    # API를 쓰는 모듈은 실제 실행할 때만 불러옴 (dry-run은 API 키 없이 동작)
    from .topics import pick_topics
    from .trends import fetch_trends
    from .writer import write_post

    if my_topics:
        print(f"[1/3] 직접 정한 주제 {len(my_topics)}개로 글을 써요.")
        topics = my_topics
    else:
        trends = fetch_trends()
        print(f"[1/3] 트렌드 {len(trends)}개를 가져왔어요.")
        topics = pick_topics(trends, recent_topics(DEDUPE_DAYS), args.count, date_str)
    day_dir.mkdir(parents=True, exist_ok=True)
    (day_dir / "topics.json").write_text(json.dumps(topics, ensure_ascii=False, indent=2), encoding="utf-8")
    print("[2/3] 오늘의 주제:", *[f"  - {t['title']}" for t in topics], sep="\n")

    entries, failures = [], []
    for i, topic in enumerate(topics):
        try:
            post = write_post(topic, date_str)
            entries.append(save_post(day_dir, i + 1, post, f"{date_str} {times[i]}"))
            print(f"[3/3] 글 {i + 1} 완성: {post['title']}")
        except Exception as e:  # 한 편이 실패해도 나머지는 계속
            failures.append(f"{topic['title']} ({e})")
            print(f"[3/3] 글 {i + 1} 실패: {e}")

    write_index(day_dir, date_str, entries, failures)
    if not entries:
        raise SystemExit("글을 하나도 만들지 못했어요.")
    print(f"완료: {day_dir}")


if __name__ == "__main__":
    main()
