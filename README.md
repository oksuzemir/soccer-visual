# soccer-visual (football-data.org sürümü)

Bu sürüm yalnızca [football-data.org](https://www.football-data.org/) API'sini kullanır.

## Sağlanan Veriler (Free Tier Kısıtları)

football-data.org free tier ayrıntılı bireysel oyuncu maç istatistikleri (pas isabeti, şut isabeti, dakika, kartlar) sunmaz. Bu nedenle kartta:

- Goals: `GET /v4/competitions/{id}/scorers` endpoint’inden (eşleşen isim bulunursa)
- Takım ve oyuncu temel bilgisi: `GET /v4/teams/{team_id}` içindeki `squad`
- Diğer metrikler (Assists, Minutes, Shots, Pass Accuracy, Distance, Cards) => “N/A” (isteğe bağlı gizlenebilir)

## Özellikler

- Tek oyuncu kartı üretimi: isim substring eşleşmesi ile kadrodan oyuncu bulma
- Tüm takım kadrosu için toplu kart üretimi (`--team-batch`)
- Placeholder siluet görseli (foto verisi olmadığı için)
- Metrik yoksa N/A yazma veya donut alanını gri gösterme
- Basit layout, Pillow ile görsel render

## Kurulum

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows Git Bash
pip install -r requirements.txt
cp .env.example .env
# .env içine FOOTBALL_DATA_KEY=... ekle
```

API token almak:

1. https://www.football-data.org/client/register
2. Hesap oluştur, mail doğrula.
3. Dashboard’da API token’ı kopyala.
4. `.env` içine `FOOTBALL_DATA_KEY=TOKEN` yaz.

## Kullanım

Tek oyuncu:

```bash
python src/cli.py \
  --team-id 65 \
  --player-name haaland \
  --competition-id 2021 \
  -v
```

Örnek IDs:

- Premier League (competition): 2021
- Manchester City (team): 65

Toplu kart (takım kadrosu):

```bash
python src/cli.py --team-id 65 --competition-id 2021 --team-batch -v
```

Not: `--team-batch` modunda kadrodaki tüm oyuncular için goals lookup yapılır; scorer listesinde bulunmayanlar 0 goal görünür.

Çıktı: `output/player_<NAME>.png` veya batch modunda `output/team_<TEAMNAME>/player_<NAME>.png`

## .env Örneği

```
FOOTBALL_DATA_KEY=YOUR_TOKEN_HERE
```

## Dosya Yapısı

```
assets/
  fonts/
  templates/
  placeholder_player.png
src/
  cli.py
  soccer_visual/
    config/settings.py
    data_providers/football_data.py
    data_providers/exceptions.py
    models/player.py
    rendering/card_renderer.py
    rendering/layout_constants.py
    utils/
        __init__.py
```

## Yol Haritası

- [ ] İsteğe bağlı: API-Football entegrasyonunu opsiyonel mod olarak geri ekleme
- [ ] Statik/derlenen SVG layout
- [ ] JSON cache (scorers + team) ile rate limit azaltma
- [ ] Oyuncu isim eşleşme skorlaması (Levenshtein)

## Lisans

Uygun bir lisans seçip ekleyin (MIT vb.).
