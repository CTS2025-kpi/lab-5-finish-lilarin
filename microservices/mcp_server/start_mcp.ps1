Write-Host "=== STEP 1: Cleaning up old processes ===" -ForegroundColor Cyan
Stop-Process -Name "kubectl" -ErrorAction SilentlyContinue

Write-Host "=== STEP 2: Starting Port Forward (Background) ===" -ForegroundColor Cyan
$pfJob = Start-Process kubectl -ArgumentList "port-forward svc/mcp-server 8081:8000 -n lab2-microservices" -PassThru -NoNewWindow

Start-Sleep -Seconds 3

Write-Host "=== STEP 3: Starting MCP Inspector ===" -ForegroundColor Green
Write-Host "Target URL: http://localhost:8081/sse" -ForegroundColor Yellow

try {
    npx @modelcontextprotocol/inspector http://localhost:8081/sse
}
finally {
    Write-Host "`n=== SHUTDOWN: Stopping Port Forward ===" -ForegroundColor Red
    Stop-Process -Id $pfJob.Id -ErrorAction SilentlyContinue
}