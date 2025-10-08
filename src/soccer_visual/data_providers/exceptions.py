class APIFootballError(Exception):
    """Genel taban hata (isim legacy)."""

class APIFootballRateLimitError(APIFootballError):
    """Rate limit aşıldı."""

class APIFootballNotFound(APIFootballError):
    """Kaynak bulunamadı."""

class APIFootballValidationError(APIFootballError):
    """Parametre doğrulama veya eksik param."""