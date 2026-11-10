"""Pexels에서 썸네일 배경용 사진을 찾아요. (무료, 출처 표시 의무 없음)

PEXELS_API_KEY 환경변수가 없거나 검색에 실패하면 None을 돌려주고,
썸네일은 사진 없이 배경색만으로 만들어져요.
"""

import io
import json
import os
import urllib.parse
import urllib.request

from PIL import Image

SEARCH_URL = "https://api.pexels.com/v1/search"


def find_photo(query: str, seed: int = 0) -> tuple[Image.Image | None, str]:
    """(사진, 출처 문구)를 돌려줘요. 못 찾으면 (None, "")."""
    key = os.environ.get("PEXELS_API_KEY", "").strip()
    if not key or not query:
        return None, ""

    try:
        url = f"{SEARCH_URL}?{urllib.parse.urlencode({'query': query, 'per_page': 8})}"
        req = urllib.request.Request(url, headers={"Authorization": key, "User-Agent": "blog-auto"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            photos = json.load(resp).get("photos", [])
        if not photos:
            print(f"[images] '{query}' 사진을 찾지 못했어요.")
            return None, ""

        photo = photos[seed % len(photos)]  # 매번 같은 사진만 나오지 않게 검색 결과 중 하나를 고름
        req = urllib.request.Request(photo["src"]["large2x"], headers={"User-Agent": "blog-auto"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            image = Image.open(io.BytesIO(resp.read())).convert("RGB")
        credit = f"{photo.get('photographer', '')} / Pexels ({photo.get('url', '')})"
        return image, credit
    except Exception as e:
        print(f"[images] Pexels 사진을 가져오지 못했어요: {e}")
        return None, ""
