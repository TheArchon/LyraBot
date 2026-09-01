import asyncio
import logging
import os
from pathlib import Path
from urllib.parse import (
    parse_qs,
    urlparse,
)

import aiohttp

from py_yt import VideosSearch

from Shizu.config import settings
from Shizu.models import Track


logger = logging.getLogger(
    __name__
)


DOWNLOAD_DIR = Path(
    "downloads"
)

DOWNLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def time_to_seconds(
    value,
) -> int:
    if not value:
        return 0

    try:
        parts = [
            int(item)
            for item in str(
                value
            ).split(":")
        ]

        total = 0

        for item in parts:
            total = (
                total * 60
                + item
            )

        return total

    except Exception:
        return 0


def youtube_id_from_url(
    link: str,
) -> str | None:
    try:
        parsed = urlparse(
            link
        )

        host = (
            parsed.netloc
            .lower()
            .replace(
                "www.",
                "",
            )
        )

        if host == "youtu.be":
            return (
                parsed.path
                .strip("/")
                .split("/")[0]
            )

        if "youtube.com" in host:
            query = parse_qs(
                parsed.query
            )

            if query.get("v"):
                return query["v"][0]

            parts = [
                part
                for part
                in parsed.path.split("/")
                if part
            ]

            if parts:
                if parts[0] in {
                    "shorts",
                    "embed",
                    "live",
                } and len(parts) > 1:
                    return parts[1]

    except Exception:
        pass

    return None


class YouTube:
    async def search(
        self,
        query: str,
    ) -> dict:
        return await asyncio.to_thread(
            self._search_sync,
            query,
        )

    def _search_sync(
        self,
        query: str,
    ) -> dict:
        search = VideosSearch(
            query,
            limit=1,
        )

        # py-yt-search exposes async-style
        # next(), even though search object
        # itself is lightweight.
        return search

    async def _search_result(
        self,
        query: str,
    ) -> dict:
        search = VideosSearch(
            query,
            limit=1,
        )

        result = (
            await search.next()
        ).get(
            "result",
            [],
        )

        if not result:
            raise ValueError(
                "No matching song found."
            )

        return result[0]

    async def resolve(
        self,
        query: str,
        requester_id: int,
        requester_name: str,
    ) -> Track:
        query = query.strip()

        video_id = None
        result = None

        if query.startswith(
            (
                "http://",
                "https://",
            )
        ):
            video_id = (
                youtube_id_from_url(
                    query
                )
            )

        if video_id:
            result = (
                await self._search_result(
                    (
                        "https://www.youtube.com/"
                        f"watch?v={video_id}"
                    )
                )
            )

        else:
            result = (
                await self._search_result(
                    query
                )
            )

            video_id = (
                result.get("id")
            )

        if not video_id:
            raise ValueError(
                "Could not find a "
                "YouTube video ID."
            )

        title = (
            result.get("title")
            or "Unknown song"
        )

        duration = (
            result.get("duration")
        )

        thumbnails = (
            result.get(
                "thumbnails"
            )
            or []
        )

        thumbnail = None

        if thumbnails:
            thumbnail = (
                thumbnails[0]
                .get("url")
            )

            if thumbnail:
                thumbnail = (
                    thumbnail.split(
                        "?"
                    )[0]
                )

        webpage_url = (
            result.get("link")
            or (
                "https://www.youtube.com/"
                f"watch?v={video_id}"
            )
        )

        return Track(
            id=str(
                video_id
            ),

            title=str(
                title
            ),

            # Filled after API download.
            stream_url="",

            webpage_url=(
                webpage_url
            ),

            duration=(
                time_to_seconds(
                    duration
                )
            ),

            thumbnail=thumbnail,

            requester_id=(
                requester_id
            ),

            requester_name=(
                requester_name
            ),

            source="YouTube",
        )

    async def download_audio(
        self,
        track: Track,
    ) -> str:
        if not settings.music_api_key:
            raise RuntimeError(
                "MUSIC_API_KEY is "
                "missing in .env."
            )

        video_id = track.id

        file_path = (
            DOWNLOAD_DIR
            / f"{video_id}.mp3"
        )

        if (
            file_path.exists()
            and file_path.stat().st_size > 0
        ):
            return str(
                file_path
            )

        endpoint = (
            settings.music_api_url
            + "/download"
        )

        params = {
            "url": video_id,
            "type": "audio",
            "api_key": (
                settings.music_api_key
            ),
        }

        timeout = (
            aiohttp.ClientTimeout(
                total=300
            )
        )

        try:
            async with (
                aiohttp.ClientSession(
                    timeout=timeout
                )
            ) as session:

                async with session.get(
                    endpoint,
                    params=params,
                ) as response:

                    if response.status != 200:
                        body = (
                            await response.text()
                        )

                        raise RuntimeError(
                            "Music API returned "
                            f"HTTP {response.status}: "
                            f"{body[:120]}"
                        )

                    with open(
                        file_path,
                        "wb",
                    ) as file:

                        async for chunk in (
                            response.content
                            .iter_chunked(
                                128 * 1024
                            )
                        ):
                            file.write(
                                chunk
                            )

            if (
                not file_path.exists()
                or file_path.stat().st_size == 0
            ):
                raise RuntimeError(
                    "Downloaded audio "
                    "file is empty."
                )

            return str(
                file_path
            )

        except Exception:
            if file_path.exists():
                try:
                    os.remove(
                        file_path
                    )
                except Exception:
                    pass

            raise


youtube = YouTube()