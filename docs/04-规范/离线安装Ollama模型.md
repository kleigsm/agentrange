---
tags: [规范, 运维]
---

# 当 `ollama pull` 反复 digest mismatch 时

## 症状

- pull 到 100%
- `verifying sha256 digest`
- `Error: digest mismatch, file must be downloaded again`
- 重试多次，每次下满但哈希都不对

## 原因

Ollama 的分片下载器在坏线路上会把错误数据组装进 blob。它只在下完后校验，失败就整包重下——坏线路下永远过不去。

## 解法：curl 下同一个官方 blob，自己校验

### 1. 取 manifest

```powershell
$px = 'http://127.0.0.1:10808'
$mf = 'D:\ollama\manifest.json'
curl.exe -sS -x $px -H "Accept: application/vnd.docker.distribution.manifest.v2+json" `
  https://registry.ollama.ai/v2/library/<model>/manifests/<tag> -o $mf
```

### 2. 找最大的 layer

```powershell
$j = Get-Content $mf -Raw | ConvertFrom-Json
$big = $j.layers | Sort-Object size -Descending | Select-Object -First 1
$big.digest; $big.size
```

### 3. 下载并校验

```powershell
$url = "https://registry.ollama.ai/v2/library/<model>/blobs/$($big.digest)"
curl.exe -L --retry 5 -C - -x $px -o D:\ollama\model.blob $url
(Get-FileHash D:\ollama\model.blob -Algorithm SHA256).Hash.ToLower()
# 必须等于 $big.digest 去掉 sha256:
```

### 4. 放入 blob 目录

```powershell
Move-Item D:\ollama\model.blob "D:\ollama\models\blobs\sha256-<digest>" -Force
```

### 5. 写 manifest

```powershell
New-Item -ItemType Directory -Force "D:\ollama\models\manifests\registry.ollama.ai\library\<model>" | Out-Null
Copy-Item $mf "D:\ollama\models\manifests\registry.ollama.ai\library\<model>\<tag>" -Force
```

### 6. 补小 blob（config / template / license）

manifest 里的每个 digest 都必须在 `blobs\` 里存在，否则 `ollama list` 不显示模型。

```powershell
foreach ($d in @($j.config.digest) + @($j.layers.digest)) {
  $h = $d -replace 'sha256:', ''
  $path = "D:\ollama\models\blobs\sha256-$h"
  if (Test-Path $path) { continue }
  curl.exe -sSL -x $px -o $path "https://registry.ollama.ai/v2/library/<model>/blobs/$d"
}
```

### 7. 重启并验证

```powershell
Get-Process ollama* | Stop-Process -Force
$env:OLLAMA_MODELS = 'D:\ollama\models'
$env:HTTPS_PROXY = 'http://127.0.0.1:10808'
Start-Process "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" -ArgumentList 'serve' -WindowStyle Hidden
ollama list
ollama run <model> "Reply with OK"
```

## 注意

- 必须校验 SHA256；哈希不对的 blob 会让模型加载失败
- 这个方法仍然使用 Ollama 官方 registry，只是换了下载器
- 下载前确认 `OLLAMA_MODELS` 指向正确的模型目录
