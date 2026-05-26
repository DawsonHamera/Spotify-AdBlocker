import asyncio
import logging
import sys
from logging.handlers import RotatingFileHandler
from dataclasses import dataclass
from pathlib import Path

from pycaw.pycaw import AudioUtilities
from winrt.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager as MediaManager
)

ENABLE_LOGGING = True

APP_ROOT = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
LOG_DIR_PATH = APP_ROOT / "logs"
LOG_FILE_PATH = LOG_DIR_PATH / "spotify_ad_muter.log"
LOG_MAX_BYTES = 1_000_000
LOG_BACKUP_COUNT = 2

LOGGER = logging.getLogger("spotify_ad_muter")

# Idle mode is used when Spotify is not running. This keeps background
# CPU usage low when launched at sign-in.
IDLE_POLL_SECONDS = 5
ACTIVE_POLL_SECONDS = 1
SESSION_MISS_LIMIT = 8


def setup_logging():
    LOG_DIR_PATH.mkdir(parents=True, exist_ok=True)
    LOGGER.setLevel(logging.INFO)
    LOGGER.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        LOG_FILE_PATH,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    LOGGER.addHandler(file_handler)

    if not ENABLE_LOGGING:
        LOGGER.info("Spotify Ad Muter started with logging disabled")
        LOGGER.setLevel(logging.CRITICAL)
    else:
        LOGGER.info("Spotify Ad Muter started (background mode)")


def log(msg):
    if ENABLE_LOGGING:
        LOGGER.info(msg)


def to_seconds(value):
    if value is None:
        return 0.0

    if hasattr(value, "total_seconds"):
        return float(value.total_seconds())

    try:
        return float(value)
    except Exception:
        return 0.0


@dataclass
class MediaState:
    title: str = ""
    artist: str = ""
    album_title: str = ""
    album_artist: str = ""
    track_number: int = 0
    duration_seconds: float = 0.0
    position_seconds: float = 0.0
    playback_status: str = ""


async def get_spotify_session_from_manager(manager):
    sessions = manager.get_sessions()

    log(f"Active sessions: {len(sessions)}")

    for s in sessions:
        try:
            source = s.source_app_user_model_id.lower()

            if "spotify" in source:
                log("Spotify session found")
                return s
        except Exception:
            pass

    return None


def is_spotify_process_running():
    try:
        sessions = AudioUtilities.GetAllSessions()
        for s in sessions:
            try:
                if s.Process and s.Process.name().lower() == "spotify.exe":
                    return True
            except Exception:
                pass
    except Exception as e:
        log(f"Process scan error: {e}")
    return False


# -----------------------------
# GET MEDIA INFO
# -----------------------------
async def get_media(session):
    try:
        props = await session.try_get_media_properties_async()

        playback = session.get_playback_info()
        timeline = session.get_timeline_properties()

        return MediaState(
            title=(props.title or "").strip(),
            artist=(props.artist or "").strip(),
            album_title=(getattr(props, "album_title", "") or "").strip(),
            album_artist=(getattr(props, "album_artist", "") or "").strip(),
            track_number=int(getattr(props, "track_number", 0) or 0),
            duration_seconds=to_seconds(getattr(timeline, "end_time", 0)),
            position_seconds=to_seconds(getattr(timeline, "position", 0)),
            playback_status=str(getattr(playback, "playback_status", "") or ""),
        )
    except Exception as e:
        log(f"Metadata error: {e}")
        return MediaState()


# -----------------------------
# MUTE SPOTIFY ONLY
# -----------------------------
def set_spotify_mute(mute: bool):
    sessions = AudioUtilities.GetAllSessions()

    for s in sessions:
        try:
            if s.Process and s.Process.name().lower() == "spotify.exe":
                s.SimpleAudioVolume.SetMute(mute, None)
                log(f"Spotify mute = {mute}")
        except Exception as e:
            log(f"Mute error: {e}")


def is_spotify_muted() -> bool:
    sessions = AudioUtilities.GetAllSessions()

    for s in sessions:
        try:
            if s.Process and s.Process.name().lower() == "spotify.exe":
                return bool(s.SimpleAudioVolume.GetMute())
        except Exception as e:
            log(f"Mute state check error: {e}")

    return False


# -----------------------------
# DETECT AD
# -----------------------------
def normalize(text: str) -> str:
    return " ".join((text or "").lower().split())


def is_ad(media: MediaState):
    log(
        "Now playing: "
        f"{media.title} - {media.artist} | album={media.album_title or '-'} | "
        f"track={media.track_number} | duration={media.duration_seconds:.0f}s | "
        f"status={media.playback_status or '-'}"
    )

    very_short_track = 0 < media.duration_seconds <= 35

    if normalize(media.album_title) in {"", "-"} and very_short_track:
        return True

    return False


# -----------------------------
# MAIN LOOP
# -----------------------------
async def main():
    muted = False
    media_manager = None
    session_misses = 0
    idle_mode = True
    startup_recovery_done = False

    try:
        while True:
            try:
                if idle_mode:
                    if not is_spotify_process_running():
                        await asyncio.sleep(IDLE_POLL_SECONDS)
                        continue

                    log("Spotify detected, switching to active mode")
                    idle_mode = False
                    session_misses = 0

                if media_manager is None:
                    media_manager = await MediaManager.request_async()

                session = await get_spotify_session_from_manager(media_manager)

                if not session:
                    session_misses += 1
                    if session_misses >= SESSION_MISS_LIMIT:
                        if muted:
                            set_spotify_mute(False)
                            muted = False
                            log("Rollback: unmuted before returning to idle mode")
                        media_manager = None
                        idle_mode = True
                        log("Spotify session missing, returning to idle mode")
                        await asyncio.sleep(IDLE_POLL_SECONDS)
                        continue

                    await asyncio.sleep(ACTIVE_POLL_SECONDS)
                    continue

                session_misses = 0

                if not startup_recovery_done:
                    startup_recovery_done = True
                    if is_spotify_muted():
                        log("Startup recovery: Spotify was muted, unmuting once")
                        set_spotify_mute(False)

                media = await get_media(session)

                ad = is_ad(media)

                log(f"State -> ad={ad}, muted={muted}")

                if ad and not muted:
                    log("MUTING Spotify (ad)")
                    set_spotify_mute(True)
                    muted = True

                elif not ad and muted:
                    log("UNMUTING Spotify (music)")
                    set_spotify_mute(False)
                    muted = False

                await asyncio.sleep(ACTIVE_POLL_SECONDS)

            except Exception as e:
                log(f"Loop error: {e}")
                media_manager = None
                idle_mode = True
                await asyncio.sleep(2)

    finally:
        log("Executing shutdown rollback")
        if muted:
            try:
                set_spotify_mute(False)
                log("Rollback: unmuted Spotify on shutdown")
            except Exception as e:
                log(f"Rollback error while unmuting: {e}")

        log("Spotify Ad Muter stopped")


if __name__ == "__main__":
    setup_logging()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log("Interrupted by user")