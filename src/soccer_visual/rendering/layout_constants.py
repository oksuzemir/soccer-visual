from ..config.settings import CARD_WIDTH, CARD_HEIGHT

# Yeni ölçüler ve alan tanımları
LAYOUT = {
    "canvas": (CARD_WIDTH, CARD_HEIGHT),
    "padding": 50,
    "avatar": {
        "center": (260, 470),   # dairesel avatar merkezi
        "radius": 200
    },
    "title_area": {
        "name_pos": (50, 40),
        "team_pos": (50, 140)
    },
    "stats_panel": {
        "x": 500,
        "y": 220,
        "w": CARD_WIDTH - 500 - 60,
        "h": 650
    },
    "donuts": {
        "goals_center": (330, 880),
        "goals_radius": 140,
        "second_center": (700, 880),
        "second_radius": 120
    },
    "footer_pos": (50, CARD_HEIGHT - 80),
}

FONT_SCALE = {
    "title": 72,
    "team": 40,
    "stat_label": 34,
    "stat_value": 42,
    "small": 24,
    "tiny": 22
}

THEME = {
    "bg_gradient_top": "#1d5924",
    "bg_gradient_bottom": "#3e9a42",
    "panel_bg": (255, 255, 255, 38),
    "panel_border": (255, 255, 255, 60),
    "panel_shadow": (0, 0, 0, 120),
    "title_color": "#FFFFFF",
    "team_color": "#d6ffd7",
    "stat_label": "#e8ffe9",
    "stat_value": "#FFFFFF",
    "accent_primary": "#FFB300",
    "accent_secondary": "#00B4FF",
    "accent_na": "#888888",
    "footer": "#ffffff",
    "avatar_ring": "#ffffff",
    "avatar_ring_shadow": (0, 0, 0, 140),
    "na_badge_bg": (255, 255, 255, 30),
    "na_badge_border": (255, 255, 255, 70)
}