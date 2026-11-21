<#
==========================================================================
 AI EMERGENCY HEALTH ASSISTANT - PORTABLE TCP HTTP SERVER
 ITM University Gwalior | Dept. of CSA | SOET
 Built with System.Net.Sockets.TcpListener for 100% compatibility across
 all Windows environments and security sandboxes!
==========================================================================
#>

param (
    [int]$Port = 8080
)

$baseDir = $PSScriptRoot
if (-not $baseDir) { $baseDir = Get-Location }

# Source clinical triage rules
. "$baseDir\run_tests.ps1" | Out-Null

$ip = [System.Net.IPAddress]::Loopback
$server = New-Object System.Net.Sockets.TcpListener($ip, $Port)

try {
    $server.Start()
    Write-Host "==============================================================" -ForegroundColor Cyan
    Write-Host "  AI EMERGENCY HEALTH ASSISTANT - HTTP & REST SERVER" -ForegroundColor White
    Write-Host "  ITM University Gwalior | Dept. of CSA | SOET" -ForegroundColor Yellow
    Write-Host "==============================================================" -ForegroundColor Cyan
    Write-Host "  Serving directory : $baseDir" -ForegroundColor White
    Write-Host "  Local Web UI      : http://localhost:$Port/" -ForegroundColor Green
    Write-Host "  API Healthcheck   : http://localhost:$Port/api/health" -ForegroundColor Green
    Write-Host "  API Chat Endpoint : http://localhost:$Port/api/chat (POST)" -ForegroundColor Green
    Write-Host "==============================================================" -ForegroundColor Cyan
    Write-Host "Server is running. Press Ctrl+C to stop.`n" -ForegroundColor DarkGray
} catch {
    Write-Error "Failed to start TCP Listener on port $Port : $_"
    exit 1
}

function Send-HttpResponse {
    param (
        [System.IO.Stream]$Stream,
        [int]$StatusCode = 200,
        [string]$StatusText = "OK",
        [string]$ContentType = "application/json; charset=utf-8",
        [byte[]]$BodyBytes = @()
    )

    $header = "HTTP/1.1 $StatusCode $StatusText`r`n"
    $header += "Content-Type: $ContentType`r`n"
    $header += "Content-Length: $($BodyBytes.Length)`r`n"
    $header += "Access-Control-Allow-Origin: *`r`n"
    $header += "Access-Control-Allow-Methods: GET, POST, OPTIONS`r`n"
    $header += "Access-Control-Allow-Headers: Content-Type, Authorization`r`n"
    $header += "Connection: close`r`n`r`n"

    $headerBytes = [System.Text.Encoding]::UTF8.GetBytes($header)
    $Stream.Write($headerBytes, 0, $headerBytes.Length)
    if ($BodyBytes.Length -gt 0) {
        $Stream.Write($BodyBytes, 0, $BodyBytes.Length)
    }
    $Stream.Flush()
}

try {
    while ($true) {
        $client = $server.AcceptTcpClient()
        $stream = $client.GetStream()
        $reader = New-Object System.IO.StreamReader($stream, [System.Text.Encoding]::UTF8)

        # Read Request Line
        $requestLine = $reader.ReadLine()
        if ([string]::IsNullOrEmpty($requestLine)) {
            $client.Close()
            continue
        }

        $parts = $requestLine -split " "
        $method = $parts[0]
        $rawPath = if ($parts.Length -gt 1) { $parts[1] } else { "/" }
        $urlPath = $rawPath.Split('?')[0]

        # Read Headers
        $contentLength = 0
        while ($line = $reader.ReadLine()) {
            if ($line -eq "") { break }
            if ($line.ToLower().StartsWith("content-length:")) {
                $contentLength = [int]($line.Split(':')[1].Trim())
            }
        }

        # Handle Preflight OPTIONS
        if ($method -eq "OPTIONS") {
            Send-HttpResponse -Stream $stream -StatusCode 204 -StatusText "No Content"
            $client.Close()
            continue
        }

        # API: Healthcheck
        if ($urlPath -eq "/api/health" -and $method -eq "GET") {
            $statusObj = @{
                status = "healthy"
                service = "AI Emergency Health Assistant"
                institution = "ITM University Gwalior"
                version = "1.0.0"
                runtime = "PowerShell TcpListener"
            }
            $jsonStr = $statusObj | ConvertTo-Json
            $bytes = [System.Text.Encoding]::UTF8.GetBytes($jsonStr)
            Send-HttpResponse -Stream $stream -StatusCode 200 -ContentType "application/json" -BodyBytes $bytes
            $client.Close()
            continue
        }

        # API: Test Cases
        if ($urlPath -eq "/api/test-cases" -and $method -eq "GET") {
            $testCasesJson = Get-Content "$baseDir\test_cases.json" -Raw -ErrorAction SilentlyContinue
            if (-not $testCasesJson) { $testCasesJson = '[]' }
            $bytes = [System.Text.Encoding]::UTF8.GetBytes($testCasesJson)
            Send-HttpResponse -Stream $stream -StatusCode 200 -ContentType "application/json" -BodyBytes $bytes
            $client.Close()
            continue
        }

        # API: Chat Endpoint (POST)
        if ($urlPath -eq "/api/chat" -and $method -eq "POST") {
            $body = ""
            if ($contentLength -gt 0) {
                $charBuffer = New-Object char[] $contentLength
                $readTotal = 0
                while ($readTotal -lt $contentLength) {
                    $readCount = $reader.Read($charBuffer, $readTotal, ($contentLength - $readTotal))
                    if ($readCount -le 0) { break }
                    $readTotal += $readCount
                }
                $body = New-Object string ($charBuffer, 0, $readTotal)
            }

            $query = ""
            try {
                $parsed = $body | ConvertFrom-Json
                $query = $parsed.query
            } catch {}

            $triageResult = Evaluate-ClinicalRules -Query $query
            $jsonResponse = $triageResult | ConvertTo-Json -Depth 5
            $bytes = [System.Text.Encoding]::UTF8.GetBytes($jsonResponse)
            Send-HttpResponse -Stream $stream -StatusCode 200 -ContentType "application/json" -BodyBytes $bytes
            $client.Close()
            continue
        }

        # Static Files Serving
        $localPath = $urlPath.TrimStart('/')
        if ([string]::IsNullOrWhiteSpace($localPath)) { $localPath = "index.html" }
        $filePath = Join-Path $baseDir $localPath

        if (Test-Path $filePath -PathType Leaf) {
            $ext = [System.IO.Path]::GetExtension($filePath).ToLower()
            $contentType = switch ($ext) {
                ".html" { "text/html; charset=utf-8" }
                ".css"  { "text/css; charset=utf-8" }
                ".js"   { "application/javascript; charset=utf-8" }
                ".json" { "application/json; charset=utf-8" }
                ".png"  { "image/png" }
                ".jpg"  { "image/jpeg" }
                ".svg"  { "image/svg+xml" }
                default { "text/plain; charset=utf-8" }
            }
            $fileBytes = [System.IO.File]::ReadAllBytes($filePath)
            Send-HttpResponse -Stream $stream -StatusCode 200 -ContentType $contentType -BodyBytes $fileBytes
        } else {
            $errBytes = [System.Text.Encoding]::UTF8.GetBytes("404 Not Found")
            Send-HttpResponse -Stream $stream -StatusCode 404 -StatusText "Not Found" -ContentType "text/plain" -BodyBytes $errBytes
        }

        $client.Close()
    }
} finally {
    $server.Stop()
}
