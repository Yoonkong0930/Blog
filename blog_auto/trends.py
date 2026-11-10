"""구글 트렌드(대한민국) 실시간 인기 검색어를 가져와요. API 키가 필요 없어요."""

import urllib.request
import xml.etree.ElementTree as ET

TRENDS_RSS = "https://trends.google.com/trending/rss?geo=KR"
HT_NS = "{https://trends.google.com/trending/rss}"


def fetch_trends(limit: int = 25) -> list[dict]:
    """인기 검색어 목록. 가져오지 못하면 빈 목록을 돌려줘요 (그때는 Claude가 웹 검색으로 찾음)."""
    try:
        req = urllib.request.Request(TRENDS_RSS, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            root = ET.fromstring(resp.read())
    except Exception as e:  # 네트워크 문제 등
        print(f"[trends] 구글 트렌드를 가져오지 못했어요: {e}")
        return []

    items = []
    for item in root.iter("item"):
        news = [
            n.findtext(f"{HT_NS}news_item_title", "").strip()
            for n in item.findall(f"{HT_NS}news_item")
        ]
        items.append(
            {
                "keyword": item.findtext("title", "").strip(),
                "traffic": item.findtext(f"{HT_NS}approx_traffic", "").strip(),
                "news": [t for t in news if t][:3],
            }
        )
        if len(items) >= limit:
            break
    return items
