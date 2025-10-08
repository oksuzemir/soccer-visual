# soccer-visual

Futbol oyuncu maç / sezon istatistiklerini şablon görsel (kart) haline dönüştüren Python projesi.

## Özellikler (İlk Sürüm)

- API-Football üzerinden oyuncu istatistiklerini çekme
- Normalize edip `CardStats` modelinde toplama
- Pillow ile görsel şablona işleme
- Komut satırı aracı (`cli.py`): tek oyuncu kartı üretir

## Kurulum

```bash
git clone https://github.com/oksuzemir/soccer-visual.git
cd soccer-visual
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# .env içinde API anahtarını ekleyin
```

## Kullanım

```bash
python src/cli.py --player 276 --season 2023 --league 39
```

Çıktı: `output/player_276.png`

## Yapı

- `src/soccer_visual/config`: Ayarlar
- `src/soccer_visual/data_providers`: Dış API katmanı
- `src/soccer_visual/processing`: Normalizasyon / dönüştürme
- `src/soccer_visual/models`: Pydantic modeller
- `src/soccer_visual/rendering`: Görsel çizim altyapısı
- `src/soccer_visual/utils`: Yardımcı fonksiyonlar
- `assets/`: Şablon, font, ikon

## Geliştirme Yol Haritası

- [ ] Donut chart’ları daha dinamik skalaya bağla
- [ ] Pass accuracy gauge ekle
- [ ] Çoklu maç trend grafiği
- [ ] FastAPI endpoint (kart üretimi)
- [ ] SVG şablon alternatifi

## Lisans

(Terp tercihine göre ekleyin)
