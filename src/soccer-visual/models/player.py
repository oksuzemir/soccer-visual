from pydantic import BaseModel, Field
from typing import List

class CardStats(BaseModel):
    player_name: str
    number: int | None = None
    age: int | None = None
    height_cm: int | None = None
    weight_kg: int | None = None
    team_name: str | None = None
    previous_teams: List[str] = Field(default_factory=list)

    games_played: int = 0
    goals: int = 0
    assists: int = 0
    shots_on_target: int = 0
    minutes: int = 0
    distance_km: float = 0.0
    pass_accuracy: float = 0.0
    cards_yellow: int = 0
    cards_red: int = 0

    photo_url: str | None = None