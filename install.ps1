# Beeper Desktop - Italian UI Installer for Windows
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "🇮🇹  Beeper Desktop — Traduzione Italiana UI" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

$tmpDir = Join-Path $env:TEMP ("beeper-it-" + [System.Guid]::NewGuid().ToString())
$repoUrl = "https://github.com/PizzaRevolutions/beeper-desktop-italian.git"

try {
    Write-Host "⬇️  Download del repository..." -ForegroundColor Yellow
    git clone --depth 1 $repoUrl $tmpDir 2>$null
    if (-not (Test-Path $tmpDir)) {
        Write-Error "Impossibile clonare il repository. Assicurati che Git sia installato."
        return
    }

    Write-Host "⚡ Esecuzione della patch..." -ForegroundColor Green
    python "$tmpDir\patch.py" $args
    Write-Host ""
    Write-Host "✨ Fatto! Riapri Beeper Desktop e goditi l'interfaccia in italiano." -ForegroundColor Green
}
finally {
    if (Test-Path $tmpDir) {
        Remove-Item -Recurse -Force $tmpDir 2>$null
    }
}
