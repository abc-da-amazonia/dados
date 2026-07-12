from pydantic import BaseModel, HttpUrl, Field, field_validator, model_validator
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
    titulo: str
    slug: str
    ano: int
    status: Literal[
        "completo",
        "parcial",
        "perdido",
        "incompleto"
    ]
    versao: int = Field(ge=1)
    ativo: bool
    videos: list[Video] | None

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

    @model_validator(mode="after")
    def validate_videos_for_status(self):
        if self.videos is None and self.status not in {"incompleto", "perdido"}:
            raise ValueError(
                "videos não pode ser nulo para este status"
            )

        return self