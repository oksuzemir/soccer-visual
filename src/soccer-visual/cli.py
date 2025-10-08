import argparse
from soccer_visual.data_providers.api_football import get_player_stats, extract_first
from soccer_visual.processing.transform import normalize_player_stats
from soccer_visual.rendering.card_renderer import render_card
from soccer_visual.config.settings import OUTPUT_DIR

def main():
    parser = argparse.ArgumentParser(description="Generate a football player stat card image.")
    parser.add_argument("--player", type=int, required=True, help="Player ID (API-Football)")
    parser.add_argument("--season", type=int, required=True, help="Season year, e.g. 2023")
    parser.add_argument("--league", type=int, required=True, help="League ID, e.g. 39 (Premier League)")
    parser.add_argument("--out", type=str, default=None, help="Output path (png)")
    args = parser.parse_args()

    raw = get_player_stats(args.player, args.season, args.league)
    first = extract_first(raw)
    if not first:
        raise SystemExit("No player data found for provided parameters.")

    stats = normalize_player_stats(first)
    out_path = args.out or (OUTPUT_DIR / f"player_{args.player}.png")
    final_path = render_card(stats, str(out_path))
    print("Saved:", final_path)

if __name__ == "__main__":
    main()