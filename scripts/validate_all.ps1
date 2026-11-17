$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$cudaBin = 'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\bin'
$env:PATH = "$cudaBin\x64;$cudaBin;$env:PATH"
$exe = Join-Path $root 'llama.cpp\build\bin\llama-cli.exe'
$prompt = 'Explain in two sentences what a CPU cache is.'
$rows = @(
    @{ Model='gemma3-4b'; Quant='native' }, @{ Model='gemma3-4b'; Quant='q8_0' },
    @{ Model='gemma3-4b'; Quant='q6_k' }, @{ Model='gemma3-4b'; Quant='q4_k_m' },
    @{ Model='gemma3-4b'; Quant='q2_k' }, @{ Model='qwen3-4b'; Quant='native' },
    @{ Model='qwen3-4b'; Quant='q8_0' }, @{ Model='qwen3-4b'; Quant='q6_k' },
    @{ Model='qwen3-4b'; Quant='q4_k_m' }, @{ Model='qwen3-4b'; Quant='q2_k' }
)
foreach ($row in $rows) {
    $name = "$($row.Model)-$($row.Quant)"
    $modelPath = Join-Path $root "models\$($row.Model)\$name.gguf"
    $logPath = Join-Path $root "results\raw\$name-validation.log"
    $argsList = @('-m', $modelPath, '-ngl', 'all', '-fit', 'off', '-c', '4096', '-n', '96', '-p', $prompt, '-st', '--temp', '0', '--check-tensors', '--no-display-prompt', '--simple-io', '-v')
    if ($row.Model -eq 'qwen3-4b') { $argsList += @('--chat-template-kwargs', '{"enable_thinking":false}') }
    & $exe @argsList 2>&1 | Out-File -LiteralPath $logPath -Encoding utf8
    if ($LASTEXITCODE -ne 0) { throw "Validation failed: $name (exit $LASTEXITCODE)" }
    Write-Host "Validated $name"
}
