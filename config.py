from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()


def required(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}"
        )

    return value


def optional_int(name: str) -> int | None:
    value = os.getenv(name)

    if not value:
        return None

    try:
        return int(value)

    except ValueError as exc:
        raise RuntimeError(
            f"{name} must be an integer."
        ) from exc


@dataclass(frozen=True, slots=True)
class Settings:
    api_id: int
    api_hash: str
    bot_token: str
    string_session: str

    owner_id: int
    owner_username: str

    mongo_uri: str
    mongo_db_name: str

    bot_name: str
    bot_username: str

    start_img_url: str
    log_group_id: int | None

    support_group: str
    support_channel: str

    music_api_url: str
    music_api_key: str

    max_queue_size: int
    max_playlists_per_user: int
    max_tracks_per_playlist: int

    log_level: str

    # Telegram custom emoji IDs used as inline-button icons.
    emoji_add_group: str
    emoji_help: str
    emoji_owner: str
    emoji_channel: str
    emoji_support: str
    emoji_music: str
    emoji_controls: str
    emoji_general: str
    emoji_back: str
    emoji_close: str
    emoji_pause: str
    emoji_resume: str
    emoji_replay: str
    emoji_skip: str
    emoji_stop: str
    emoji_restart: str
    emoji_cancel: str

    # Telegram custom emoji IDs used inside message/caption text.
    emoji_text_hey: str
    emoji_text_play: str
    emoji_text_music: str
    emoji_text_controls: str
    emoji_text_general: str
    emoji_text_started: str
    emoji_text_title: str
    emoji_text_duration: str
    emoji_text_requested: str
    emoji_text_queue: str
    emoji_text_position: str
    emoji_text_queue_full: str
    emoji_text_error: str
    emoji_text_settings: str
    emoji_text_statistics: str
    emoji_text_users: str
    emoji_text_groups: str
    emoji_text_active: str

    @classmethod
    def load(cls) -> "Settings":
        return cls(
            api_id=int(
                required("API_ID")
            ),

            api_hash=required(
                "API_HASH"
            ),

            bot_token=required(
                "BOT_TOKEN"
            ),

            string_session=required(
                "STRING_SESSION"
            ),

            owner_id=int(
                required("OWNER_ID")
            ),

            owner_username=os.getenv(
                "OWNER_USERNAME",
                "",
            ),

            mongo_uri=required(
                "MONGO_DB_URI"
            ),

            mongo_db_name=os.getenv(
                "MONGO_DB_NAME",
                "Shizu",
            ),

            bot_name="Shizu",

            bot_username=os.getenv(
                "BOT_USERNAME",
                "",
            ),

            start_img_url=os.getenv(
                "START_IMG_URL",
                "",
            ),

            log_group_id=optional_int(
                "LOG_GROUP_ID"
            ),

            support_group=os.getenv(
                "SUPPORT_GROUP",
                "",
            ),

            support_channel=os.getenv(
                "SUPPORT_CHANNEL",
                "",
            ),

            music_api_url=os.getenv(
                "MUSIC_API_URL",
                "https://api01.shrutibots.site",
            ).rstrip("/"),

            music_api_key=os.getenv(
                "MUSIC_API_KEY",
                "",
            ),

            max_queue_size=int(
                os.getenv(
                    "MAX_QUEUE_SIZE",
                    "60",
                )
            ),

            max_playlists_per_user=int(
                os.getenv(
                    "MAX_PLAYLISTS_PER_USER",
                    "25",
                )
            ),

            max_tracks_per_playlist=int(
                os.getenv(
                    "MAX_TRACKS_PER_PLAYLIST",
                    "150",
                )
            ),

            log_level=os.getenv(
                "LOG_LEVEL",
                "INFO",
            ),

            emoji_add_group=os.getenv("EMOJI_ADD_GROUP", ""),
            emoji_help=os.getenv("EMOJI_HELP", ""),
            emoji_owner=os.getenv("EMOJI_OWNER", ""),
            emoji_channel=os.getenv("EMOJI_CHANNEL", ""),
            emoji_support=os.getenv("EMOJI_SUPPORT", ""),
            emoji_music=os.getenv("EMOJI_MUSIC", ""),
            emoji_controls=os.getenv("EMOJI_CONTROLS", ""),
            emoji_general=os.getenv("EMOJI_GENERAL", ""),
            emoji_back=os.getenv("EMOJI_BACK", ""),
            emoji_close=os.getenv("EMOJI_CLOSE", ""),
            emoji_pause=os.getenv("EMOJI_PAUSE", ""),
            emoji_resume=os.getenv("EMOJI_RESUME", ""),
            emoji_replay=os.getenv("EMOJI_REPLAY", ""),
            emoji_skip=os.getenv("EMOJI_SKIP", ""),
            emoji_stop=os.getenv("EMOJI_STOP", ""),
            emoji_restart=os.getenv("EMOJI_RESTART", ""),
            emoji_cancel=os.getenv("EMOJI_CANCEL", ""),
            emoji_text_hey=os.getenv("EMOJI_TEXT_HEY", ""),
            emoji_text_play=os.getenv("EMOJI_TEXT_PLAY", ""),
            emoji_text_music=os.getenv("EMOJI_TEXT_MUSIC", ""),
            emoji_text_controls=os.getenv("EMOJI_TEXT_CONTROLS", ""),
            emoji_text_general=os.getenv("EMOJI_TEXT_GENERAL", ""),
            emoji_text_started=os.getenv("EMOJI_TEXT_STARTED", ""),
            emoji_text_title=os.getenv("EMOJI_TEXT_TITLE", ""),
            emoji_text_duration=os.getenv("EMOJI_TEXT_DURATION", ""),
            emoji_text_requested=os.getenv("EMOJI_TEXT_REQUESTED", ""),
            emoji_text_queue=os.getenv("EMOJI_TEXT_QUEUE", ""),
            emoji_text_position=os.getenv("EMOJI_TEXT_POSITION", ""),
            emoji_text_queue_full=os.getenv("EMOJI_TEXT_QUEUE_FULL", ""),
            emoji_text_error=os.getenv("EMOJI_TEXT_ERROR", ""),
            emoji_text_settings=os.getenv("EMOJI_TEXT_SETTINGS", ""),
            emoji_text_statistics=os.getenv("EMOJI_TEXT_STATISTICS", ""),
            emoji_text_users=os.getenv("EMOJI_TEXT_USERS", ""),
            emoji_text_groups=os.getenv("EMOJI_TEXT_GROUPS", ""),
            emoji_text_active=os.getenv("EMOJI_TEXT_ACTIVE", ""),
        )


settings = Settings.load()