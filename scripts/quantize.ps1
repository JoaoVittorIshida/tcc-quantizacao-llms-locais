$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$quantizer = Join-Path $root 'llama.cpp\build\bin\llama-quantize.exe'
$cudaBin = 'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\bin'
$env:PATH = "$cudaBin\x64;$cudaBin;$env:PATH"
$logDir = Join-Path $root 'results\raw'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

if (-not (Test-Path -LiteralPath $quantizer)) { throw "Executável ausente: $quantizer" }

$models = @(
    @{ Name = 'gemma3-4b'; NativeSha256 = '06F32227DA36840C82C13A24C3EF6F307327DA3643FA5C4C957445B8E8770090' },
    @{ Name = 'qwen3-4b'; NativeSha256 = 'FAC55A00FD3799B70EF03BD6A6F32F1F72B087FA315035789F69F8F2FE78CA76' }
)
$presets = @('Q8_0', 'Q6_K', 'Q4_K_M', 'Q2_K')

foreach ($model in $models) {
    $name = $model.Name
    $modelDir = Join-Path $root "models\$name"
    $native = Join-Path $modelDir "$name-native.gguf"
    if (-not (Test-Path -LiteralPath $native)) { throw "Baseline ausente: $native" }

    $actualHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $native).Hash
    if ($actualHash -ne $model.NativeSha256) { throw "Hash do baseline mudou: $native" }

    foreach ($preset in $presets) {
        $output = Join-Path $modelDir "$name-$($preset.ToLowerInvariant()).gguf"
        $log = Join-Path $logDir "$name-$($preset.ToLowerInvariant())-quantization.log"
        if (Test-Path -LiteralPath $output) { throw "Saída já existe: $output" }

        @(
            "input=$native",
            "input_sha256=$actualHash",
            "output=$output",
            "preset=$preset",
            "command=llama-quantize.exe `"$native`" `"$output`" $preset"
        ) | Set-Content -LiteralPath $log -Encoding utf8

        Write-Output "Quantizando $name em $preset..."
        & $quantizer $native $output $preset *>> $log
        if ($LASTEXITCODE -ne 0) { throw "Falha em $name $preset. Consulte $log" }
        if (-not (Test-Path -LiteralPath $output)) { throw "Saída ausente: $output" }
        Write-Output "Concluído: $output ($((Get-Item -LiteralPath $output).Length) bytes)"
    }
}
