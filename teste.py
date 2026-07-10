from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent

EPISODES_DIR = ROOT / "src" / "episodios"
TRANSCRIPTS_DIR = ROOT / "src" / "transcricoes"

def load_episodes():
    episodes = []

    for file in sorted(EPISODES_DIR.glob("*.json")):
        with file.open(encoding="utf-8") as f:
            episodes.append((file, json.load(f)))

    return episodes
print(load_episodes())