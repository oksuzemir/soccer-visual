import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
# BASE_DIR -> <repo>/src/...

API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY", "")
API_FOOTBALL_HOST = "api-football-v1.p.rapidapi.com"

HEADERS = {
    "x-rapidapi-key": API_FOOTBALL_KEY,
    "x-rapidapi-host": API_FOOTBALL_HOST
}

ASSETS_DIR = BASE_DIR / "assets"
TEMPLATES_DIR = ASSETS_DIR / "templates"
FONTS_DIR = ASSETS_DIR / "fonts"
ICONS_DIR = ASSETS_DIR / "icons"
OUTPUT_DIR = BASE_DIR / "output"

CARD_WIDTH = 1200
CARD_HEIGHT = 1200

# Basit sabitler
MAX_DISTANCE_REF = 20.0    # km - ölçek
MAX_MINUTES_REF = 120.0    # tek maç perspektifi; sezon kartı yaparsanız değiştirin