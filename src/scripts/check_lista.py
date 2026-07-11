from pathlib import Path
import json
import re
import unicodedata

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
            "id": f"X{counter:03d}",
            "titulo": item,
            "slug": slug,
            "exists": episode is not None,
        }

        if episode:
            entry.update(
                {
                    "existing_id": episode.get("id"),
                    "status": episode.get("status"),
                    "versao": episode.get("versao"),
                }
            )

        result.append(entry)

        counter += 1
    
    return result


def check_lista():
    report = generate_report()

    OUTPUT_FILE.parent.mkdir(
        exist_ok=True
    )

    payload = {
        "meta": {
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