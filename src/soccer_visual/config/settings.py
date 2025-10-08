import os
from pathlib import Path
from dotenv import load_dotenv

# Proje kök yolu
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# .env yolu
ENV_PATH = BASE_DIR / ".env"

# Güvenli yükleme:
# - find_dotenv kullanmıyoruz (Python 3.13 stack frame assertion sorunu)
# - Dosya varsa açıkça path veriyoruz.
if ENV_PATH.exists():
    # override=False -> dışarıdan export ettiğin env değişkenlerini ezmez
    load_dotenv(dotenv_path=ENV_PATH, override=False)
else:
    print(f"[WARN] .env bulunamadı: {ENV_PATH}")

FOOTBALL_DATA_KEY = os.getenv("FOOTBALL_DATA_KEY", "").strip()

FOOTBALL_DATA_BASE_URL = "https://api.football-data.org/v4"

# Fotoğraf alma modu: wikimedia | none
FETCH_PLAYER_IMAGE = os.getenv("FETCH_PLAYER_IMAGE", "wikimedia").strip().lower()

ASSETS_DIR = BASE_DIR / "assets"
TEMPLATES_DIR = ASSETS_DIR / "templates"
FONTS_DIR = ASSETS_DIR / "fonts"
ICONS_DIR = ASSETS_DIR / "icons"
OUTPUT_DIR = BASE_DIR / "output"

CARD_WIDTH = 1000
CARD_HEIGHT = 1200

PLACEHOLDER_IMAGE = ASSETS_DIR / "placeholder_player.png"

# Footer attribution uzunluğunu kısaltma
ATTRIBUTION_MAX_CHARS = 90