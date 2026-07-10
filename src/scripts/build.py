from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import sys
import os
import subprocess

import yaml


ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = ROOT.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

SOURCE_DIR = ROOT / "episodios"
DIST_DIR = ROOT / "dist"

OUTPUT_FILE = DIST_DIR / "episodios.json"


from src.schema import Episodio


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