import json
import os


def load_scores(path: str) -> dict:
    defaults = {
        "best_score": 0,
        "last_score": 0,
        "games_played": 0,
        "best_level": 1,
    }
    if not os.path.exists(path):
        return defaults
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        defaults.update({k: int(data.get(k, v)) for k, v in defaults.items()})
    except Exception:
        pass
    return defaults


def save_scores(path: str, data: dict) -> None:
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Gagal menyimpan skor: {e}")
