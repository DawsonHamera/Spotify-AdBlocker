# Spotify Ad Muter

Small Windows-only helper that watches Spotify's media session and mutes the Spotify process when the current track looks like an ad or promo.

## What it checks

The current detector is intentionally simple: it treats a track as an ad when the album field is blank or `-` and the duration is short.

## Requirements

- Python 3.14.5
- `pycaw`
- `winsdk`
- `winrt-Windows.Foundation.Collections`

The script imports `winrt.windows.media.control`.

## Install

```powershell
python -m pip install pycaw winsdk winrt-Windows.Foundation.Collections
```

If Spotify's media session is visible to Windows, the script will log what it sees and keep running in a monitor loop. Logs are written to `logs\spotify_ad_muter.log`.

## Run

```powershell
python -u main.py
```

## Live Logs

```powershell
show_live_logs.bat
```

## Notes

- This is heuristic-based, not perfect detection.
- Generic CTA titles and very short tracks are treated as likely ads.
- If you see false positives, the keyword list in `is_ad()` is the first place to tune.
- Log rotation is enabled (up to ~1 MB per file with 2 backups).
- On graceful shutdown, the script attempts a rollback by unmuting Spotify before exit.