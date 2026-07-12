# Edição não autorizada. Pull requests modificando este arquivo não serão aceitos.
from pathlib import Path
import re
import yaml

from src.schema import ALLOWED_VIDEO_DOMAINS


ROOT = Path(__file__).resolve().parent.parent

EPISODES_DIR = ROOT / "src" / "episodios"

ALLOWED_URLS = {
    "youtube.com",
    "www.youtube.com",
}

DANGEROUS_PATTERNS = [
    r"<\s*/?\s*[a-zA-Z][^>]*>",
    r"<script\b",
    r"</script>",
    r"javascript:",
    r"on\w+\s*=",
    r"DROP\s+TABLE",
    r"DELETE\s+FROM",
    r"SELECT\s+FROM",
    r"INSERT\s+INTO",
    r"UPDATE\s+\w+\s+SET",
    r"--",
    r";\s*$",
]


REQUIRED_FIELDS = {
    "titulo",
    "slug",
    "ano",
    "status",
    "versao",
    "ativo",
    "videos",
}


VIDEO_FIELDS = {
    "tipo",
    "duracao",
    "url",
    "transcricao",
}


VALID_STATUS = {
    "completo",
    "parcial",
    "perdido",
    "incompleto",
}


def load_episodes():
    episodes = []

    for file in sorted(EPISODES_DIR.glob("*.yaml")):
        with file.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)

        episodes.append((file, data))

    return episodes
