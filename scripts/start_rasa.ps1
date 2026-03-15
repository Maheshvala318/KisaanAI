param (
    [switch]$AutoKill,
    [switch]$UpdateEndpoints
)

Write-Host "Starting Rasa Server..." -ForegroundColor Cyan
python -m rasa run --enable-api --cors "*" --port 5005
