from pathlib import Path
from urllib.parse import urlparse
import bleach

import pytest
import re

from .conftest import (
    REQUIRED_FIELDS,
    VALID_STATUS,
    VIDEO_FIELDS,
    ALLOWED_VIDEO_DOMAINS,
    DANGEROUS_PATTERNS,
    load_episodes,
)

NULL_ALLOWED_VIDEO_STATUS = {
    "incompleto",
    "perdido",
}


def has_videos(data):
    return data["videos"] is not None

@pytest.mark.parametrize("file,data", load_episodes())
def test_no_html_content(file, data):
    def check_value(value, path=""):
        if isinstance(value, dict):
            for key, item in value.items():
                check_value(item, f"{path}.{key}")

        elif isinstance(value, list):
            for index, item in enumerate(value):
                check_value(item, f"{path}[{index}]")

        elif isinstance(value, str):
            cleaned = bleach.clean(
                value,
                tags=[],
                attributes={},
                strip=True,
            )

            assert cleaned == value, (
                f"{file.name}: HTML detectado em {path}"
            )

    check_value(data)

@pytest.mark.parametrize("file,data", load_episodes())
def test_content_sanitization(file, data):
    def check_value(value, path=""):
        if isinstance(value, dict):
            for key, item in value.items():
                check_value(item, f"{path}.{key}")

        elif isinstance(value, list):
            for index, item in enumerate(value):
                check_value(item, f"{path}[{index}]")

        elif isinstance(value, str):
            for pattern in DANGEROUS_PATTERNS:
                assert not re.search(
                    pattern,
                    value,
                    flags=re.IGNORECASE
                ), (
                    f"{file.name}: conteúdo suspeito em {path}: "
                    f"{value}"
                )

    check_value(data)
    
@pytest.mark.parametrize("file,data", load_episodes())
def test_url_has_no_credentials(file, data):
    if not has_videos(data):
        assert data["status"] in NULL_ALLOWED_VIDEO_STATUS
        return

    for video in data["videos"]:
        parsed = urlparse(video["url"])

        assert not parsed.username
        assert not parsed.password

@pytest.mark.parametrize("file,data", load_episodes())
def test_required_fields(file, data):
    missing = REQUIRED_FIELDS - data.keys()

    assert not missing, (
        f"{file.name} está sem campos obrigatórios: {missing}"
    )


@pytest.mark.parametrize("file,data", load_episodes())
def test_filename(file, data):
    expected_suffix = f'{data["slug"]}-{data["versao"]}'

    assert file.stem.endswith(expected_suffix), (
        f"{file.name} deveria terminar com {expected_suffix}.yaml"
    )


def test_slug_is_unique():
    slugs = [
        data["slug"]
        for _, data in load_episodes()
        if data and data["ativo"]
    ]

    assert len(slugs) == len(set(slugs)), (
        "Existem slugs duplicados entre os episódios ativos"
    )


@pytest.mark.parametrize("file,data", load_episodes())
def test_basic_types(file, data):
    assert isinstance(data["titulo"], str)
    assert isinstance(data["slug"], str)
    assert isinstance(data["ano"], int)

    assert data["status"] in VALID_STATUS

    assert isinstance(data["versao"], int)
    assert isinstance(data["ativo"], bool)

    if data["status"] in NULL_ALLOWED_VIDEO_STATUS:
        assert data["videos"] is None
    else:
        assert isinstance(data["videos"], list)
        assert data["videos"], "Deve existir pelo menos um vídeo"


@pytest.mark.parametrize("file,data", load_episodes())
def test_video_fields(file, data):
    if not has_videos(data):
        assert data["status"] in NULL_ALLOWED_VIDEO_STATUS
        return

    for video in data["videos"]:
        missing = VIDEO_FIELDS - video.keys()

        assert not missing, (
            f"{file.name} vídeo sem campos: {missing}"
        )


@pytest.mark.parametrize("file,data", load_episodes())
def test_video_types(file, data):
    if not has_videos(data):
        assert data["status"] in NULL_ALLOWED_VIDEO_STATUS
        return

    for video in data["videos"]:
        assert isinstance(video["tipo"], str)
        assert isinstance(video["duracao"], int)
        assert isinstance(video["url"], str)
        assert isinstance(video["transcricao"], str)


@pytest.mark.parametrize("file,data", load_episodes())
def test_urls(file, data):
    if not has_videos(data):
        assert data["status"] in NULL_ALLOWED_VIDEO_STATUS
        return

    for video in data["videos"]:
        parsed = urlparse(video["url"])

        assert parsed.scheme in ("http", "https")
        assert parsed.netloc in ALLOWED_VIDEO_DOMAINS    


@pytest.mark.parametrize("file,data", load_episodes())
def test_video_duration(file, data):
    if not has_videos(data):
        assert data["status"] in NULL_ALLOWED_VIDEO_STATUS
        return

    for video in data["videos"]:
        assert video["duracao"] > 0


@pytest.mark.parametrize("file,data", load_episodes())
def test_transcription_not_empty(file, data):
    if not has_videos(data):
        assert data["status"] in NULL_ALLOWED_VIDEO_STATUS
        return

    for video in data["videos"]:
        assert video["transcricao"].strip()
