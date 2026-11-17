# Relação entre o TCC e os artefatos

A referência é o TCC atual, com 50 páginas físicas; os hashes de DOCX, PDF e Markdown consultados estão em [tcc_reference.json](tcc_reference.json). Não se distribui o documento integral: sua capa contém um identificador estudantil desnecessário ao pacote experimental. Os capítulos não foram copiados ou editados.

## Metodologia e Apêndice A

| Parte do TCC | Evidências no pacote | Dependências externas e observações |
| --- | --- | --- |
| 3.2 Ambiente | `environment.txt`, `requirements.txt`, JSONs do harness e benchmark | Não há lockfile transitivo completo; torch tem intervalo no requirements e versão medida no environment |
| 3.3 Checkpoints | `docs/checkpoints.json`, `scripts/verify_checkpoints.py`, README | Pesos oficiais e arquivos do checkpoint devem ser baixados nas revisões registradas |
| 3.4 Conversão | `results/raw/*-conversion.log`, comandos do README | `convert_hf_to_gguf.py` pertence ao checkout externo fixado de llama.cpp |
| 3.4 Quantização | `scripts/quantize.ps1`, `results/raw/*-quantization.log`, `quantization_manifest.csv` | GGUF excluídos; manifesto registra os hashes e a ferramenta |
| 3.4 Validação | `scripts/validate_all.ps1`, `scripts/validation_report.py`, `analysis/validation.csv`, dez logs de validação | Binário e modelos externos para repetir |
| 3.6.1 Velocidade/VRAM | `scripts/benchmark.py`, dez `*-bench.json`, dez `*-benchmark.json` | Cinco amostras por teste; nenhum histórico temporal completo de NVML foi encontrado |
| 3.6.2 WikiText/PPL | `scripts/prepare_wikitext.py`, `scripts/perplexity.py`, metadados do dataset, dez JSONs de PPL e doze logs | Corpus integral excluído por conteúdo de terceiros; duas repetições Q2_K preservadas |
| 3.6.3 MMLU-Pro | `scripts/quality.py`, YAML e função em `configs/`, dez JSONs completos e dois pilotos com seus agregados do harness | Servidor local, GGUF e dataset externo; JSONL de amostras omitidos |
| 3.6.4 Recuperação | `scripts/auditar_dados.py`, `analysis/mmlu_por_questao_recuperado.csv`, contagens, transições e auditoria | Para recuperar novamente dos caches históricos: dez DB, dez logs grandes, Arrow e WikiText, omitidos e inventariados |
| 3.7 Consolidação | `scripts/results.py`, `analysis/results.csv`, `analysis/integridade_final.json` | Sete medidas normalizadas contra NATIVO por família |
| Apêndice A | Todos os nove scripts experimentais listados e `scripts/auditar_dados.py` | Conversor externo documentado; caminho temporário da recuperação substituído somente na cópia |

## Tabelas e figuras

| Elemento | Arquivo e campos utilizados |
| --- | --- |
| Quadro 1 — Ambiente | `environment.txt`; confirmação por JSONs brutos de velocidade/harness |
| Tabela 1 — Arquivo/VRAM | `analysis/results.csv`: `file_size_gb`, `peak_vram_mb` |
| Tabela 2 — Throughput | Mesmo CSV: `pp512_tps_mean`, `pp512_tps_std`, `tg128_tps_mean`, `tg128_tps_std` |
| Tabela 3 — Perplexidade | Mesmo CSV: `perplexity`, `ppl_increase_percent`; JSONs e logs de PPL |
| Tabela 4 — MMLU-Pro | Mesmo CSV: `mmlu_pro_score`; `analysis/mmlu_contagens.csv` fornece acertos e respostas sem extração |
| Tabela 5 — Transições | `analysis/mmlu_pareado_descritivo.csv`, derivado das respostas individuais |
| Tabela 6 — Normalização | CSV consolidado: `size_reduction_percent`, `vram_reduction_percent`, `generation_speedup`, `mmlu_retention_percent` |
| Figura 1 | `plots/01_size.png` — `file_size_gb` |
| Figura 2 | `plots/02_vram.png` — `peak_vram_mb` |
| Figura 3 | `plots/03_pp512.png` — `pp512_tps_mean` |
| Figura 4 | `plots/04_tg128.png` — `tg128_tps_mean` |
| Figura 5 | `plots/05_perplexity.png` — `ppl_increase_percent` |
| Figura 6 | `plots/06_mmlu_pro.png` — `mmlu_retention_percent` |

Os seis arquivos de `plots/` são as imagens existentes usadas no TCC atual, copiadas sem redesenho. `plots/valores_graficos.json` contém as séries exatas. `analysis/plots/` preserva também a apresentação anterior gerada pelo consolidado, necessária à verificação original. As duas apresentações usam os mesmos números, mas diferem nos rótulos e no posicionamento visual.

## Cálculos verificáveis

Para cada família, n é NATIVO e q é a configuração comparada:

- Redução do arquivo: `100 * (1 - bytes_q / bytes_n)`.
- Redução de VRAM: `100 * (1 - vram_q / vram_n)`.
- Aceleração: `tokens_s_q / tokens_s_n`, separada para pp512 e tg128.
- Delta de PPL: `ppl_q - ppl_n`; variação: `100 * (ppl_q / ppl_n - 1)`.
- Retenção MMLU-Pro: `100 * acuracia_q / acuracia_n`.
- Diferença em pontos percentuais: `100 * (acuracia_q - acuracia_n)`.
- Transições: ambos corretos, perda, ganho, ambos errados; soma 12.032; saldo = ganhos − perdas.

A unidade MB usa `MiB * 1.048.576 / 1.000.000`. Os cálculos usam valores completos; arredondamento pertence à apresentação. O verificador público confronta esses cálculos com os CSVs preservados, sem criar novos resultados experimentais ou testes estatísticos.

## Proveniência da recuperação

A cópia atualmente referenciada pelo Apêndice A é a do diretório de apoio da versão atual. Ela difere do script originalmente executado apenas na primeira linha da docstring, que deixou de mencionar uma pasta de redação. O código funcional é idêntico. O processo editorial também registra que os CSVs e a auditoria foram copiados da entrega auditada anterior. As versões recuperadas têm hashes idênticos entre essas entregas.

O manifesto identifica ambos os caminhos históricos e seus hashes; esses nomes aparecem como proveniência, sem dependência operacional. A cópia pública altera raiz, saída e seleção opcional do Arrow, preservando a reconstrução de prompts, chaves, extração e contagens.
