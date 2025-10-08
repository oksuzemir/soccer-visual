from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime

class CardStats(BaseModel):
    # Temel
    player_name: str
    team_name: Optional[str] = None

    # Yeni alanlar
    position: Optional[str] = None
    nationality: Optional[str] = None
    birthdate: Optional[date] = None
    age: Optional[int] = None
    shirt_number: Optional[int] = None

    # Sadece elimizde varsa dolduracağımız istatistiksel alanlar
    goals: int = 0   # scorers endpoint’ten
    assists: int = 0 # (football-data free: genelde yok, 0 kalır)

    # Kullanılmayan/legacy alanlar (görselde artık render etmiyoruz ama ileride API-Football eklenirse)
    previous_teams: List[str] = Field(default_factory=list)

    # Aşağıdakiler free planda yok; placeholder olarak tutuluyor (render etmeyeceğiz)
    games_played: int = 0
    shots_on_target: int = 0
    minutes: int = 0
    distance_km: float = 0.0
    pass_accuracy: float = 0.0
    cards_yellow: int = 0
    cards_red: int = 0

    photo_url: Optional[str] = None

    @staticmethod
    def compute_age(birthdate: Optional[date]) -> Optional[int]:
        if not birthdate:
            return None
        today = date.today()
        return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

    def finalize(self):
        # Yaşı compute et (varsa)
        if self.birthdate and not self.age:
            self.age = self.compute_age(self.birthdate)

    def dynamic_fields(self):
        """
        Boş olmayan alanları (label, value) listesi şeklinde döndür.
        Sıra: Position, Shirt, Nationality, Age, Goals
        Goals yoksa (0) yine gösterelim ama N/A mı 0 mı olduğunu kart_renderer karar verebilir.
        """
        items = []
        if self.position:
            items.append(("Position", self.position))
        if self.shirt_number is not None:
            items.append(("Number", str(self.shirt_number)))
        if self.nationality:
            items.append(("Nationality", self.nationality))
        if self.age is not None:
            items.append(("Age", str(self.age)))
        # Goals daima en sonda
        items.append(("Goals", str(self.goals)))
        return items