$ErrorActionPreference = 'Stop'

Set-StrictMode -Version Latest

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

python -m pip install -r requirements.txt
python -m PyInstaller --noconfirm --clean --onefile --windowed --name SpotifyAdBlocker --collect-all pycaw --collect-all winrt main.py