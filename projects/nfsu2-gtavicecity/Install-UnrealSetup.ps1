param(
    [switch]$SkipVisualStudio
)

$ErrorActionPreference = "Stop"

function Write-Step([string]$Message) {
    Write-Host "`n==> $Message" -ForegroundColor Cyan
}

Write-Step "Checking Windows Package Manager"
$winget = Get-Command winget -ErrorAction SilentlyContinue
if (-not $winget) {
    throw "winget is not available. Install App Installer from Microsoft Store, then rerun this script."
}

Write-Step "Installing Epic Games Launcher"
$launcher = Get-Package -Name "Epic Games Launcher" -ErrorAction SilentlyContinue
if ($launcher) {
    Write-Host "Epic Games Launcher is already installed."
} else {
    winget install --exact --id EpicGames.EpicGamesLauncher --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) {
        throw "Epic Games Launcher installation failed (winget exit code $LASTEXITCODE)."
    }
}

if (-not $SkipVisualStudio) {
    Write-Step "Installing Visual Studio 2022 Build Tools"
    winget install --exact --id Microsoft.VisualStudio.2022.BuildTools `
        --override "--wait --passive --add Microsoft.VisualStudio.Workload.NativeDesktop --includeRecommended" `
        --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) {
        throw "Visual Studio Build Tools installation failed (winget exit code $LASTEXITCODE)."
    }
}

Write-Step "Opening Unreal Engine 5.5.4 installation action"
$engineUri = "com.epicgames.launcher://apps/UE_5.5.4?action=install"
Start-Process $engineUri

Write-Host ""
Write-Host "The Epic Games Launcher should now open." -ForegroundColor Green
Write-Host "Sign in, then install Unreal Engine 5.5.4 from Library -> Engine Versions."
Write-Host "After installation, open:"
Write-Host "  C:\Users\joshu\Documents\GitHub\ClaudeProjects\.tools\unreal-engine-mcp\FlopperamUnrealMCP\FlopperamUnrealMCP.uproject"
