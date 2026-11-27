$ErrorActionPreference = 'Continue'
$ollama = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
$models = @('qwen2.5:7b', 'llama3.1:8b')

function Get-BlobSize {
    (Get-ChildItem 'D:\ollama\models\blobs' -File -ErrorAction SilentlyContinue |
        Measure-Object Length -Sum).Sum
}

foreach ($m in $models) {
    Write-Output "########## $m ##########"
    $done = $false
    for ($attempt = 1; $attempt -le 8; $attempt++) {
        $list = & $ollama list 2>&1
        if ($list -match [regex]::Escape($m)) {
            Write-Output "already installed: $m"
            $done = $true
            break
        }
        Write-Output "attempt $attempt for $m"
        $p = Start-Process -FilePath $ollama -ArgumentList @('pull', $m) -PassThru -WindowStyle Hidden
        $last = Get-BlobSize
        $stall = 0
        while (-not $p.HasExited) {
            Start-Sleep -Seconds 15
            $size = Get-BlobSize
            if ($size -le $last) {
                $stall++
            }
            else {
                $stall = 0
            }
            $last = $size
            if ($stall -ge 8) {
                Write-Output ("stalled at {0:N2} GB; restarting" -f ($size / 1GB))
                Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
                break
            }
        }
        if ($p.HasExited -and $p.ExitCode -eq 0) {
            $list = & $ollama list 2>&1
            if ($list -match [regex]::Escape($m)) {
                Write-Output "installed: $m"
                $done = $true
                break
            }
        }
        Start-Sleep -Seconds 5
    }
    if (-not $done) {
        Write-Output "FAILED: $m"
    }
}

Write-Output 'ALL DONE'
& $ollama list
