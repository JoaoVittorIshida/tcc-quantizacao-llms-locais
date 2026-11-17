$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$source = Join-Path $root 'llama.cpp'
$build = Join-Path $source 'build'
$cmake = Join-Path $root '.venv\Scripts\cmake.exe'
$ninja = Join-Path $root '.venv\Scripts\ninja.exe'
$cuda = 'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4'
$nvcc = Join-Path $cuda 'bin\nvcc.exe'
$vswhere = 'C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe'
$vs = & $vswhere -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
$vcvars = Join-Path $vs 'VC\Auxiliary\Build\vcvars64.bat'

foreach ($path in @($source, $cmake, $ninja, $nvcc, $vcvars)) {
    if (-not (Test-Path -LiteralPath $path)) { throw "Arquivo ausente: $path" }
}

# Importa o ambiente do compilador MSVC para esta sessão do PowerShell.
$variables = & cmd.exe /c "call `"$vcvars`" >nul && set"
if ($LASTEXITCODE -ne 0) { throw 'Falha ao configurar o compilador MSVC.' }
foreach ($line in $variables) {
    if ($line -match '^([^=]+)=(.*)$') {
        Set-Item -Path "Env:$($Matches[1])" -Value $Matches[2]
    }
}

$env:CUDAToolkit_ROOT = $cuda
& $cmake -S $source -B $build -G Ninja `
    "-DCMAKE_MAKE_PROGRAM=$ninja" `
    "-DCMAKE_CUDA_COMPILER=$nvcc" `
    '-DCMAKE_CUDA_ARCHITECTURES=120' `
    '-DCMAKE_BUILD_TYPE=Release' `
    '-DGGML_CUDA=ON' `
    '-DLLAMA_BUILD_TESTS=OFF' `
    '-DLLAMA_BUILD_EXAMPLES=ON' `
    '-DLLAMA_BUILD_SERVER=ON'
if ($LASTEXITCODE -ne 0) { throw 'Falha na configuração do llama.cpp.' }

& $cmake --build $build -j 8 --target llama-cli llama-bench llama-quantize llama-perplexity llama-server
if ($LASTEXITCODE -ne 0) { throw 'Falha na compilação do llama.cpp.' }
