from dataclasses import dataclass
from typing import Tuple


@dataclass
class Stream:
    index: int
    stream_type: str
    codec: str
    language: str
    description: str
    checked: bool = False

    @property
    def match_key(self) -> Tuple[str, str, str]:
        return (self.stream_type.lower(), self.language.lower(), self.codec.lower())

    @property
    def type_label(self) -> str:
        labels = {
            "video": "Video",
            "audio": "Audio",
            "subtitle": "Subtitulo",
        }
        return labels.get(self.stream_type, self.stream_type.upper())

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "stream_type": self.stream_type,
            "codec": self.codec,
            "language": self.language,
            "description": self.description,
            "checked": self.checked,
        }

    @classmethod
    def from_probe(cls, stream_data: dict) -> "Stream":
        index = stream_data.get("index", 0)
        stream_type = stream_data.get("codec_type", "unknown")
        codec = stream_data.get("codec_name", "unknown")
        tags = stream_data.get("tags", {})
        language = tags.get("language", "und")
        description = tags.get("description", "")
        return cls(
            index=index,
            stream_type=stream_type,
            codec=codec,
            language=language,
            description=description,
        )
