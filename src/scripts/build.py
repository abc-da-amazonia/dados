from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import sys
import os
import subprocess
from html import escape
from check_lista import check_lista

import yaml


ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = ROOT.parent
PAGES_BASE_URL = "https://abc-da-amazonia.github.io/dados"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

SOURCE_DIR = ROOT / "episodios"
DIST_DIR = ROOT / "dist"

MANIFEST_FILE = DIST_DIR / "meta.json"
OUTPUT_FILE = DIST_DIR / "episodios.json"


from src.schema import Episodio

def generate_index(files):
    files = [
        file
        for file in files
        if file != "index.html"
    ]

    links = "\n".join(
        f'<li><a href="{escape(file)}" target="_blank" rel="noopener noreferrer">{escape(file)}</a></li>'
        for file in files
    )

    return f"""<!DOCTYPE html>
                <html lang="pt-BR">
                <head>
                <meta charset="UTF-8">
                <title>ABC da Amazônia - Arquivos</title>

                <style>
                body {{
                    font-family: sans-serif;
                    max-width: 800px;
                    margin: 40px auto;
                }}

                li {{
                    margin: 10px 0;
                }}

                a {{
                    text-decoration: none;
                }}
                </style>

                </head>

                <body>

                <ul>
                {links}
                </ul>

                </body>
                </html>
                """

def generate_dist_index():
    files = [
        file.name
        for file in DIST_DIR.iterdir()
        if file.is_file()
    ]

    html = generate_index(files)

    with (DIST_DIR / "index.html").open(
        "w",
        encoding="utf-8"
    ) as f:
        f.write(html)

def load_yaml_episodes():
    episodes = []

    for file in sorted(SOURCE_DIR.glob("*.yaml")):
        with file.open(
            encoding="utf-8"
        ) as f:
            raw = yaml.safe_load(f)


        try:
            episodio = Episodio.model_validate(raw)

        except Exception as e:
            raise ValueError(
                f"{file.name} inválido:\n{e}"
            )

        if not episodio.ativo:
            continue

        episodes.append(
            episodio.model_dump(mode="json")
        )

    return episodes


def generate_payload(episodes):
    now = datetime.now(
        timezone.utc
    )

    contributors = get_episode_contributors()

    payload = {
        "meta": {
            "format": "episodios",
            "build_version": "1.0",

            "generated_at": now.isoformat(),
            "generated_timestamp": int(now.timestamp()),

            "total": len(episodes),

            "github": {
                **get_github_metadata(),

                "contributors_count": len(
                    contributors
                ),

                "contributors": contributors,
            },
        },

        "episodes": episodes,
    }

    return payload

def generate_meta():
    now = datetime.now(timezone.utc)

    files = {}

    for file in sorted(DIST_DIR.glob("*.json")):
        if file.name == MANIFEST_FILE.name:
            continue

        with file.open(encoding="utf-8") as f:
            data = json.load(f)

        meta = data.get("meta", {})

        relative = file.relative_to(DIST_DIR).as_posix()

        files[file.stem] = {
            "file_name": relative,
            "url": f"{PAGES_BASE_URL}/{relative}",
            "format": meta.get("format"),
            "hash": meta.get("hash"),
            "generated_at": meta.get("generated_at"),
            "generated_timestamp": meta.get("generated_timestamp"),
            "size": file.stat().st_size,
        }

    payload = {
        "meta": {
            "format": "manifest",
            "build_version": "1.0",
            "generated_at": now.isoformat(),
            "generated_timestamp": int(now.timestamp()),
            "total_files": len(files),
        },
        "files": files,
    }

    payload["meta"]["hash"] = calculate_hash(payload)

    with MANIFEST_FILE.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            payload,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"Manifesto gerado: {MANIFEST_FILE.name}")

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


def build():
    episodes = load_yaml_episodes()

    payload = generate_payload(
        episodes
    )

    content_hash = calculate_hash(
        payload
    )

    payload["meta"]["hash"] = content_hash

    DIST_DIR.mkdir(
        exist_ok=True
    )

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
    check_lista()
    generate_meta()
    generate_dist_index()

    print(
        f"Build concluído."
    )
    print(
        f"Episódios: {len(episodes)}"
    )
    print(
        f"Hash: {content_hash}"
    )

def git_command(args):
    try:
        return subprocess.check_output(
            args,
            text=True
        ).strip()

    except Exception:
        return None


def get_github_metadata():
    return {
        "repository": os.getenv(
            "GITHUB_REPOSITORY"
        ),

        "branch": os.getenv(
            "GITHUB_REF_NAME"
        ),

        "commit": os.getenv(
            "GITHUB_SHA"
        ),

        "commit_short": git_command(
            [
                "git",
                "rev-parse",
                "--short",
                "HEAD"
            ]
        ),

        "workflow": os.getenv(
            "GITHUB_WORKFLOW"
        ),

        "run_id": os.getenv(
            "GITHUB_RUN_ID"
        ),

        "actor": os.getenv(
            "GITHUB_ACTOR"
        ),
    }


def get_episode_contributors():
    result = git_command(
        [
            "git",
            "log",
            "--format=%an",
            "--",
            "src/episodios"
        ]
    )

    if not result:
        return []

    return sorted(
        set(
            name.strip()
            for name in result.splitlines()
            if name.strip()
        )
    )

if __name__ == "__main__":
    build()