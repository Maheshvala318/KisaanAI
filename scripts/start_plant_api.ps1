Write-Host "Starting Plant Disease Model API..." -ForegroundColor Cyan
cd Image_model
uvicorn plant_model_service:app --host 0.0.0.0 --port 8001
