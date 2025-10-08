from typing import Any, Dict
from ..config.settings import HEADERS
from ..utils.http import get_json

BASE_URL = "https://api-football-v1.p.rapidapi.com/v3"

def get_player_stats(player_id: int, season: int, league: int) -> Dict[str, Any]:
    """
    API-Football örnek endpoint: /players?id={player_id}&season={season}&league={league}
    """
    url = f"{BASE_URL}/players"
    params = {
        "id": player_id,
        "season": season,
        "league": league
    }
    return get_json(url, headers=HEADERS, params=params)

def extract_first(response: Dict[str, Any]) -> Dict[str, Any] | None:
    arr = response.get("response", [])
    return arr[0] if arr else None