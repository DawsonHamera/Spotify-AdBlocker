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

If Spotify's media session is visible to Windows, the script will log what it sees and keep running in a monitor loop. In source runs, logs are written to `logs\spotify_ad_muter.log`; in the packaged `.exe`, logs are written next to the executable in `dist\logs\spotify_ad_muter.log`.

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

## Start Automatically

The packaged `.exe` enables a user-level autostart entry on its first launch, so there is no separate installer step.

To remove that autostart entry with the same exe:

```powershell
.\dist\SpotifyAdBlocker.exe --uninstall
```

After that, delete the `dist` folder if you want a full manual cleanup of the app files.

## Publish A GitHub Release

For now, use the local build artifact from `build_exe.ps1` as the release file. That is the known-good exe.

1. Run `.uild_exe.ps1` locally.
2. Upload `dist\SpotifyAdBlocker.exe` to a GitHub Release manually.
3. Optionally tag the repo for version tracking, but do not rely on the tag build until it is verified.

Example:

```powershell
git tag v1.0.0
git push origin v1.0.0
```

Warning: the GitHub Actions build path has had WinRT packaging differences from the local build. Use the locally built exe for release assets until that path is fully proven.

## Notes

- This is heuristic-based, not perfect detection.
- Generic CTA titles and very short tracks are treated as likely ads.
- If you see false positives, the keyword list in `is_ad()` is the first place to tune.
- Log rotation is enabled (up to ~1 MB per file with 2 backups).
- On graceful shutdown, the script attempts a rollback by unmuting Spotify before exit.