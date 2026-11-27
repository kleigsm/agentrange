# 重启 Ollama 服务，确保：
#   1. 模型目录指向 D 盘
#   2. 下载走代理（如果代理开着）
# 用法：右键“使用 PowerShell 运行”，或在终端执行
#   powershell -ExecutionPolicy Bypass -File .\scripts\start_ollama.ps1

$ErrorActionPreference = 'Continue'

$env:OLLAMA_MODELS = 'D:\ollama\models'
$env:HTTPS_PROXY = 'http://127.0.0.1:10808'
$env:HTTP_PROXY = 'http://127.0.0.1:10808'

Get-Process ollama* -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 3

Start-Process -FilePath "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" `
    -ArgumentList 'serve' -WindowStyle Hidden
Start-Sleep -Seconds 6

& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" list
