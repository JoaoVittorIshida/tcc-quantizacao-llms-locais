# Avaliação do impacto da quantização no desempenho e na eficiência de modelos de linguagem executados localmente

**Autor:** João Vittor Ishida de Sousa  
**Orientadora:** Profa. Dra. Wanessa Machado do Amaral  
**Instituição:** IFSP – Campus Piracicaba  
**Curso:** Engenharia de Computação  
**Ano:** 2026

**Repositório:** [JoaoVittorIshida/tcc-quantizacao-llms-locais](https://github.com/JoaoVittorIshida/tcc-quantizacao-llms-locais)  
**Versão utilizada no trabalho:** [v1.0.0](https://github.com/JoaoVittorIshida/tcc-quantizacao-llms-locais/releases/tag/v1.0.0)

Artefatos do experimento do TCC: dois checkpoints próximos de 4B parâmetros, cada um em NATIVO, Q8_0, Q6_K, Q4_K_M e Q2_K. O objetivo é medir o efeito da quantização no armazenamento, na VRAM, no throughput e na qualidade, normalizando cada quantização pelo NATIVO da mesma família.

Este pacote foi preparado a partir dos arquivos existentes. Os experimentos não foram executados novamente durante sua preparação. Os CSVs, as respostas recuperadas e as imagens foram preservados byte a byte; alguns logs e JSONs tiveram somente prefixos de caminhos pessoais removidos. As adaptações dos scripts constam em [REPO_AUDIT.md](REPO_AUDIT.md).

## Verificação e reprodução

**Verificação:** consulte os resultados preservados e execute `scripts/verify_public_package.py` para conferir hashes, cálculos, 120.320 respostas, transições e gráficos, sem GPU ou inferência.

**Reprodução:** obtenha os checkpoints e datasets nas revisões fixadas, prepare o ambiente e execute a sequência documentada em “Reprodução do experimento”, numa área separada.

Os scripts correspondem ao ambiente realmente utilizado nos experimentos, com as adaptações de empacotamento explicitadas nos diffs. Caminhos de CUDA/MSVC, arquitetura da GPU e outras configurações específicas podem exigir adaptação em outra máquina. Essas adaptações ambientais são responsabilidade de quem reproduz; elas não devem alterar o protocolo experimental, as métricas ou os parâmetros das avaliações. Resultados de desempenho podem variar com hardware, drivers e ambiente. O código não foi refatorado para selecionar automaticamente outras GPUs ou configurações.

## Licença do código

O código original de `scripts/` e `configs/` e sua documentação de software são disponibilizados sob a [licença MIT](LICENSE), por autorização do autor. Essa licença não relicencia modelos, datasets, dados experimentais, llama.cpp, lm-evaluation-harness, bibliotecas ou outros componentes de terceiros. A origem e o tratamento dos dados derivados estão em [LICENSING_NOTES.md](LICENSING_NOTES.md).

## Modelos, software e datasets

| Item | Origem oficial | Revisão utilizada |
| --- | --- | --- |
| Gemma 3 4B Instruct | [google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it) | `093f9f388b31de276ce2de164bdc2081324b9767` |
| Qwen3-4B | [Qwen/Qwen3-4B](https://huggingface.co/Qwen/Qwen3-4B) | `1cfa9a7208912126459214e8b04321603b3df60c` |
| llama.cpp | [ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp) | `1c4729414deba3bcacef6a5614e2ca04d069be3a` |
| WikiText-2 | [Salesforce/wikitext](https://huggingface.co/datasets/Salesforce/wikitext) | `b08601e04326c79dfdd32d625aee71d232d685c3` |
| MMLU-Pro | [TIGER-Lab/MMLU-Pro](https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro) | `b189ec765aa7ed75c8acfea42df31fdae71f97be` |

NATIVO é o GGUF sem quantização dos pesos, convertido com `--outtype bf16`; contém tensores BF16 e F32. O Gemma exporta somente a parte de linguagem do checkpoint multimodal. Não houve QAT, matriz de importância, requantização nem seleção manual de tipos por tensor. O Qwen foi avaliado com thinking desativado.

SHA-256 dos GGUF NATIVO:

```text
Gemma: 06F32227DA36840C82C13A24C3EF6F307327DA3643FA5C4C957445B8E8770090
Qwen:  FAC55A00FD3799B70EF03BD6A6F32F1F72B087FA315035789F69F8F2FE78CA76
```

Os hashes das oito quantizações estão em [quantization_manifest.csv](results/raw/quantization_manifest.csv). Os recibos dos checkpoints, com revisão, tamanho e hashes/ETags disponíveis, foram resumidos em [checkpoints.json](docs/checkpoints.json). ETags Git de 40 caracteres não devem ser interpretados como SHA-256. Os pesos não foram relidos nesta preparação; a conferência histórica consta dos registros originais.

## Métricas e protocolo

| Medida | Procedimento registrado |
| --- | --- |
| Armazenamento | Bytes do GGUF completo, divididos por 10⁹ para GB decimais |
| VRAM | NVML a cada 50 ms; pico menos mediana de dez leituras anteriores; MiB convertidos para MB decimais |
| Velocidade | `llama-bench`: pp512 e tg128 separados, cinco amostras de cada um, oito threads reportadas |
| Perplexidade | WikiText `wikitext-2-raw-v1`, split `test`, 4.358 linhas, contexto 512 |
| MMLU-Pro | Split `test`, 12.032 questões por configuração; zero-shot, letra direta, até oito tokens, temperatura zero |

Benchmark e perplexidade usam batch 2048, microbatch 512, KV F16/F16, offload integral e Flash Attention desligada. O servidor MMLU-Pro usa contexto 2048, batch 2048, microbatch 512, KV F16/F16, Flash Attention ligada, um slot e `-rea off`. O harness é `lm-eval[api]==0.4.13`, com oito solicitações concorrentes, batch 1 e API local em `127.0.0.1:8090`.

A tarefa e o prompt estão em [configs/mmlu_pro_direct.yaml](configs/mmlu_pro_direct.yaml) e [configs/mmlu_pro_direct_utils.py](configs/mmlu_pro_direct_utils.py). O extrator reconhece uma letra A–J no início, com espaços e prefixo `Answer:` opcionais; pode haver texto posterior. Respostas sem extração contam como incorretas. O piloto usa as primeiras 70 questões do **split test**, via `--limit 70`; ele não usa o split validation e não integra a pontuação completa.

O WikiText foi unido por LF, com LF final e UTF-8. O arquivo preparado, omitido por conter texto de terceiros, tem 1.292.014 bytes e SHA-256 `bfe9eb16ab9987fb88bde4ea9a30a00f2a45db01dfc14bad78d05325789c4f12`. Seus metadados estão em [datasets/wiki.test.metadata.json](datasets/wiki.test.metadata.json).

## Hardware e requisitos

Windows 11 Home x64, build 26200; Ryzen 7 9700X; 31,58 GiB de RAM física; RTX 5070 Ti, compute capability 12.0, com 16.303 MiB de VRAM reportados. Driver NVIDIA 617.14; CUDA Toolkit/nvcc 13.4.59; MSVC 19.44.35217.0; CMake 4.4.3; Ninja 1.13.2. Build Release, `GGML_CUDA=ON`, arquitetura 120 selecionada como 120a pelo projeto.

Python 3.12.10 e versões registradas em [environment.txt](environment.txt) e [requirements.txt](requirements.txt). O registro histórico informa PyTorch **2.13.0+cu130**, enquanto requirements permite `torch>=2.6,<3`. O ambiente original usava `--system-site-packages`. Não há lockfile completo nem origem preservada do wheel cu130; instalar apenas requirements não garante reconstruir esse ambiente. Não foram atualizadas ou completadas artificialmente as versões.

A recuperação Arrow exige `pyarrow`, dependência transitiva de datasets; a versão 25.0.1 está instalada no ambiente local inspecionado em 17/11/2026, mas não há registro suficiente para tratá-la como pin histórico. Este é um limite de rastreabilidade.

## Organização e consulta

```text
scripts/                  pipeline, verificações e geração dos gráficos
configs/                  tarefa MMLU-Pro e função do prompt
datasets/                 somente metadados do WikiText
results/raw/              manifesto, JSONs e logs pequenos selecionados
results/processed/        métricas por configuração e dois pilotos
analysis/results.csv      valores absolutos e normalizados, sem arredondamento
analysis/validation.csv   carga, CUDA, offload e respostas de validação
analysis/mmlu_*.csv        120.320 registros recuperados, contagens e transições
analysis/auditoria_dados.json      auditoria histórica com caminho privado removido
analysis/integridade_final.json   conferência histórica de hashes e normalizações
analysis/plots/           seis gráficos originais de results.py
plots/                    seis figuras usadas no TCC atual e valores_graficos.json
docs/                     proveniência, inventários, adaptações e verificações
```

Os caminhos canônicos dos dois CSVs foram mantidos em `analysis/`, como no experimento. Isso evita alterar os scripts que os consomem. O [mapa do TCC](docs/TCC_ARTIFACT_MAP.md) relaciona as seis tabelas e figuras às fontes. O [manifesto](REPO_MANIFEST.md) lista cada cópia; [exclusões](REPO_EXCLUDED.md) explica o que ficou de fora.

Para conferir o pacote sem GPU, modelos, dependências científicas ou acesso à rede, a partir desta raiz:

```powershell
py -3.12 scripts\verify_public_package.py
```

Esse verificador foi criado na preparação pública. Ele apenas lê arquivos e verifica checksums, métricas brutas/processadas, cálculos normalizados, respostas por questão, transições e séries dos gráficos. Não executa scripts experimentais nem recarrega os caches SQLite. A verificação histórica completa de `verify_results.py` exige os GGUF omitidos.

## Reprodução do experimento

Os comandos abaixo documentam a execução futura, em PowerShell. Nenhum deles foi usado para repetir experimentos na preparação deste pacote. É preciso obter os softwares e arquivos externos indicados e conferir suas condições de uso.

### Área separada e ambiente

Para manter as evidências distribuídas intactas, crie uma área vazia a partir da raiz do pacote e leve apenas código, configurações e referências necessárias. **Não copie os resultados processados**: benchmark, perplexidade e quality pulam casos com JSONs já existentes. `--force` existe somente em quality e não resolve os demais scripts.

```powershell
New-Item -ItemType Directory -Path .\reproduction_run -ErrorAction Stop
Copy-Item .\scripts, .\configs -Destination .\reproduction_run -Recurse
Copy-Item .\requirements.txt, .\environment.txt -Destination .\reproduction_run
New-Item -ItemType Directory -Path .\reproduction_run\datasets, .\reproduction_run\results\raw
Copy-Item .\datasets\wiki.test.metadata.json .\reproduction_run\datasets\
Copy-Item .\results\raw\quantization_manifest.csv .\reproduction_run\results\raw\
Set-Location .\reproduction_run
```

Todos os comandos seguintes partem dessa **nova raiz**. O manifesto copiado é a referência histórica esperada, não um registro de uma nova quantização. `quantize.ps1` não gera o manifesto; confira os novos hashes contra ele. Se divergirem, preserve a divergência em um registro separado e não apresente o arquivo histórico como medição nova.

Prepare previamente Visual Studio 2022 com ferramentas C++, CUDA 13.4 e o Python indicado. A origem exata do PyTorch cu130 deve ser resolvida antes de alegar reprodução estrita. Os comandos registrados para venv, instalação e build são:

```powershell
py -3.12 -m venv --system-site-packages .venv
& .venv\Scripts\python.exe -m pip install -r requirements.txt
git clone https://github.com/ggml-org/llama.cpp.git llama.cpp
git -C llama.cpp checkout 1c4729414deba3bcacef6a5614e2ca04d069be3a
& .\scripts\build_llama.ps1
$cudaBin = 'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\bin'
$env:PATH = "$cudaBin\x64;$cudaBin;$env:PATH"
```

Esses comandos preservam a abordagem original, mas não fixam todas as dependências transitivas. O conversor também depende dos requisitos de seu checkout, em `llama.cpp/requirements/requirements-convert_hf_to_gguf.txt`; consulte esse arquivo da revisão fixada se o ambiente isolado indicar módulos ausentes. Não houve registro separado de instalação desse conjunto no projeto original.

Aceite os termos do Gemma no repositório oficial e autentique sua própria conta localmente quando necessário; não grave tokens neste repositório. Downloads registrados:

```powershell
& .venv\Scripts\python.exe -c "from huggingface_hub import snapshot_download; snapshot_download('google/gemma-3-4b-it', revision='093f9f388b31de276ce2de164bdc2081324b9767', local_dir='models/gemma3-4b/original', max_workers=4)"
& .venv\Scripts\python.exe -c "from huggingface_hub import snapshot_download; snapshot_download('Qwen/Qwen3-4B', revision='1cfa9a7208912126459214e8b04321603b3df60c', local_dir='models/qwen3-4b/original', max_workers=4)"
& .venv\Scripts\python.exe scripts\verify_checkpoints.py
```

### 1. Conversão dos checkpoints

```powershell
& .venv\Scripts\python.exe llama.cpp\convert_hf_to_gguf.py models\gemma3-4b\original --outfile models\gemma3-4b\gemma3-4b-native.gguf --outtype bf16
& .venv\Scripts\python.exe llama.cpp\convert_hf_to_gguf.py models\qwen3-4b\original --outfile models\qwen3-4b\qwen3-4b-native.gguf --outtype bf16
Get-FileHash -Algorithm SHA256 -LiteralPath models\gemma3-4b\gemma3-4b-native.gguf, models\qwen3-4b\qwen3-4b-native.gguf
```

Compare os hashes com os NATIVO acima. Antes da quantização, o procedimento registrado também validou os dois baselines com o mesmo prompt:

```powershell
$prompt = 'Explain in two sentences what a CPU cache is.'
& .\llama.cpp\build\bin\llama-cli.exe -m models\gemma3-4b\gemma3-4b-native.gguf -ngl all -fit off -c 4096 -n 96 -p $prompt -st --temp 0
& .\llama.cpp\build\bin\llama-cli.exe -m models\qwen3-4b\qwen3-4b-native.gguf -ngl all -fit off -c 4096 -n 96 -p $prompt -st --temp 0 --chat-template-kwargs '{"enable_thinking":false}'
```

### 2. Quantização

```powershell
& .\scripts\quantize.ps1
Get-ChildItem models\*\*.gguf | Get-FileHash -Algorithm SHA256
```

O script verifica os hashes nativos e recusa sobrescrever GGUF existentes. Compare hashes e tamanhos das oito saídas com o manifesto histórico. Os logs registram os comandos; os presets são aplicados diretamente ao NATIVO de cada família.

### 3. Validação das dez configurações

```powershell
& .\scripts\validate_all.ps1
& .venv\Scripts\python.exe scripts\validation_report.py
```

### 4. Velocidade e VRAM

```powershell
& .venv\Scripts\python.exe scripts\benchmark.py
```

### 5. Preparação do WikiText-2

```powershell
& .venv\Scripts\python.exe scripts\prepare_wikitext.py
Get-FileHash -Algorithm SHA256 -LiteralPath datasets\wiki.test.raw
```

A cópia pública fixa a revisão efetivamente usada. Confira o hash do corpus informado acima antes da perplexidade. O original consultava a revisão corrente; a adaptação atende à observação explícita do Apêndice A.

### 6. Perplexidade

```powershell
& .venv\Scripts\python.exe scripts\perplexity.py
```

No experimento original, os dois Q2_K foram repetidos com parâmetros idênticos; os logs `*-perplexity-repeat.log` estão preservados no pacote. O script não implementa a repetição nem cria esses nomes automaticamente. Para reproduzir também essa conferência, depois da primeira passagem:

```powershell
& .\llama.cpp\build\bin\llama-perplexity.exe -m models\gemma3-4b\gemma3-4b-q2_k.gguf -f datasets\wiki.test.raw -c 512 -b 2048 -ub 512 -ngl all -fa off -fit off -ctk f16 -ctv f16 *> results\raw\gemma3-4b-q2_k-perplexity-repeat.log
& .\llama.cpp\build\bin\llama-perplexity.exe -m models\qwen3-4b\qwen3-4b-q2_k.gguf -f datasets\wiki.test.raw -c 512 -b 2048 -ub 512 -ngl all -fa off -fit off -ctk f16 -ctv f16 *> results\raw\qwen3-4b-q2_k-perplexity-repeat.log
```

Os argumentos foram conferidos em `perplexity.py`; a redação PowerShell acima explicita a repetição descrita no TCC, sem afirmar que a sintaxe exata da sessão original foi preservada.

### 7. Piloto MMLU-Pro

```powershell
& .venv\Scripts\python.exe scripts\quality.py pilot
```

### 8. Avaliação completa MMLU-Pro

```powershell
& .venv\Scripts\python.exe scripts\quality.py full
```

O script inicia/encerra o servidor por configuração e mantém caches para retomada. A configuração pública está em `configs/`; apenas o caminho de inclusão foi adaptado. Os parâmetros experimentais são os originais.

### 9. Consolidação

```powershell
& .venv\Scripts\python.exe scripts\results.py
```

Gera `analysis/results.csv` e `analysis/plots/`. Para a apresentação usada no TCC atual, sem mudar dados:

```powershell
& .venv\Scripts\python.exe scripts\gerar_figuras.py
```

Gera `plots/` e `plots/valores_graficos.json`, verificando igualdade com o CSV.

### 10. Verificação do experimento completo

```powershell
& .venv\Scripts\python.exe scripts\verify_results.py
```

Exige GGUF, manifesto, logs das duas repetições, dados processados e gráficos originais. Não é o comando de consulta do pacote sem modelos. Mudanças reais em novas medições podem causar falhas de igualdade; não ajuste as medições para forçar concordância.

### 11. Auditoria e recuperação individual

```powershell
& .venv\Scripts\python.exe scripts\auditar_dados.py
```

Não inicia inferência. Exige dez bancos `results/processed/*-mmlu-full-cache_rank0.db`, dez logs `results/raw/*-mmlu-full-server.log`, `datasets/wiki.test.raw` e o Arrow do split test. Depois de uma reprodução completa, esses arquivos são produzidos pelas etapas anteriores. Para repetir a recuperação **histórica**, os bancos e logs históricos devem ser obtidos de um futuro arquivo suplementar; ainda não existe URL ou DOI desse depósito.

O script procura o Arrow no cache padrão do Hugging Face, na revisão fixada. Em instalações com outro cache, indique o arquivo existente, sem mover os originais:

```powershell
$env:TCC_MMLU_ARROW = Join-Path $env:HF_DATASETS_CACHE 'TIGER-Lab___mmlu-pro\default\0.0.0\b189ec765aa7ed75c8acfea42df31fdae71f97be\mmlu-pro-test.arrow'
& .venv\Scripts\python.exe scripts\auditar_dados.py
```

Esse exemplo pressupõe `HF_DATASETS_CACHE` configurado. `TCC_MMLU_ARROW` é uma adaptação pública documentada. A saída fica em `analysis/reproduced_audit/`, preservando os derivados históricos distribuídos. O relatório do algoritmo original mantém a data histórica de 16/10/2026; para uma execução futura, use os registros da nova sessão como data efetiva, sem interpretar essa constante como data da reprodução.

## Arquivos omitidos e limites

Não são distribuídos checkpoints, GGUF, tokenizadores completos, executáveis/builds ou clone do llama.cpp. Os dez bancos completos (~21,1 MB), os dez logs completos do servidor (~110,6 MB) e o Arrow (~8,7 MB) estão inventariados em [docs/large_files.csv](docs/large_files.csv), com função, necessidade, possibilidade de reconstrução e recomendação. Nenhum Git LFS foi configurado.

O texto do WikiText, os JSONL dos pilotos com questões/alternativas e os caches completos do Hugging Face foram excluídos. Os resultados por questão contêm identificadores, categorias, letras do gabarito e respostas curtas geradas; não contêm colunas de enunciado ou alternativas. Consulte [LICENSING_NOTES.md](LICENSING_NOTES.md) antes de reutilizar material derivado de datasets. A licença MIT limita-se ao código próprio e à documentação de software; não é uma licença global dos dados.

A reprodução perfeita é limitada pela ausência de lockfile completo, fonte do wheel PyTorch, controles de temperatura/clocks/plano de energia/processos externos e seed explícita adicional do servidor. A ordem dos testes era fixa; as cinco amostras pertencem a um processo por configuração. O pico NVML tem resolução de 50 ms e não há série temporal completa. O harness registra seeds 0/1234/1234/1234; temperatura zero não garante igualdade entre hardwares. A perplexidade usa blocos e não pontua todas as posições. As comparações pareadas são descritivas: não houve McNemar nem intervalos pareados. As acurácias não são comparáveis diretamente a protocolos de cinco exemplos com cadeia de raciocínio.

Arquivar os bancos/logs históricos melhora a verificabilidade independente da recuperação. Nenhum depósito Zenodo foi criado e não há DOI do repositório. A referência de versão está em CITATION.cff; futuras versões não devem substituir a tag utilizada no trabalho.
