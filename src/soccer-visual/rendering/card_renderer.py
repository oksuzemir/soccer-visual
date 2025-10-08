from PIL import Image, ImageDraw, ImageFont
import io, requests, os, math
from ..models.player import CardStats
from ..config.settings import (
    FONTS_DIR, TEMPLATES_DIR, CARD_WIDTH, CARD_HEIGHT,
    MAX_DISTANCE_REF, MAX_MINUTES_REF
)
from .layout_constants import (
    TITLE_POS, NUMBER_POS, STATS_BLOCK_START, LINE_HEIGHT,
    PHOTO_BOX, DONUT_DISTANCE_CENTER, DONUT_MINUTES_CENTER,
    DONUT_RADIUS, FONT_SIZES
)

def _font(file: str, size: int):
    return ImageFont.truetype(str(FONTS_DIR / file), size=size)

def _fetch_image(url: str):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return Image.open(io.BytesIO(r.content)).convert("RGBA")
    except Exception:
        return None

def _draw_donut(draw: ImageDraw.ImageDraw, center, radius, percent, base="#555555", fill="#ffaa00", width=24):
    cx, cy = center
    bbox = [cx - radius, cy - radius, cx + radius, cy + radius]
    # Gri halkayı çiz
    draw.arc(bbox, start=0, end=360, fill=base, width=width)
    # Değer
    start_angle = -90
    end_angle = start_angle + 360 * percent
    draw.arc(bbox, start=start_angle, end=end_angle, fill=fill, width=width)

def render_card(stats: CardStats, output_path: str):
    # Arkaplan
    template_path = TEMPLATES_DIR / "base_field.png"
    if template_path.exists():
        base = Image.open(template_path).convert("RGBA").resize((CARD_WIDTH, CARD_HEIGHT))
    else:
        base = Image.new("RGBA", (CARD_WIDTH, CARD_HEIGHT), "#2d7b32")

    draw = ImageDraw.Draw(base)

    font_title = _font("Montserrat-Bold.ttf", FONT_SIZES["title"])
    font_normal = _font("Montserrat-Regular.ttf", FONT_SIZES["normal"])
    font_small = _font("Montserrat-Regular.ttf", FONT_SIZES["small"])

    # Başlık ve numara
    draw.text(TITLE_POS, stats.player_name.upper(), font=font_title, fill="white")
    if stats.number:
        draw.text(NUMBER_POS, f"#{stats.number}", font=font_title, fill="white")

    # Foto
    if stats.photo_url:
        img = _fetch_image(stats.photo_url)
        if img:
            box_w = PHOTO_BOX[2] - PHOTO_BOX[0]
            box_h = PHOTO_BOX[3] - PHOTO_BOX[1]
            img = img.resize((box_w, box_h))
            base.alpha_composite(img, dest=(PHOTO_BOX[0], PHOTO_BOX[1]))

    # İstatistik listesi
    sx, sy = STATS_BLOCK_START
    lines = [
        ("GAMES", stats.games_played),
        ("GOALS", stats.goals),
        ("ASSISTS", stats.assists),
        ("SHOT ON TGT", stats.shots_on_target),
        ("Y/R CARDS", f"{stats.cards_yellow}/{stats.cards_red}")
    ]
    for i, (label, val) in enumerate(lines):
        draw.text((sx, sy + i * LINE_HEIGHT), f"{label}: {val}", font=font_normal, fill="white")

    # Donut yüzdeleri
    distance_pct = min(stats.distance_km / MAX_DISTANCE_REF, 1.0) if stats.distance_km else 0
    minutes_pct = min(stats.minutes / MAX_MINUTES_REF, 1.0) if stats.minutes else 0

    _draw_donut(draw, DONUT_DISTANCE_CENTER, DONUT_RADIUS, distance_pct, fill="#f2c744")
    _draw_donut(draw, DONUT_MINUTES_CENTER, DONUT_RADIUS, minutes_pct, fill="#ff4d32")

    draw.text((DONUT_DISTANCE_CENTER[0]-90, DONUT_DISTANCE_CENTER[1] + DONUT_RADIUS + 10),
              f"DIST: {stats.distance_km:.1f} km", font=font_small, fill="white")
    draw.text((DONUT_MINUTES_CENTER[0]-90, DONUT_MINUTES_CENTER[1] + DONUT_RADIUS + 10),
              f"MIN: {stats.minutes}", font=font_small, fill="white")

    # Alt bar (yaş / boy / kilo)
    bottom_text = f"AGE: {stats.age or '-'}  HEIGHT: {stats.height_cm or '-'}cm  WEIGHT: {stats.weight_kg or '-'}kg"
    draw.text((80, CARD_HEIGHT - 140), bottom_text, font=font_normal, fill="white")

    # Takım
    if stats.team_name:
        draw.text((80, CARD_HEIGHT - 190), f"TEAM: {stats.team_name}", font=font_normal, fill="white")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    base.save(output_path)
    return output_path