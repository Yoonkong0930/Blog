"""썸네일 이미지(1080x1080 PNG)를 만들어요."""

import hashlib
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from .config import FONT_CANDIDATES, THUMB_IMAGE_OPACITY

SIZE = 1080

# (배경 위, 배경 아래, 강조색) — 주제마다 하나를 골라 매일 색이 달라짐
PALETTES = [
    ((24, 40, 72), (58, 96, 160), (255, 214, 102)),
    ((20, 70, 60), (40, 140, 110), (255, 240, 200)),
    ((90, 30, 60), (190, 70, 100), (255, 225, 180)),
    ((40, 30, 80), (110, 80, 180), (180, 255, 220)),
    ((30, 30, 30), (80, 80, 80), (255, 120, 90)),
    ((10, 80, 110), (30, 160, 190), (255, 255, 255)),
]


def _font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        if path and Path(path).exists():
            # .ttc 파일은 여러 글꼴이 묶여 있음. Noto Sans CJK는 1번이 한국어(KR)
            index = 1 if path.endswith("NotoSansCJK-Bold.ttc") else 0
            return ImageFont.truetype(path, size, index=index)
    raise FileNotFoundError("한글 글꼴을 찾지 못했어요. BLOG_FONT 환경변수로 글꼴 경로를 지정해 주세요.")


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    """단어 단위로 줄바꿈하고, 한 단어가 너무 길면 글자 단위로 자름."""
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=font) <= max_width:
            line = trial
            continue
        if line:
            lines.append(line)
        line = ""
        for ch in word:
            if draw.textlength(line + ch, font=font) > max_width:
                lines.append(line)
                line = ""
            line += ch
    if line:
        lines.append(line)
    return lines


def make_thumbnail(text: str, label: str, out_path: Path, photo: Image.Image | None = None) -> Path:
    seed = int(hashlib.md5(text.encode()).hexdigest(), 16)
    top, bottom, accent = PALETTES[seed % len(PALETTES)]

    img = Image.new("RGB", (SIZE, SIZE))
    draw = ImageDraw.Draw(img)
    for y in range(SIZE):  # 세로 그라데이션 배경
        t = y / SIZE
        draw.line([(0, y), (SIZE, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(top, bottom)))

    if photo is not None:  # 관련 사진을 정사각형으로 잘라 배경 위에 은은하게 겹침
        photo = ImageOps.fit(photo.convert("RGB"), (SIZE, SIZE), Image.LANCZOS)
        img = Image.blend(img, photo, THUMB_IMAGE_OPACITY)
        draw = ImageDraw.Draw(img)

    margin = 110
    max_w = SIZE - margin * 2

    # 제목이 들어갈 만큼 글자 크기를 줄여가며 맞춤 (최대 4줄)
    for size in range(130, 60, -6):
        font = _font(size)
        lines = _wrap(draw, text, font, max_w)
        if len(lines) <= 4:
            break
    line_h = int(size * 1.3)
    block_h = line_h * len(lines)
    y = (SIZE - block_h) // 2

    # 강조 막대
    draw.rectangle([margin, y - 70, margin + 120, y - 56], fill=accent)

    for line in lines:
        draw.text((margin, y), line, font=font, fill=(255, 255, 255))
        y += line_h

    if label:
        small = _font(40)
        draw.text((margin, SIZE - margin - 40), label, font=small, fill=accent)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG", optimize=True)
    return out_path
