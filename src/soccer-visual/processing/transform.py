from ..models.player import CardStats

def _parse_metric(metric_str: str | None):
    if not metric_str or not isinstance(metric_str, str):
        return None
    # "180 cm" -> 180
    for token in metric_str.split():
        if token.isdigit():
            return int(token)
    return None

def normalize_player_stats(api_obj: dict) -> CardStats:
    player = api_obj["player"]
    stats_list = api_obj["statistics"]
    s = stats_list[0]

    games = s.get("games", {})
    shots = s.get("shots", {})
    goals = s.get("goals", {})
    passes = s.get("passes", {})
    cards = s.get("cards", {})

    return CardStats(
        player_name = player.get("name"),
        number = games.get("number"),
        age = player.get("age"),
        height_cm = _parse_metric(player.get("height")),
        weight_kg = _parse_metric(player.get("weight")),
        team_name = s.get("team", {}).get("name"),
        previous_teams = [],  # ileride farklı endpoint ile doldurulabilir
        games_played = games.get("appearences") or 0,
        goals = goals.get("total") or 0,
        assists = goals.get("assists") or 0,
        shots_on_target = shots.get("on") or 0,
        minutes = games.get("minutes") or 0,
        distance_km = 0.0,  # API-Football doğrudan vermez
        pass_accuracy = passes.get("accuracy") or 0,
        cards_yellow = cards.get("yellow") or 0,
        cards_red = cards.get("red") or 0,
        photo_url = player.get("photo")
    )