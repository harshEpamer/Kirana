# start-all.ps1 — Start all 8 FastAPI microservices in parallel
# Run from the project root: .\scripts\start-all.ps1
# Prerequisites: pip install -r requirements.txt in each service folder

$services = @(
    @{ name = "auth-service";      port = 8001; path = "backend\auth-service" },
    @{ name = "inventory-service"; port = 8002; path = "backend\inventory-service" },
    @{ name = "catalog-service";   port = 8003; path = "backend\catalog-service" },
    @{ name = "sales-service";     port = 8004; path = "backend\sales-service" },
    @{ name = "order-service";     port = 8005; path = "backend\order-service" },
    @{ name = "coupon-service";    port = 8006; path = "backend\coupon-service" },
    @{ name = "alert-service";     port = 8007; path = "backend\alert-service" },
    @{ name = "customer-service";  port = 8008; path = "backend\customer-service" }
)

Write-Host "Starting all Kirana microservices..." -ForegroundColor Green

foreach ($svc in $services) {
    $scriptBlock = {
        param($path, $port, $name)
        Set-Location $path
        Write-Host "Starting $name on port $port" -ForegroundColor Cyan
        uvicorn main:app --reload --port $port
    }
    Start-Job -Name $svc.name -ScriptBlock $scriptBlock -ArgumentList (Join-Path $PSScriptRoot "..\$($svc.path)"), $svc.port, $svc.name | Out-Null
    Write-Host "  Started $($svc.name) on port $($svc.port)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "All services started as background jobs." -ForegroundColor Green
Write-Host "Run 'Get-Job' to list jobs, 'Receive-Job -Name <name>' to see output." -ForegroundColor Gray
Write-Host ""
Write-Host "Health check URLs:" -ForegroundColor Cyan
foreach ($svc in $services) {
    Write-Host "  http://localhost:$($svc.port)/health"
}
