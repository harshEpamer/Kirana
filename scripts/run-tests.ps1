# ─────────────────────────────────────────────────────────────────────────────
# scripts/run-tests.ps1
# Runs pytest for each backend service in isolation and generates a report.
# Usage: .\scripts\run-tests.ps1
# ─────────────────────────────────────────────────────────────────────────────

$ROOT = Split-Path -Parent $PSScriptRoot
$REPORTS_DIR = Join-Path $ROOT "test-reports"

if (-not (Test-Path $REPORTS_DIR)) {
    New-Item -ItemType Directory -Path $REPORTS_DIR | Out-Null
}

$services = @(
    "auth-service",
    "inventory-service",
    "catalog-service",
    "sales-service",
    "order-service",
    "coupon-service",
    "alert-service",
    "customer-service"
)

$summary = @()

foreach ($svc in $services) {
    $svcPath  = Join-Path $ROOT "backend" $svc
    $xmlReport = Join-Path $REPORTS_DIR "$svc-results.xml"

    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host " Running tests: $svc" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

    Push-Location $svcPath
    python -m pytest tests/ -v --tb=short --junit-xml="$xmlReport" 2>&1
    $exitCode = $LASTEXITCODE
    Pop-Location

    $passed = 0; $failed = 0; $errors = 0
    if (Test-Path $xmlReport) {
        [xml]$xml = Get-Content $xmlReport
        $testsuite = $xml.testsuites.testsuite
        if ($null -eq $testsuite) { $testsuite = $xml.testsuite }
        if ($null -ne $testsuite) {
            $passed  = [int]$testsuite.tests - [int]$testsuite.failures - [int]$testsuite.errors - [int]$testsuite.skipped
            $failed  = [int]$testsuite.failures
            $errors  = [int]$testsuite.errors
        }
    }

    $status = if ($exitCode -eq 0) { "PASS" } else { "FAIL" }
    $color  = if ($exitCode -eq 0) { "Green" } else { "Red" }
    Write-Host "  Result: $status  (passed=$passed  failed=$failed  errors=$errors)" -ForegroundColor $color

    $summary += [PSCustomObject]@{
        Service = $svc
        Status  = $status
        Passed  = $passed
        Failed  = $failed
        Errors  = $errors
    }
}

# ── Generate Markdown report ──────────────────────────────────────────────────
$reportPath = Join-Path $REPORTS_DIR "REPORT.md"
$totalPassed = ($summary | Measure-Object -Property Passed -Sum).Sum
$totalFailed = ($summary | Measure-Object -Property Failed -Sum).Sum
$totalErrors = ($summary | Measure-Object -Property Errors -Sum).Sum
$overallStatus = if ($totalFailed -eq 0 -and $totalErrors -eq 0) { "✅ ALL PASS" } else { "❌ FAILURES DETECTED" }

$md = @"
# Kirana Test Report
**Date:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Overall Status:** $overallStatus

## Summary

| Service | Status | Passed | Failed | Errors |
|---|---|---|---|---|
"@

foreach ($row in $summary) {
    $icon = if ($row.Status -eq "PASS") { "✅" } else { "❌" }
    $md += "`n| $($row.Service) | $icon $($row.Status) | $($row.Passed) | $($row.Failed) | $($row.Errors) |"
}

$md += @"

## Totals
| Passed | Failed | Errors |
|---|---|---|
| $totalPassed | $totalFailed | $totalErrors |

## XML Reports
Individual JUnit XML reports are saved to ``test-reports/<service>-results.xml``.
"@

$md | Out-File -FilePath $reportPath -Encoding utf8

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host " FINAL SUMMARY — $overallStatus" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Yellow
$summary | Format-Table -AutoSize
Write-Host ""
Write-Host " Markdown report saved to: $reportPath" -ForegroundColor Yellow
