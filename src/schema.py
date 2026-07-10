from pydantic import BaseModel, HttpUrl, Field, field_validator
from typing import Literal
from urllib.parse import urlparse

ALLOWED_VIDEO_DOMAINS = {
    "youtube.com",
    "www.youtube.com"
}


class Video(BaseModel):
    tipo: str
    duracao: int
    url: HttpUrl
    transcricao: str

    @field_validator("url")
    @classmethod
    def validate_url_domain(cls, value):
        domain = urlparse(
            str(value)
        ).netloc.lower()

        if domain not in ALLOWED_VIDEO_DOMAINS:
            raise ValueError(
                f"Domínio não permitido: {domain}"
            )

        return value


class Episodio(BaseModel):
    id: str
    titulo: str
    slug: str
    ano: int
    status: Literal[
        "completo",
        "parcial",
        "perdido",
    ]
    versao: int = Field(ge=1)
    ativo: bool
    videos: list[Video]


    @field_validator("id")
    @classmethod
    def validate_id(cls, value):
        if not value.startswith("A"):
            raise ValueError(
                "id deve iniciar com A"
            )

        return value


    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value):
        import re

        if not re.match(
            r"^[a-z0-9-]+$",
            value
        ):
            raise ValueError(
                "slug inválido"
            )

        return value