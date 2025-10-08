from typing import Dict, Any, Optional, List
import requests
from datetime import datetime, date
from ..config import settings
from .exceptions import (
    APIFootballError,
    APIFootballNotFound,
    APIFootballValidationError
)

def _headers():
    if not settings.FOOTBALL_DATA_KEY:
        raise APIFootballValidationError("FOOTBALL_DATA_KEY eksik (.env).")
    return {"X-Auth-Token": settings.FOOTBALL_DATA_KEY}

def _get(path: str, params: Dict[str, Any] | None = None, timeout: int = 12):
    url = f"{settings.FOOTBALL_DATA_BASE_URL}{path}"
    r = requests.get(url, headers=_headers(), params=params, timeout=timeout)
    if r.status_code == 404:
        raise APIFootballNotFound(f"football-data 404: {path}")
    if r.status_code == 403:
        raise APIFootballError(f"403 Forbidden. Token geçersiz / yetkisiz. Body: {r.text[:160]}")
    if r.status_code == 429:
        raise APIFootballError("429 Rate limit (football-data).")
    if r.status_code >= 400:
        raise APIFootballError(f"Hata {r.status_code}: {r.text[:160]}")
    try:
        return r.json()
    except ValueError:
        raise APIFootballError("JSON parse hatası.")

def get_team(team_id: int) -> Dict[str, Any]:
    return _get(f"/teams/{team_id}")

def get_scorers(competition_id: int, limit: int = 100) -> Dict[str, Any]:
    return _get(f"/competitions/{competition_id}/scorers", params={"limit": limit})

def find_player_in_team_squad(team_json: Dict[str, Any], name_query: str) -> Dict[str, Any] | None:
    squad = team_json.get("squad") or []
    q = name_query.lower()
    candidates = [p for p in squad if q in p.get("name", "").lower()]
    if not candidates:
        return None
    return candidates[0]

def collect_team_players(team_json: Dict[str, Any]) -> List[Dict[str, Any]]:
    return team_json.get("squad") or []

def parse_birthdate(raw: Optional[str]) -> Optional[date]:
    if not raw:
        return None
    try:
        # Örnek format: 2000-02-24
        return datetime.fromisoformat(raw.replace("Z", "")).date()
    except ValueError:
        return None

def build_cardstats_dict(player_obj: Dict[str, Any],
                          team_obj: Dict[str, Any],
                          goals: int | None = None) -> Dict[str, Any]:
    """
    Yeni CardStats alanları için sözlük üretir.
    """
    bd = parse_birthdate(player_obj.get("dateOfBirth"))
    return {
        "player_name": player_obj.get("name", "UNKNOWN"),
        "team_name": team_obj.get("name"),
        "position": player_obj.get("position"),
        "nationality": player_obj.get("nationality"),
        "birthdate": bd,
        "shirt_number": player_obj.get("shirtNumber"),
        "goals": goals or 0
    }