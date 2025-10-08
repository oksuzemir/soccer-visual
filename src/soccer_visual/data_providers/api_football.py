from typing import Any, Dict, List, Optional, Callable
import requests
from ..config import settings
from ..data_providers.exceptions import (
    APIFootballError,
    APIFootballRateLimitError,
    APIFootballNotFound,
    APIFootballValidationError
)
from ..utils.retry import retry

BASE_URL = "https://api-football-v1.p.rapidapi.com/v3"

def _headers():
    if not settings.API_FOOTBALL_KEY:
        raise APIFootballValidationError("API key eksik (.env -> API_FOOTBALL_KEY).")
    return {
        "x-rapidapi-key": settings.API_FOOTBALL_KEY,
        "x-rapidapi-host": settings.API_FOOTBALL_HOST
    }

def _request(method: str, path: str, params: Dict[str, Any] | None = None, timeout: int = 15) -> Dict[str, Any]:
    url = f"{BASE_URL}{path}"

    def do_call():
        r = requests.request(method, url, headers=_headers(), params=params, timeout=timeout)
        if r.status_code == 404:
            raise APIFootballNotFound(f"Kaynak bulunamadı: {path} params={params}")
        if r.status_code == 429:
            raise APIFootballRateLimitError("Rate limit aşıldı (429).")
        if r.status_code >= 500:
            # Retry mekanizması üstte handle edilecek
            raise APIFootballError(f"Sunucu hatası {r.status_code}: {r.text[:200]}")
        if r.status_code >= 400:
            raise APIFootballError(f"İstek hatası {r.status_code}: {r.text[:200]}")
        try:
            return r.json()
        except ValueError:
            raise APIFootballError("JSON parse edilemedi.")
    # 500 ve RateLimit için retry (RateLimit'i burada farklı yönetiyoruz)
    try:
        return retry(
            do_call,
            exceptions=(APIFootballError,),
            tries=3
        )
    except APIFootballRateLimitError:
        # Rate limit ise bekleyip tekrar denemek mantıklı olabilir;
        # küçük projede kullanıcıya hızlı feedback verelim
        raise
    except APIFootballError:
        raise

def status() -> Dict[str, Any]:
    return _request("GET", "/status")

def get_player_stats_by_id(player_id: int, season: int, league: Optional[int] = None, page: int = 1) -> Dict[str, Any]:
    """
    Tek bir player id için, season (+ opsiyonel league). 
    League verirsen daha direkt istatistik eşleşmesi sağlar.
    """
    if player_id <= 0:
        raise APIFootballValidationError("player_id > 0 olmalı")
    params = {"id": player_id, "season": season, "page": page}
    if league:
        params["league"] = league
    return _request("GET", "/players", params=params)

def search_players(name: str, season: int, league: Optional[int] = None, page: int = 1) -> Dict[str, Any]:
    """
    İsim arama. name = 'haaland' gibi. Büyük küçük duyarsız.
    """
    if not name or len(name) < 2:
        raise APIFootballValidationError("Arama için en az 2 karakter girin.")
    params = {"search": name, "season": season, "page": page}
    if league:
        params["league"] = league
    return _request("GET", "/players", params=params)

def fetch_all_pages(fetch_func: Callable[[int], Dict[str, Any]], max_pages: int | None = None) -> List[Dict[str, Any]]:
    """
    Paging üzerinden tüm sayfaları toplar.
    fetch_func(page) -> response JSON
    """
    results: List[Dict[str, Any]] = []
    page = 1
    while True:
        data = fetch_func(page)
        resp = data.get("response", [])
        results.extend(resp)
        paging = data.get("paging", {})
        current = paging.get("current", page)
        total = paging.get("total", page)
        if max_pages and current >= max_pages:
            break
        if current >= total:
            break
        page += 1
    return results

def player_first_stat_entry(player_block: Dict[str, Any], preferred_league: int | None = None) -> Dict[str, Any] | None:
    """
    Dönen response[i] içindeki statistics listesinde tercih edilen league varsa onu seç,
    yoksa ilk elemanı döndür.
    """
    stats_list = player_block.get("statistics") or []
    if preferred_league:
        for st in stats_list:
            league_id = (st.get("league") or {}).get("id")
            if league_id == preferred_league:
                return st
    return stats_list[0] if stats_list else None

def extract_first(response_json: Dict[str, Any]) -> Dict[str, Any] | None:
    arr = response_json.get("response") or []
    return arr[0] if arr else None

def get_team_squad(team_id: int) -> Dict[str, Any]:
    params = {"team": team_id}
    return _request("GET", "/players/squads", params=params)

def search_team(name: str) -> Dict[str, Any]:
    params = {"search": name}
    return _request("GET", "/teams", params=params)

def list_leagues(country: str | None = None, code: str | None = None) -> Dict[str, Any]:
    params = {}
    if country:
        params["country"] = country
    if code:
        params["code"] = code
    return _request("GET", "/leagues", params=params)