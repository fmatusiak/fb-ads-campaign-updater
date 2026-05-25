param(
    [string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"

Write-Host "Building Auto FB Boost release with PyInstaller..."

& $PythonExe -m PyInstaller --noconfirm --clean --distpath output --workpath build main.spec

Write-Host ""
Write-Host "Build finished."
Write-Host "Share the whole folder:"
Write-Host "output\\Auto FB Boost"
Write-Host ""
Write-Host "Keep config.json next to Auto FB Boost.exe before running."
