from dataclasses import dataclass, asdict
from typing import Any


@dataclass(slots=True)
class Track:
    id: str
    title: str
    stream_url: str
    webpage_url: str
    duration: int
    thumbnail: str | None
    requester_id: int
    requester_name: str
    source: str = "youtube"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Track":
        keys = {
            "id",
            "title",
            "stream_url",
            "webpage_url",
            "duration",
            "thumbnail",
            "requester_id",
            "requester_name",
            "source",
        }
        return cls(**{key: value for key, value in data.items() if key in keys})
