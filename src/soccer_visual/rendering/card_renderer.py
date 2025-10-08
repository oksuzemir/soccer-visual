from PIL import Image, ImageDraw, ImageFont
import os
from ..models.player import CardStats
from ..config.settings import (
    FONTS_DIR, TEMPLATES_DIR, PLACEHOLDER_IMAGE, CARD_WIDTH, CARD_HEIGHT,
    ATTRIBUTION_MAX_CHARS
)
from ..config import settings
from soccer_visual.utils.player_image import get_player_photo_wikimedia

# Tema / basit stil
BG_TOP = "#184d1f"
BG_BOTTOM = "#2f7c33"
PANEL_BG = (255, 255, 255, 35)
PANEL_BORDER = (255, 255, 255, 70)
TITLE_COLOR = "#FFFFFF"
LABEL_COLOR = "#d8ffe0"
VALUE_COLOR = "#FFFFFF"
FOOTER_COLOR = "#ffffff"

AVATAR_RADIUS = 160


def _font(file: str, size: int):
    path = FONTS_DIR / file
    if not path.exists():
        return ImageFont.load_default()
    return ImageFont.truetype(str(path), size=size)


def _gradient_bg(size):
    w, h = size
    base = Image.new("RGBA", size, BG_TOP)
    top = Image.new("RGBA", size, BG_BOTTOM)
    mask = Image.new("L", size)
    md = ImageDraw.Draw(mask)
    for y in range(h):
        md.line([(0, y), (w, y)], fill=int(255 * y / h))
    return Image.composite(top, base, mask)


def _placeholder():
    if PLACEHOLDER_IMAGE.exists():
        try:
            return Image.open(PLACEHOLDER_IMAGE).convert("RGBA")
        except Exception:
            pass
    img = Image.new("RGBA", (AVATAR_RADIUS * 2, AVATAR_RADIUS * 2), "#1f1f1f")
    d = ImageDraw.Draw(img)
    f = _font("Montserrat-Bold.ttf", 38)
    d.text((30, AVATAR_RADIUS - 30), "NO PHOTO", font=f, fill="white")
    return img


def _circular_avatar(base, img, center, radius):
    cx, cy = center
    if img is None:
        img = _placeholder()
    img = img.resize((radius * 2, radius * 2))
    mask = Image.new("L", (radius * 2, radius * 2), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse((0, 0, radius * 2, radius * 2), fill=255)
    avatar = Image.new("RGBA", (radius * 2, radius * 2), (0, 0, 0, 0))
    avatar.paste(img, (0, 0), mask)
    base.alpha_composite(avatar, (cx - radius, cy - radius))


def _panel(base, x, y, w, h, radius=30):
    panel = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(panel)
    d.rounded_rectangle((0, 0, w, h), radius, fill=PANEL_BG, outline=PANEL_BORDER, width=2)
    base.alpha_composite(panel, (x, y))


def render_card(stats: CardStats, output_path: str):
    stats.finalize()

    size = (CARD_WIDTH, CARD_HEIGHT)
    base = _gradient_bg(size)
    draw = ImageDraw.Draw(base)

    # Foto (Wikimedia)
    photo_meta = get_player_photo_wikimedia(stats.player_name)
    img = None
    if photo_meta and photo_meta.get("path") and os.path.exists(photo_meta["path"]):
        try:
            img = Image.open(photo_meta["path"]).convert("RGBA")
        except Exception:
            img = None

    # Başlık
    title_font = _font("Montserrat-Bold.ttf", 76)
    name_text = stats.player_name.upper()
    while title_font.getlength(name_text) > CARD_WIDTH - 80 and title_font.size > 34:
        title_font = _font("Montserrat-Bold.ttf", title_font.size - 4)
    draw.text((50, 40), name_text, font=title_font, fill=TITLE_COLOR)

    team_font = _font("Montserrat-Regular.ttf", 44)
    team_text = stats.team_name or "TEAM UNKNOWN"
    draw.text((50, 140), team_text, font=team_font, fill="#e0ffe2")

    # Avatar
    _circular_avatar(base, img, center=(240, 480), radius=AVATAR_RADIUS)

    # Stat panel
    panel_x = 470
    panel_y = 230
    panel_w = CARD_WIDTH - panel_x - 60
    panel_h = 620
    _panel(base, panel_x, panel_y, panel_w, panel_h)

    label_font = _font("Montserrat-Regular.ttf", 36)
    value_font = _font("Montserrat-Bold.ttf", 40)

    fields = stats.dynamic_fields()
    line_gap = 80
    inner_x_label = panel_x + 40
    inner_x_value = panel_x + panel_w - 40
    y = panel_y + 50

    for label, value in fields:
        draw.text((inner_x_label, y), label, font=label_font, fill=LABEL_COLOR)
        tw = value_font.getlength(value)
        draw.text((inner_x_value - tw, y - 6), value, font=value_font, fill=VALUE_COLOR)
        y += line_gap
        if y > panel_y + panel_h - 60:
            break

    # Footer + foto attribution
    footer_font = _font("Montserrat-Regular.ttf", 20)
    base_footer = "Data: football-data.org (Free Tier)"
    if photo_meta:
        artist = photo_meta.get("artist") or "Author?"
        lic = photo_meta.get("license") or "License?"
        attr = f"Image: {artist} ({lic})"
        # kısaltma
        if len(attr) > ATTRIBUTION_MAX_CHARS:
            attr = attr[:ATTRIBUTION_MAX_CHARS - 3] + "..."
        footer_text = base_footer + " | " + attr
    else:
        footer_text = base_footer + " | Image: Placeholder"

    draw.text((50, CARD_HEIGHT - 70), footer_text, font=footer_font, fill=FOOTER_COLOR)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    base.save(output_path)
    return output_path