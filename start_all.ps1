Write-Host "Starting KisaanAI Health Chatbot System..." -ForegroundColor Yellow

# Start Action Server in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "powershell -ExecutionPolicy Bypass -File .\scripts\start_actions.ps1"

# Start Plant API in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "powershell -ExecutionPolicy Bypass -File .\scripts\start_plant_api.ps1"

# Start Rasa Server in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "powershell -ExecutionPolicy Bypass -File .\scripts\start_rasa.ps1"

# Start Frontend in current window or new one
Write-Host "Starting Frontend..." -ForegroundColor Cyan
cd frontend
npm start
