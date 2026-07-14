from pathlib import Path
import json
import re
import unicodedata
from datetime import datetime, timezone
import hashlib

import yaml


ROOT = Path(__file__).resolve().parent.parent.parent

SOURCE_DIR = ROOT / "src" / "episodios"
INPUT_FILE = ROOT / "src" / "mapeamento" / "episodios_mapeados.txt"
OUTPUT_FILE = ROOT / "src" / "dist" / "episodios_mapeados.json"


def slugify(value: str) -> str:
    value = unicodedata.normalize(
        "NFKD",
        value
    )

    value = (
        value
        .encode("ascii", "ignore")
        .decode("ascii")
    )

    value = value.lower()

    value = re.sub(
        r"[^a-z0-9]+",
        "-",
        value
    )

    return value.strip("-")


def load_active_episodes():
    episodes = {}

    for file in SOURCE_DIR.glob("*.yaml"):
        with file.open(
            encoding="utf-8"
        ) as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            continue

        if data.get("ativo") is True:
            episodes[data["slug"]] = data

    return episodes


def generate_report():
    existing = load_active_episodes()

    result = []

    counter = 1

    with INPUT_FILE.open(
        encoding="utf-8"
    ) as f:
        items = [
            line.strip()
            for line in f
            if line.strip()
        ]

    for item in items:
        slug = slugify(item)

        episode = existing.get(
            slug
        )

        entry = {
            "titulo": item,
            "slug": slug,
            "exists": episode is not None,
            "status": "incompleto",
            "versao": None,
        }

        if episode:
            entry.update(
                {
                    "status": episode.get("status"),
                    "versao": episode.get("versao"),
                }
            )

        result.append(entry)

        counter += 1
    
    return result

def calculate_hash(payload):
    content = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )

    return hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()

def check_lista():
    report = generate_report()

    OUTPUT_FILE.parent.mkdir(
        exist_ok=True
    )

    now = datetime.now(timezone.utc)

    payload = {
        "meta": {
            "format": "episodios_mapeados",
            "build_version": "1.0",

            "generated_at": now.isoformat(),
            "generated_timestamp": int(now.timestamp()),

            "total": len(report),

            "exists": sum(
                1
                for item in report
                if item["exists"]
            ),

            "missing": sum(
                1
                for item in report
                if not item["exists"]
            ),
        },

        "items": report,
    }

    payload["meta"]["hash"] = calculate_hash(payload)

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            payload,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print("Relatório gerado!")

    print(
        f"Itens analisados: {payload['meta']['total']}"
    )

    print(
        payload["meta"]
    )

    return payload["meta"]


if __name__ == "__main__":
    check_lista()