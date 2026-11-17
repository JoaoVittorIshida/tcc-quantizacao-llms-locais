# Arquivos e pastas excluídos
Classificação: A = incluído; B = importante para arquivo suplementar; C = redundante/recriável; D = cache temporário; E = material de terceiro; F = fora do pacote científico. Cada arquivo de results/raw e results/processed foi classificado individualmente em [docs/results_classification.csv](docs/results_classification.csv). O inventário por arquivo está em [docs/source_inventory.csv](docs/source_inventory.csv).
## Exclusões por conjunto
| Conjunto | Motivo e efeito |
| --- | --- |
| `.venv/`, virtualenv, `__pycache__/` | Ambiente instalado/bytecode; versões preservadas nos registros, sem copiar pacotes |
| `.git/` | Histórico, objetos e configuração internos; nenhum repositório novo foi inicializado |
| `llama.cpp/` | Clone, builds e executáveis de terceiros; revisão exata registrada no README |
| `models/` | Checkpoints, GGUF, pesos e tokenizadores; cerca de 55,8 GB; recuperação pela origem oficial e hashes |
| Caches Hugging Face | Downloads, Arrow e Parquet de datasets; não se redistribui cache completo |
| Dez caches SQLite completos | B; cerca de 21,1 MB; candidatos a Zenodo. São fontes históricas únicas para refazer a recuperação sem inferência, embora os derivados já estejam incluídos |
| Dez logs completos MMLU-Pro | B; cerca de 110,6 MB; candidatos a Zenodo após sanitização; necessários aos checks históricos de completude |
| JSONL dos pilotos | E; contêm questões e alternativas; agregados dos pilotos efetivos foram preservados |
| `datasets/wiki.test.raw` | E; texto WikiText integral, 1.292.014 bytes; revisão, hash e preparo preservados |
| TCC em DOCX/PDF/Markdown e versões antigas | F; pacote é de artefatos, sem capítulos ou identificador estudantil. Hashes da versão consultada preservados |
| Prompts/instruções editoriais, diffs, renders e verificadores de documentos | F; não integram os procedimentos experimentais |
| `analysis/interpretation.md` | F; texto anterior à recuperação, com afirmação superada sobre ausência de dados individuais; TCC atual prevalece |
| Pilotos/ensaios anteriores, primeira conversão falha e offload redundante | C/D; resultados finais e logs de validação completos selecionados já cobrem o procedimento |

Nenhum arquivo foi apagado ou movido na origem. Nenhuma exclusão implica perda dos arquivos originais. Caminhos pessoais foram removidos apenas das cópias de logs/JSONs selecionados. Não foi identificado segredo de alta confiança no conjunto de artefatos próprios examinado; dependências e caches rejeitados não foram copiados.
## Cada resultado excluído

| Caminho original | Bytes | Classe | Motivo |
| --- | ---: | --- | --- |
| `results/processed/gemma3-4b-native-mmlu-full-cache_rank0.db` | 2093056 | B | Cache histórico importante; 12.032 respostas por banco; necessário à recuperação histórica independente |
| `results/processed/gemma3-4b-native-mmlu-pilot-cacheconcurrent8_rank0.db` | 32768 | D | Cache de piloto/ensaios; resultados finais e agregados selecionados são suficientes |
| `results/processed/gemma3-4b-native-mmlu-pilot-cacheflashon_rank0.db` | 32768 | D | Cache de piloto/ensaios; resultados finais e agregados selecionados são suficientes |
| `results/processed/gemma3-4b-native-mmlu-pilot-cachenographs_rank0.db` | 32768 | D | Cache de piloto/ensaios; resultados finais e agregados selecionados são suficientes |
| `results/processed/gemma3-4b-native-mmlu-pilot-cache_rank0.db` | 32768 | D | Cache de piloto/ensaios; resultados finais e agregados selecionados são suficientes |
| `results/processed/gemma3-4b-q2_k-mmlu-full-cache_rank0.db` | 2101248 | B | Cache histórico importante; 12.032 respostas por banco; necessário à recuperação histórica independente |
| `results/processed/gemma3-4b-q4_k_m-mmlu-full-cache_rank0.db` | 2097152 | B | Cache histórico importante; 12.032 respostas por banco; necessário à recuperação histórica independente |
| `results/processed/gemma3-4b-q6_k-mmlu-full-cache_rank0.db` | 2097152 | B | Cache histórico importante; 12.032 respostas por banco; necessário à recuperação histórica independente |
| `results/processed/gemma3-4b-q8_0-mmlu-full-cache_rank0.db` | 2084864 | B | Cache histórico importante; 12.032 respostas por banco; necessário à recuperação histórica independente |
| `results/processed/qwen3-4b-native-mmlu-full-cache_rank0.db` | 2121728 | B | Cache histórico importante; 12.032 respostas por banco; necessário à recuperação histórica independente |
| `results/processed/qwen3-4b-native-mmlu-pilot-cacheconcurrent8_rank0.db` | 32768 | D | Cache de piloto/ensaios; resultados finais e agregados selecionados são suficientes |
| `results/processed/qwen3-4b-native-mmlu-pilot-cacheflashon_rank0.db` | 32768 | D | Cache de piloto/ensaios; resultados finais e agregados selecionados são suficientes |
| `results/processed/qwen3-4b-native-mmlu-pilot-cache_rank0.db` | 32768 | D | Cache de piloto/ensaios; resultados finais e agregados selecionados são suficientes |
| `results/processed/qwen3-4b-q2_k-mmlu-full-cache_rank0.db` | 2191360 | B | Cache histórico importante; 12.032 respostas por banco; necessário à recuperação histórica independente |
| `results/processed/qwen3-4b-q4_k_m-mmlu-full-cache_rank0.db` | 2088960 | B | Cache histórico importante; 12.032 respostas por banco; necessário à recuperação histórica independente |
| `results/processed/qwen3-4b-q6_k-mmlu-full-cache_rank0.db` | 2093056 | B | Cache histórico importante; 12.032 respostas por banco; necessário à recuperação histórica independente |
| `results/processed/qwen3-4b-q8_0-mmlu-full-cache_rank0.db` | 2101248 | B | Cache histórico importante; 12.032 respostas por banco; necessário à recuperação histórica independente |
| `results/raw/bench-pilot.json` | 2698 | C | Piloto anterior, tentativa falha, log vazio ou evidência redundante aos logs finais selecionados |
| `results/raw/bench-pilot.stderr.log` | 155 | C | Piloto anterior, tentativa falha, log vazio ou evidência redundante aos logs finais selecionados |
| `results/raw/gemma3-4b-conversion-first-attempt.log` | 1559 | C | Piloto anterior, tentativa falha, log vazio ou evidência redundante aos logs finais selecionados |
| `results/raw/gemma3-4b-native-mmlu-full-server.log` | 11078916 | B | Log histórico de completude; 12.032 liberações e ausência de truncamento; sanitizar caminhos antes de depósito |
| `results/raw/gemma3-4b-native-offload.log` | 344629 | C | Piloto anterior, tentativa falha, log vazio ou evidência redundante aos logs finais selecionados |
| `results/raw/gemma3-4b-q2_k-mmlu-full-server.log` | 11073657 | B | Log histórico de completude; 12.032 liberações e ausência de truncamento; sanitizar caminhos antes de depósito |
| `results/raw/gemma3-4b-q4_k_m-mmlu-full-server.log` | 11064558 | B | Log histórico de completude; 12.032 liberações e ausência de truncamento; sanitizar caminhos antes de depósito |
| `results/raw/gemma3-4b-q6_k-mmlu-full-server.log` | 11070160 | B | Log histórico de completude; 12.032 liberações e ausência de truncamento; sanitizar caminhos antes de depósito |
| `results/raw/gemma3-4b-q8_0-mmlu-full-server.log` | 11068103 | B | Log histórico de completude; 12.032 liberações e ausência de truncamento; sanitizar caminhos antes de depósito |
| `results/raw/qwen3-4b-native-loader.log` | 0 | C | Piloto anterior, tentativa falha, log vazio ou evidência redundante aos logs finais selecionados |
| `results/raw/qwen3-4b-native-mmlu-full-server.log` | 11044367 | B | Log histórico de completude; 12.032 liberações e ausência de truncamento; sanitizar caminhos antes de depósito |
| `results/raw/qwen3-4b-native-offload.log` | 353338 | C | Piloto anterior, tentativa falha, log vazio ou evidência redundante aos logs finais selecionados |
| `results/raw/qwen3-4b-q2_k-mmlu-full-server.log` | 11054547 | B | Log histórico de completude; 12.032 liberações e ausência de truncamento; sanitizar caminhos antes de depósito |
| `results/raw/qwen3-4b-q4_k_m-mmlu-full-server.log` | 11037096 | B | Log histórico de completude; 12.032 liberações e ausência de truncamento; sanitizar caminhos antes de depósito |
| `results/raw/qwen3-4b-q6_k-mmlu-full-server.log` | 11039734 | B | Log histórico de completude; 12.032 liberações e ausência de truncamento; sanitizar caminhos antes de depósito |
| `results/raw/qwen3-4b-q8_0-mmlu-full-server.log` | 11038532 | B | Log histórico de completude; 12.032 liberações e ausência de truncamento; sanitizar caminhos antes de depósito |
| `results/raw/mmlu_pilot/gemma3-4b-native/tcc-model/results_2026-09-28T22-24-36.202196.json` | 5739 | C | Piloto anterior, tentativa falha, log vazio ou evidência redundante aos logs finais selecionados |
| `results/raw/mmlu_pilot/gemma3-4b-native/tcc-model/results_2026-09-28T22-25-43.456691.json` | 5737 | C | Piloto anterior, tentativa falha, log vazio ou evidência redundante aos logs finais selecionados |
| `results/raw/mmlu_pilot/gemma3-4b-native/tcc-model/results_2026-09-28T22-30-07.111553.json` | 5775 | C | Piloto anterior, tentativa falha, log vazio ou evidência redundante aos logs finais selecionados |
| `results/raw/mmlu_pilot/gemma3-4b-native/tcc-model/results_2026-09-28T22-33-11.076540.json` | 5772 | C | Piloto anterior, tentativa falha, log vazio ou evidência redundante aos logs finais selecionados |
| `results/raw/mmlu_pilot/gemma3-4b-native/tcc-model/samples_mmlu_pro_direct_2026-09-28T22-24-36.202196.jsonl` | 128061 | E | Amostras de piloto com enunciados/alternativas de terceiros; não integram as tabelas finais |
| `results/raw/mmlu_pilot/gemma3-4b-native/tcc-model/samples_mmlu_pro_direct_2026-09-28T22-25-43.456691.jsonl` | 128061 | E | Amostras de piloto com enunciados/alternativas de terceiros; não integram as tabelas finais |
| `results/raw/mmlu_pilot/gemma3-4b-native/tcc-model/samples_mmlu_pro_direct_2026-09-28T22-30-07.111553.jsonl` | 128061 | E | Amostras de piloto com enunciados/alternativas de terceiros; não integram as tabelas finais |
| `results/raw/mmlu_pilot/gemma3-4b-native/tcc-model/samples_mmlu_pro_direct_2026-09-28T22-33-11.076540.jsonl` | 128061 | E | Amostras de piloto com enunciados/alternativas de terceiros; não integram as tabelas finais |
| `results/raw/mmlu_pilot/gemma3-4b-native/tcc-model/samples_mmlu_pro_direct_2026-09-28T22-33-49.972039.jsonl` | 128061 | E | Amostras de piloto com enunciados/alternativas de terceiros; não integram as tabelas finais |
| `results/raw/mmlu_pilot/qwen3-4b-native/tcc-model/results_2026-09-28T22-26-41.392494.json` | 5738 | C | Piloto anterior, tentativa falha, log vazio ou evidência redundante aos logs finais selecionados |
| `results/raw/mmlu_pilot/qwen3-4b-native/tcc-model/results_2026-09-28T22-31-01.477099.json` | 5772 | C | Piloto anterior, tentativa falha, log vazio ou evidência redundante aos logs finais selecionados |
| `results/raw/mmlu_pilot/qwen3-4b-native/tcc-model/samples_mmlu_pro_direct_2026-09-28T22-26-41.392494.jsonl` | 128209 | E | Amostras de piloto com enunciados/alternativas de terceiros; não integram as tabelas finais |
| `results/raw/mmlu_pilot/qwen3-4b-native/tcc-model/samples_mmlu_pro_direct_2026-09-28T22-31-01.477099.jsonl` | 128184 | E | Amostras de piloto com enunciados/alternativas de terceiros; não integram as tabelas finais |
| `results/raw/mmlu_pilot/qwen3-4b-native/tcc-model/samples_mmlu_pro_direct_2026-09-28T22-34-31.530937.jsonl` | 128184 | E | Amostras de piloto com enunciados/alternativas de terceiros; não integram as tabelas finais |

## Arquivos grandes

Todos os resultados com pelo menos 1 MiB, os pesos/recursos grandes locais e o Arrow utilizado estão detalhados em [docs/large_files.csv](docs/large_files.csv). O limite de 1 MiB é um critério de inventário, não uma regra de exclusão: o CSV recuperado de 12.510.388 bytes foi incluído expressamente, por ser central à verificação e ter tamanho manejável. Nenhum banco/log foi enviado automaticamente a Git LFS ou Zenodo.
