# Spotify Ad Muter

Small Windows-only helper that watches Spotify's media session and mutes the Spotify process when the current track looks like an ad or promo.

## What it checks

The current detector is intentionally simple: it treats a track as an ad when the album field is blank or `-` and the duration is short.

## Requirements

- Python 3.14.5
- `pycaw`
- `winrt-Windows.Foundation.Collections`
- `winrt-Windows.Media.Control`
- `pyinstaller`

The script imports `winrt.windows.media.control`.

## Install

```powershell
python -m pip install -r requirements.txt
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

## Build An EXE

If you want a one-click version for a friend, build a single executable with:

```powershell
.\build_exe.ps1
```

That will install the required packages and write the release executable to `dist\SpotifyAdBlocker.exe`.

## Publish A GitHub Release

1. Push this repo to GitHub.
2. Create a tag like `v1.0.0` locally.
3. Push the tag.
4. The GitHub Action will build the exe and attach it to the release automatically.

Example:

```powershell
git tag v1.0.0
git push origin v1.0.0
```

If you want to create the release manually instead, upload `dist\SpotifyAdBlocker.exe` as the release asset.

## Notes

- This is heuristic-based, not perfect detection.
- Generic CTA titles and very short tracks are treated as likely ads.
- If you see false positives, the keyword list in `is_ad()` is the first place to tune.
- Log rotation is enabled (up to ~1 MB per file with 2 backups).
- On graceful shutdown, the script attempts a rollback by unmuting Spotify before exit.