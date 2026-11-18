# Beeper Desktop - Italian UI Installer for Windows
$tmpDir = Join-Path $env:TEMP ("beeper-it-" + [System.Guid]::NewGuid().ToString())
$repoUrl = "https://github.com/PizzaRevolutions/beeper-desktop-italian.git"

try {
    Write-Host "Download del repository in corso..."
    git clone --depth 1 $repoUrl $tmpDir 2>$null
    if (-not (Test-Path $tmpDir)) {
        Write-Error "Impossibile clonare il repository. Assicurati che Git sia installato."
        return
    }

    python "$tmpDir\patch.py" $args
}
finally {
    if (Test-Path $tmpDir) {
        Remove-Item -Recurse -Force $tmpDir 2>$null
    }
}
