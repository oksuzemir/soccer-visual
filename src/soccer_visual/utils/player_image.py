import requests, hashlib, os, re, json, unicodedata
from pathlib import Path
from typing import Optional, List, Dict, Any
from PIL import Image
from ..config import settings

CACHE_DIR = Path("assets/cache_images")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

META_SUFFIX = ".meta.json"
PHOTO_DEBUG = os.getenv("PHOTO_DEBUG", "0") == "1"


def _dbg(*a):
    if PHOTO_DEBUG:
        print("[PHOTO]", *a)


def _strip_html(s: str) -> str:
    return re.sub(r"<.*?>", "", s or "").strip()


def _norm_name(name: str) -> str:
    nf = unicodedata.normalize("NFD", name)
    return "".join(ch for ch in nf if unicodedata.category(ch) != "Mn")


def _resize_max(img: Image.Image, max_side=700):
    w, h = img.size
    m = max(w, h)
    if m <= max_side:
        return img
    scale = max_side / m
    return img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)


def wikidata_search_candidates(name: str, language="en", limit=5) -> List[Dict[str, Any]]:
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",
        "search": name,
        "language": language,
        "format": "json",
        "type": "item",
        "limit": limit
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code != 200:
            _dbg("Search HTTP", r.status_code)
            return []
        data = r.json()
        return data.get("search", [])
    except Exception as e:
        _dbg("Search error", e)
        return []


def wikidata_get_image_filename(qid: str) -> Optional[str]:
    try:
        url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            _dbg("Entity HTTP", r.status_code)
            return None
        data = r.json()
        ent = data.get("entities", {}).get(qid, {})
        claims = ent.get("claims", {})
        p18 = claims.get("P18")
        if not p18:
            return None
        return p18[0]["mainsnak"]["datavalue"]["value"]
    except Exception as e:
        _dbg("Entity err", e)
        return None


def commons_image_info(filename: str):
    try:
        url = "https://commons.wikimedia.org/w/api.php"
        params = {
            "action": "query",
            "titles": f"File:{filename}",
            "prop": "imageinfo",
            "iiprop": "url|extmetadata",
            "format": "json"
        }
        r = requests.get(url, params=params, timeout=10)
        if r.status_code != 200:
            _dbg("Commons HTTP", r.status_code)
            return None
        data = r.json()
        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            infos = page.get("imageinfo")
            if infos:
                return infos[0]
    except Exception as e:
        _dbg("Commons err", e)
    return None


def _meta_path(hash_id: str) -> Path:
    return CACHE_DIR / f"{hash_id}{META_SUFFIX}"


def _load_meta(hash_id: str):
    p = _meta_path(hash_id)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def _save_meta(hash_id: str, meta: dict):
    try:
        _meta_path(hash_id).write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


def _candidate_loops(base_name: str) -> List[str]:
    base_norm = _norm_name(base_name)
    variants = [base_name, base_norm]
    variants.append(base_name + " footballer")
    variants.append(base_norm + " footballer")
    seen = set()
    ordered = []
    for v in variants:
        key = v.lower().strip()
        if key not in seen:
            seen.add(key)
            ordered.append(v.strip())
    return ordered


def get_player_photo_wikimedia(player_name: str):
    if settings.FETCH_PLAYER_IMAGE != "wikimedia":
        _dbg("FETCH_PLAYER_IMAGE not wikimedia")
        return None

    for variant in _candidate_loops(player_name):
        _dbg("Trying variant:", variant)
        candidates = wikidata_search_candidates(variant)
        if not candidates:
            continue
        for cand in candidates:
            qid = cand.get("id")
            if not qid:
                continue
            fname = wikidata_get_image_filename(qid)
            if not fname:
                _dbg("No P18 for", qid)
                continue
            _dbg("Found P18 file:", fname, "QID:", qid)
            info = commons_image_info(fname)
            if not info or not info.get("url"):
                _dbg("No commons url")
                continue
            url = info.get("url")
            hash_id = hashlib.sha1(url.encode("utf-8")).hexdigest()[:18]
            ext = os.path.splitext(url)[1] or ".jpg"
            local_path = CACHE_DIR / f"{hash_id}{ext}"

            cached_meta = _load_meta(hash_id)
            if cached_meta and local_path.exists():
                _dbg("Cache hit", local_path)
                return cached_meta | {"path": local_path}

            try:
                resp = requests.get(url, timeout=20)
                resp.raise_for_status()
                with open(local_path, "wb") as f:
                    f.write(resp.content)
            except Exception as e:
                _dbg("Download err", e)
                continue

            extmeta = info.get("extmetadata", {}) or {}
            artist = _strip_html(extmeta.get("Artist", {}).get("value", "")) or None
            license_short = extmeta.get("LicenseShortName", {}).get("value") or None

            result = {
                "path": local_path,
                "artist": artist,
                "license": license_short,
                "source_url": url,
                "qid": qid,
                "file": fname
            }
            _save_meta(hash_id, {k: v for k, v in result.items() if k != "path"})
            return result

    _dbg("No image found for any variant.")
    return None