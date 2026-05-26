$ErrorActionPreference = 'Stop'

Set-StrictMode -Version Latest

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Get-Process SpotifyAdBlocker -ErrorAction SilentlyContinue | Stop-Process -Force

python -m pip install -r requirements.txt
python -m PyInstaller --noconfirm --clean --onefile --windowed --name SpotifyAdBlocker --runtime-hook winrt_runtime_hook.py --collect-all pycaw --collect-all winrt main.py