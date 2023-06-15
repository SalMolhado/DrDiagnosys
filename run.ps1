$venvName = "venv"

if (Test-Path $venvName) {
    . $venvName/Scripts/Activate.ps1
    python main.py
} else {
    Write-Output "O ambiente virtual '$venvName' não existe."
}