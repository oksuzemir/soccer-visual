from ..models.player import CardStats

def _parse_metric(metric_str: str | None):
    if not metric_str or not isinstance(metric_str, str):
        return None
    for token in metric_str.split():
        if token.isdigit():
            return int(token)
    return None

def normalize_player_stats(api_obj: dict, stat_entry: dict | None = None) -> CardStats:
    """
    api_obj: response[i] (player + statistics list)
    stat_entry: seçilmiş statistics (league filtrelenmiş)
    """
    player = api_obj.get("player") or {}
    # stat_entry yoksa fallback ilk element
    stats_list = api_obj.get("statistics") or []
    if not stat_entry and stats_list:
        stat_entry = stats_list[0]
    s = stat_entry or {}

    games = s.get("games", {}) if s else {}
    shots = s.get("shots", {})
    goals = s.get("goals", {})
    passes = s.get("passes", {})
    cards = s.get("cards", {})

    # Pass accuracy bazen string (%). Örn "82"
    pass_acc = passes.get("accuracy") or 0
    try:
        pass_acc = float(pass_acc)
    except (TypeError, ValueError):
        pass_acc = 0.0

    return CardStats(
        player_name = player.get("name") or "UNKNOWN",
        number = games.get("number"),
        age = player.get("age"),
        height_cm = _parse_metric(player.get("height")),
        weight_kg = _parse_metric(player.get("weight")),
        team_name = (s.get("team") or {}).get("name"),
        previous_teams = [],  # İleride genişletilebilir
        games_played = games.get("appearences") or 0,
        goals = goals.get("total") or 0,
        assists = goals.get("assists") or 0,
        shots_on_target = shots.get("on") or 0,
        minutes = games.get("minutes") or 0,
        distance_km = 0.0,  # API vermediği için placeholder
        pass_accuracy = pass_acc,
        cards_yellow = cards.get("yellow") or 0,
        cards_red = cards.get("red") or 0,
        photo_url = player.get("photo")
    )