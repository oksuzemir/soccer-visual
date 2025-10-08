import argparse
from pathlib import Path
from soccer_visual.config import settings
from soccer_visual.data_providers import football_data as fd
from soccer_visual.data_providers.exceptions import (
    APIFootballError,
    APIFootballNotFound,
    APIFootballValidationError
)
from soccer_visual.models.player import CardStats
from soccer_visual.rendering.card_renderer import render_card

def cli():
    parser = argparse.ArgumentParser(description="Generate football player card (limited free data).")
    parser.add_argument("--team-id", type=int, required=True, help="Team ID (football-data)")
    parser.add_argument("--player-name", type=str, help="Player name substring (single mode)")
    parser.add_argument("--competition-id", type=int, help="Competition ID (for goals lookup)", required=False)
    parser.add_argument("--team-batch", action="store_true", help="Generate all squad cards")
    parser.add_argument("--out", type=str, help="Output path (single)")
    parser.add_argument("--limit-scorers", type=int, default=100)
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    try:
        if not settings.FOOTBALL_DATA_KEY:
            raise APIFootballValidationError("FOOTBALL_DATA_KEY eksik (.env).")

        team_json = fd.get_team(args.team_id)

        # Goals lookup haritası (opsiyonel competition-id verilirse)
        scorers_map = {}
        if args.competition_id:
            scorers_json = fd.get_scorers(args.competition_id, limit=args.limit_scorers)
            for sc in scorers_json.get("scorers", []):
                pname = sc.get("player", {}).get("name", "")
                goals = sc.get("goals", 0)
                if pname:
                    scorers_map[pname.lower()] = goals

        if args.team_batch:
            squad = fd.collect_team_players(team_json)
            team_name = team_json.get("name", f"team_{args.team_id}")
            out_dir = Path(settings.OUTPUT_DIR) / f"team_{team_name.replace(' ', '_')}"
            out_dir.mkdir(parents=True, exist_ok=True)
            count = 0
            for p in squad:
                pname = p.get("name", "UNKNOWN")
                goals = scorers_map.get(pname.lower(), 0)
                raw = fd.build_cardstats_dict(p, team_json, goals)
                stats = CardStats(**raw)
                stats.finalize()
                out_path = out_dir / f"player_{pname.replace(' ', '_')}.png"
                render_card(stats, str(out_path))
                count += 1
                if args.verbose:
                    print(f"[OK] {pname} -> {out_path}")
            print(f"Toplam {count} kart üretildi: {out_dir}")
        else:
            if not args.player_name:
                raise APIFootballValidationError("Tekil mod için --player-name gerekli.")
            p_obj = fd.find_player_in_team_squad(team_json, args.player_name)
            if not p_obj:
                raise APIFootballNotFound("Oyuncu bulunamadı (substring eşleşmesi).")
            goals = scorers_map.get(p_obj.get("name", "").lower(), 0)
            raw = fd.build_cardstats_dict(p_obj, team_json, goals)
            stats = CardStats(**raw)
            stats.finalize()
            output_path = args.out or (Path(settings.OUTPUT_DIR) / f"player_{stats.player_name.replace(' ', '_')}.png")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            render_card(stats, str(output_path))
            print(f"OK -> {output_path}")

    except (APIFootballValidationError, APIFootballNotFound) as e:
        print(f"[HATA] {e}")
    except APIFootballError as e:
        print(f"[API HATASI] {e}")
    except Exception as e:
        print(f"[GENEL HATA] {e}")

if __name__ == "__main__":
    cli()