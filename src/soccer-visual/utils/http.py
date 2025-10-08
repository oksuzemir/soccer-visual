from typing import Any, Dict
import requests
from rich import print

def get_json(url: str, headers: Dict[str, str], params: Dict[str, Any] | None = None, timeout: int = 15):
    r = requests.get(url, headers=headers, params=params, timeout=timeout)
    if r.status_code != 200:
        print(f"[red]HTTP Error {r.status_code}: {r.text[:200]}[/red]")
    r.raise_for_status()
    return r.json()