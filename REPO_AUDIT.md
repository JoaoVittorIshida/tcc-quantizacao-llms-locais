# Auditoria do pacote público

Este documento preserva o registro da preparação anterior à publicação. A finalização autorizada pelo autor aplicou MIT ao código próprio e manteve todos os scripts, configurações, dados e figuras com os mesmos bytes desse pacote auditado. O registro da versão pública está em [docs/PUBLICATION.md](docs/PUBLICATION.md), e a nova conferência está em `docs/publication_validation.json`. As declarações abaixo sobre ausência de licença/publicação descrevem a etapa anterior.

Preparação em 17/11/2026, horário de referência America/Sao_Paulo. O escopo é copiar, organizar, documentar e conferir evidências existentes. Nenhum experimento, conversão, quantização, build, benchmark, inferência ou teste estatístico foi executado. Não houve git init, commit, push, criação remota, publicação ou configuração de Git LFS. A leitura da revisão Git do clone existente foi somente consultiva.

## Fontes e preservação

O TCC atual foi consultado em DOCX, PDF de 50 páginas e Markdown. Os hashes dessas fontes estão em `docs/tcc_reference.json`. Foram lidos README, environment, requirements, plano experimental, scripts, configurações, metadados, resultados brutos/processados, consolidados e auditorias. O inventário recursivo abrange **36.708 arquivos**; `docs/inspection_scope.json` explicita os limites da inspeção sem afirmar leitura semântica de todos os pesos, dependências ou documentos antigos.

Uma fotografia anterior à cópia registrou tamanho e data de modificação de todos esses arquivos. A conferência final compara esse inventário e **611 hashes SHA-256** de arquivos próprios/documentais/experimentais, incluindo as fontes atuais do TCC. Nenhum arquivo original foi alterado, movido ou apagado; a única entrada nova na raiz é a pasta deste pacote. Os utilitários temporários de preparação ficaram fora da raiz original e não são distribuídos.

Foram selecionadas **149 cópias**, rastreadas individualmente em `REPO_MANIFEST.md` e `docs/copied_files.json`. Documentação, inventários, checksums, diffs e o verificador público são arquivos novos de preparação, identificados como tais. Os CSVs, figuras e valores experimentais não foram recalculados ou substituídos no pacote.

## Identidade dos resultados principais

| Arquivo | SHA-256 idêntico na origem e na cópia |
| --- | --- |
| `analysis/results.csv` | `091f19a313157de822effd597550f16b7bf0273c5a6a5573c5f349ee3a34efe3` |
| `analysis/validation.csv` | `8bcb26b78f59f9172c6e342d20ab3a6fa9ece763dc5f5fdbf453e8aa61527763` |
| `analysis/mmlu_por_questao_recuperado.csv` | `8ab90424c82ac91b9c603a75e2f0797a80b3773bd90acb18e8ec86d7ebc1ffef` |
| `results/raw/quantization_manifest.csv` | `fcea479242143c101ea93173f7fa23304dbdc650f63b26a223579fb349d7d1b0` |

O mesmo critério de identidade byte a byte se aplica aos demais CSVs selecionados, às seis figuras atuais, às seis figuras originais e a `plots/valores_graficos.json`. As diferenças nos JSONs sanitizados foram comparadas estruturalmente: somente strings de localização mudaram, sem alteração de números, booleanos, listas ou métricas. Os logs sanitizados diferem apenas nos prefixos de caminhos removidos.

## Adaptações operacionais somente na cópia

| Arquivo | Alteração e motivo |
| --- | --- |
| `scripts/prepare_wikitext.py` | Substitui a consulta à revisão corrente pelo commit efetivamente usado; remove import HfApi que ficou sem uso. É a correção de reprodução pedida expressamente no Apêndice A. |
| `scripts/quality.py` | Aponta `--include_path` para `configs/`, mantendo todos os parâmetros de geração, servidor e harness. |
| `scripts/auditar_dados.py` | A cópia citada no TCC atual tem algoritmo idêntico ao script histórico, diferindo antes do empacotamento somente na docstring. Ajusta a raiz para `scripts/`, a saída para `analysis/reproduced_audit/` e as fontes YAML/util para `configs/`; aceita Arrow indicado em `TCC_MMLU_ARROW` e evita escrever caminho pessoal no relatório novo. Mantém prompts, serialização, chaves, extrator, asserts e contagens. |
| `scripts/gerar_figuras.py` | Ajusta a raiz e a saída para `plots/`; mantém a conferência contra o CSV, os números e a apresentação usada no TCC. |

Os quatro diffs completos estão em `docs/adaptations/`. Nos scripts adaptados, as quebras de linha foram normalizadas para LF; os demais códigos copiados conservaram seus bytes. Nenhum script depende operacionalmente de diretórios temporários de redação. Esses nomes permanecem apenas nos manifestos, inventários e metadados de proveniência.

`scripts/verify_public_package.py` é novo: confere evidências sem modelos ou rede. O verificador experimental `scripts/verify_results.py` foi mantido intacto e continua exigindo os GGUF e logs de repetição. Essas ausências são dependências externas documentadas, não referências internas acidentalmente quebradas.

## Privacidade e segredos

Foram encontradas localizações pessoais em logs/JSONs do benchmark, perplexidade, harness e no campo `dataset_cache_file` da auditoria histórica. Nas cópias selecionadas, o prefixo da raiz original foi removido, mantendo caminhos relativos; o caminho do cache passou a começar por `~/.cache/huggingface/`. As chaves e hashes históricos da auditoria foram preservados. Sua seção `experimental_sources_sha256` registra os caminhos **originais** da tarefa; a correspondência pública é `configs/mmlu_pro_direct.yaml` e `configs/mmlu_pro_direct_utils.py`.

O texto integral do TCC não foi copiado, pois contém um identificador estudantil que não é necessário para reproduzir os experimentos. Nenhum dado pessoal adicional foi incluído além da autoria/orientação/instituição solicitadas. Instruções de redação, materiais internos, históricos Git, ambientes, credenciais e caches completos não foram distribuídos.

A varredura recursiva do pacote examina textos e metadados das imagens para padrões de chaves API, tokens Hugging Face/GitHub/OpenAI/AWS, chaves privadas, atribuições de senha/segredo, URLs com autenticação, URLs de rede privada, caminhos de usuário, e-mails e o identificador estudantil. Verifica também ausência de `.env`, chaves SSH e binários/datasets excluídos. Não foram identificadas credenciais ou informações pessoais desnecessárias no pacote final. Ocorrências descritivas de termos como tokens, cache ou secreted não são credenciais.

Permanecem caminhos absolutos de **instalação de software** sob `C:\Program Files` e `C:\Program Files (x86)`, necessários aos scripts Windows/CUDA/MSVC. Eles não contêm nome de usuário. `127.0.0.1:8090` é a API local prevista no protocolo, sem autenticação embutida. Não foram encontrados endpoints privados de terceiros.

## Dados grandes e licenças

Os 158 arquivos de `results/` foram classificados individualmente. Dez DB completos, entre 2,08 e 2,19 MB cada, e dez logs completos de servidor, cerca de 11,1 MB cada, foram separados como B, candidatos a Zenodo após revisão e sanitização. O Arrow test de 8.724.720 bytes contém questões de terceiros e fica fora do pacote. `docs/large_files.csv` registra tamanho, função, necessidade, reconstrução, conteúdo externo, hash quando disponível e destino recomendado para cada recurso grande avaliado.

Os dez bancos foram abertos somente com SQLite `mode=ro`: cada um tem a tabela `unnamed`, colunas chave/valor e 12.032 strings de resposta serializadas. Seus hashes coincidem com a auditoria histórica; não contêm isoladamente o gabarito nem o question_id. A inspeção está em `docs/sqlite_inspection.json`. Não se executou novamente a recuperação a partir de Arrow/DB.

Os JSONL dos pilotos, o corpus WikiText e caches de dataset contêm texto de terceiros e foram excluídos. O CSV recuperado de 12,5 MB foi incluído por solicitação expressa: registra saídas curtas e campos derivados, sem enunciados/alternativas integrais. As notas de licença distinguem esses derivados, resultados próprios, software e modelos. Há divergência entre os identificadores de licença do cabeçalho e do corpo do cartão WikiText; ela foi registrada, sem atribuir uma licença por suposição. A indicação MIT do cartão MMLU-Pro foi conferida no cache da revisão histórica. Nenhuma licença global ou DOI foi inventado.

## Verificação final e limites

- Os nove scripts experimentais citados no Apêndice A estão presentes, além do script de recuperação. O conversor pertence ao checkout externo de llama.cpp, cuja revisão foi identificada.
- A metodologia e as seis tabelas/seis figuras possuem correspondência explícita em `docs/TCC_ARTIFACT_MAP.md`.
- Foram conferidos hashes, cinco amostras por teste/configuração, métricas brutas/processadas, normalizações, repetições Q2_K, 120.320 respostas recuperadas, dez contagens e oito linhas de transições.
- A verificação por questão reaplica apenas o extrator às respostas já existentes; não solicita respostas novas nem altera os CSVs.
- Os scripts Python foram analisados sintaticamente sem importação/execução; scripts e comandos PowerShell foram analisados pelo parser sem executar os comandos.
- Links locais Markdown, arquivos referenciados nos agregados e tarefa/função MMLU-Pro foram conferidos. Não há dependência operacional de pasta de redação ou raiz pessoal.
- `docs/package_checksums.csv` cobre todos os arquivos públicos, exceto a si mesmo. O verificador público confere seus hashes sem gravar arquivos.

O relatório de validação desta preparação está em `docs/package_validation.json`. Não se alegou execução ponta a ponta do pipeline. Ela exigiria executar experimentos, expressamente fora do escopo. A reconstrução estrita continua limitada pelo PyTorch permitido por intervalo no requirements, ausência do wheel/transitivos completos e controles de hardware não registrados. A data fixa de 16/10/2026 no relatório produzido pelo algoritmo de auditoria é histórica; não é timestamp de uma futura reprodução.

## Prontidão

**Pronto para um futuro `git init`: sim, como pacote público de código e evidências selecionadas.** Nenhum comando de criação/versionamento/publicação foi executado nesta etapa. Não há caminho pessoal ou pasta temporária pendente de ajuste nos scripts ativos. Os caminhos de instalação CUDA/MSVC dependem da máquina de reprodução e estão documentados.

Antes de anunciar reprodução histórica integral desde os caches, disponibilizar o suplemento DB/logs ou declarar explicitamente sua ausência. Antes de oferecer permissões amplas de reutilização, o autor deve escolher a licença do código próprio. URL do repositório, release e eventual DOI poderão ser acrescentados quando existirem; o CITATION.cff é preliminar. Essas decisões não foram antecipadas pelo pacote.
